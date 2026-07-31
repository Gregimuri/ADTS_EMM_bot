from __future__ import annotations

import logging
import socket
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# Typical local ports of Clash / v2rayN / Hiddify / Outline clients
CANDIDATE_PORTS = (
    10808,
    10809,
    7890,
    7891,
    1080,
    2080,
    1087,
    20170,
    3080,
    1081,
    9050,
    8118,
    51837,
)

CANDIDATE_SCHEMES = ("socks5://", "http://")


def _port_open(host: str, port: int, timeout: float = 0.35) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _telegram_ok(token: str, proxy: str | None, timeout: float = 12.0) -> str | None:
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        with httpx.Client(proxy=proxy, timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.json()
            if data.get("ok"):
                return data["result"].get("username", "?")
    except Exception as exc:
        logger.debug("Telegram check failed proxy=%s: %s", proxy, exc)
    return None


def resolve_telegram_proxy(token: str, configured: str) -> tuple[str | None, str]:
    """
    Returns (proxy_url_or_None, bot_username).
    Tries configured proxy, then direct, then auto-detect local VPN ports.
    """
    tried: list[str] = []

    if configured:
        tried.append(configured)
        username = _telegram_ok(token, configured)
        if username:
            logger.info("Telegram OK via configured proxy %s (@%s)", configured, username)
            return configured, username
        logger.warning("Configured TELEGRAM_PROXY failed: %s", configured)

    username = _telegram_ok(token, None)
    if username:
        logger.info("Telegram OK without proxy (@%s)", username)
        return None, username

    open_ports = [p for p in CANDIDATE_PORTS if _port_open("127.0.0.1", p)]
    logger.info("Open local proxy ports: %s", open_ports or "none")

    for port in open_ports:
        for scheme in CANDIDATE_SCHEMES:
            proxy = f"{scheme}127.0.0.1:{port}"
            if proxy in tried:
                continue
            tried.append(proxy)
            username = _telegram_ok(token, proxy)
            if username:
                logger.info("Telegram OK via auto proxy %s (@%s)", proxy, username)
                return proxy, username

    raise RuntimeError(
        "Не удалось подключиться к api.telegram.org.\n"
        "Прямой доступ заблокирован, а рабочий локальный прокси не найден.\n"
        "Включи клиент VPN (Clash / v2rayN / Hiddify) и убедись, что "
        "SOCKS/HTTP proxy слушает порт (часто 10808 или 7890).\n"
        f"Проверено: {', '.join(tried) if tried else 'direct only'}"
    )


def persist_proxy_to_env(env_path: Path, proxy: str | None) -> None:
    if not proxy or not env_path.exists():
        return
    text = env_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    key = "TELEGRAM_PROXY="
    replaced = False
    new_lines: list[str] = []
    for line in lines:
        if line.startswith(key) or line.startswith("# TELEGRAM_PROXY="):
            if not replaced and line.startswith(key):
                new_lines.append(f"{key}{proxy}")
                replaced = True
            elif line.startswith(key):
                continue
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    if not replaced:
        new_lines.append(f"{key}{proxy}")
    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
