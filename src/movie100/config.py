"""설정 파일 관리"""

from __future__ import annotations

import json
import os
from pathlib import Path

from loguru import logger

CONFIG_DIR = Path.home() / ".config" / "movie100"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS = {
    "api_key": "",
}


def load_config() -> dict:
    """설정 파일을 읽어옵니다."""
    if not CONFIG_FILE.exists():
        return dict(DEFAULTS)
    try:
        data = json.loads(CONFIG_FILE.read_text())
        logger.debug(f"설정 파일 로드: {CONFIG_FILE}")
        return {**DEFAULTS, **data}
    except Exception as e:
        logger.warning(f"설정 파일 읽기 실패: {e}")
        return dict(DEFAULTS)


def save_config(config: dict) -> None:
    """설정 파일에 저장합니다."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    fd = os.open(CONFIG_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(json.dumps(config, indent=2, ensure_ascii=False))
    logger.debug(f"설정 파일 저장: {CONFIG_FILE}")


def get_api_key(cli_key: str = "") -> str:
    """API 키를 우선순위에 따라 반환합니다: CLI 옵션 > 환경변수 > 설정 파일"""
    if cli_key:
        return cli_key
    env_key = os.environ.get("TMDB_API_KEY", "")
    if env_key:
        return env_key
    return load_config().get("api_key", "")
