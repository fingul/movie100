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
uv run movie100 config set --api-key YOUR_KEY
```

## Commands

```bash
uv sync                                          # 의존성 설치
uv run movie100 search 2024                      # 2024년 인기 영화 Top 100
uv run movie100 search 2020 2021 2022            # 여러 년도 동시 조회
uv run movie100 search 2024 -n 20                # 상위 20개만
uv run movie100 search 2024 -v                   # 상세 로그 포함
uv run movie100 search 2024 --xlsx               # XLSX 저장
uv run movie100 config set --api-key YOUR_KEY    # API 키 설정
uv run movie100 config show                      # 설정 확인
uv run pytest                                     # 테스트
uv run ruff check .                               # 린트
uv run ruff format .                              # 포맷
```

## Architecture

- `src/movie100/cli.py` — typer CLI 엔트리포인트, 테이블 출력
- `src/movie100/scraper.py` — TMDB discover API 호출, WR 계산 및 정렬
- `src/movie100/config.py` — 설정 파일 관리 (`~/.config/movie100/config.json`)
- `src/movie100/exporter.py` — CSV/XLSX 내보내기

## Ranking Logic

1. 요청 수의 2배 또는 최소 500개를 투표수 순으로 후보 수집
2. 전체 후보에 대해 IMDB Weighted Rating(베이지안 평균) 계산
3. WR 기준 내림차순 재정렬 후 상위 N개 반환

## Conventions

- 한국어 CLI 출력 (TMDB API도 `ko-KR` 로케일)
- `loguru.logger` 사용 (stdlib logging 사용 금지)
- 기본 로그 레벨 WARNING, `-v` 플래그로 DEBUG
- 설정 파일 권한 0o600 (API 키 보호)
- 출력 파일명: `년도.카운트.YYYYMMDD_HHMMSS.ext`
