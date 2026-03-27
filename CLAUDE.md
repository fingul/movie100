# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

각 년도별 Best 100 영화를 TMDB API로 조회하는 CLI 도구.

## Tech Stack

- **uv** — package/project management
- **typer** — CLI framework
- **loguru** — logging
- **httpx** — HTTP client (TMDB API 호출)
- **rich** — 테이블 출력

## Setup

```bash
# TMDB API 키 필요 (https://www.themoviedb.org/settings/api)
export TMDB_API_KEY='your_key'
```

## Commands

```bash
uv sync                              # 의존성 설치
uv run movie100 2024                  # 2024년 인기 영화 Top 100
uv run movie100 2024 -n 20           # 상위 20개만
uv run movie100 2024 -v              # 상세 로그 포함
uv run movie100 2024 -k YOUR_KEY     # API 키 직접 전달
uv run pytest                         # 테스트
uv run ruff check .                   # 린트
uv run ruff format .                  # 포맷
```

## Architecture

- `src/movie100/cli.py` — typer CLI 엔트리포인트, 테이블 출력
- `src/movie100/scraper.py` — TMDB discover API 호출 및 응답 파싱

## Conventions

- 한국어 CLI 출력 (TMDB API도 `ko-KR` 로케일)
- `loguru.logger` 사용 (stdlib logging 사용 금지)
- 기본 로그 레벨 WARNING, `-v` 플래그로 DEBUG
