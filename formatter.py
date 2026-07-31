from __future__ import annotations

from collections import OrderedDict

from sheets import PlayerRow

TELEGRAM_LIMIT = 4000


def _clean(value: str) -> str:
    text = (value or "").strip()
    if not text or text.lower() == "none" or text == "-":
        return ""
    return text


def _common_prefix(names: list[str]) -> str:
    if not names:
        return ""
    if len(names) == 1:
        # For a single device keep the full name in the equipment line.
        return ""
    prefix = names[0]
    for name in names[1:]:
        while prefix and not name.startswith(prefix):
            prefix = prefix[:-1]
        if not prefix:
            break
    # cut on last space so we don't keep a broken word
    if prefix and not prefix.endswith(" "):
        cut = prefix.rfind(" ")
        if cut > 0:
            prefix = prefix[: cut + 1]
    # Avoid TT title eating shared device type ("... ДП " → remainders "1","2")
    while prefix:
        remainders = [name[len(prefix) :].strip(" -") for name in names]
        if remainders and all(r and not r.isdigit() for r in remainders):
            break
        trimmed = prefix.rstrip()
        cut = trimmed.rfind(" ")
        prefix = trimmed[: cut + 1] if cut >= 0 else ""
    return prefix


def _device_label(name: str, tt_prefix: str) -> str:
    if tt_prefix and name.startswith(tt_prefix):
        label = name[len(tt_prefix) :].strip(" -")
        return label or name
    return name


def _version_label(old_version: str) -> str:
    value = _clean(old_version).casefold()
    if not value or value in {"нет", "no", "false", "0"}:
        return "Новая"
    if value in {"да", "yes", "true", "1"}:
        return "Старая"
    return _clean(old_version)


def _format_emm_line(row: PlayerRow) -> str:
    emm = _clean(row.emm)
    reflash = _clean(row.reflash)
    if emm and reflash:
        if emm.casefold().startswith("емм"):
            return f"{emm} - {reflash}"
        return f"ЕММ {emm} - {reflash}"
    if emm:
        if emm.casefold().startswith("емм"):
            return emm
        return f"ЕММ {emm}"
    if reflash:
        return reflash
    return ""


def _capitalize(text: str) -> str:
    if not text:
        return text
    return text[:1].upper() + text[1:]


def _format_device(row: PlayerRow, tt_prefix: str) -> str:
    label = _device_label(row.name, tt_prefix)
    do_nothing = _clean(row.do_nothing)

    # «Ничего не делать» → короткий блок с ❌
    if do_nothing:
        return f"🛠 {label} ❌\n{_capitalize(do_nothing)}"

    lines = [f"🛠 {label} ✅"]

    player_id = _clean(row.player_id)
    model = _clean(row.model)
    id_parts: list[str] = []
    if player_id:
        id_parts.append(f"PlayerId: {player_id}")
    if model:
        id_parts.append(f"Модель: {model}")
    if id_parts:
        lines.append(" - ".join(id_parts))

    emm_line = _format_emm_line(row)
    if emm_line:
        lines.append(emm_line)

    adb = _clean(row.adb)
    if adb:
        lines.append(f"Подключение по adb: {adb}")

    update_cube = _clean(row.update_cube)
    if update_cube:
        lines.append(f"Обновить Кубик: {update_cube}")

    lines.append(f"Версия: {_version_label(row.old_version)}")

    edtech = _clean(row.edtech) or "нет"
    lines.append(f"Эдтех: {edtech}")

    mac = _clean(row.mac)
    if mac:
        lines.append(f"network.macAddress: {mac}")

    return "\n".join(lines)


def format_tt_block(rows: list[PlayerRow]) -> str:
    names = [r.name for r in rows]
    tt_prefix = _common_prefix(names)
    tt_title = tt_prefix.strip() or (rows[0].name if rows else "ТТ")
    address = _clean(rows[0].address) if rows else ""
    header = f"🏪 {tt_title}"
    if address:
        header = f"{header}, {address}"

    device_blocks = [_format_device(row, tt_prefix) for row in rows]
    return f"{header}\n\nОборудование:\n\n" + "\n\n".join(device_blocks)


def group_by_tt(rows: list[PlayerRow]) -> list[list[PlayerRow]]:
    groups: OrderedDict[str, list[PlayerRow]] = OrderedDict()
    for row in rows:
        key = row.object_number or f"{row.address}|{row.name}"
        groups.setdefault(key, []).append(row)
    return list(groups.values())


def format_search_result(rows: list[PlayerRow]) -> list[str]:
    if not rows:
        return []
    blocks = [format_tt_block(group) for group in group_by_tt(rows)]
    text = "\n\n".join(blocks)
    return split_message(text)


def split_message(text: str, limit: int = TELEGRAM_LIMIT) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts: list[str] = []
    current: list[str] = []
    size = 0
    for line in text.split("\n"):
        add = len(line) + (1 if current else 0)
        if current and size + add > limit:
            parts.append("\n".join(current))
            current = [line]
            size = len(line)
        else:
            current.append(line)
            size += add
    if current:
        parts.append("\n".join(current))
    return parts
