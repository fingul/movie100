# movie100

각 년도별 Best 100 영화를 조회하는 CLI. TMDB API + IMDB Weighted Rating 적용.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- [TMDB API 키](https://www.themoviedb.org/settings/api) (무료)

## Install

```bash
git clone https://github.com/fingul/movie100.git
cd movie100
uv sync
```

## TMDB API 키 발급

1. https://www.themoviedb.org 에서 회원가입
2. **Settings → API** (https://www.themoviedb.org/settings/api) 이동
3. **Request an API Key** → **Developer** 선택 → 약관 동의
4. 간단한 폼 작성 (용도: Personal, URL은 아무거나)
5. **API Key (v3 auth)** 값을 복사

## Setup

설정 파일에 저장 (권장):

```bash
uv run movie100 config set --api-key YOUR_API_KEY
```

설정 확인:

```bash
uv run movie100 config show
```

또는 환경변수로 설정:

```bash
export TMDB_API_KEY='YOUR_API_KEY'
```

> API 키 우선순위: `--api-key` 옵션 > `TMDB_API_KEY` 환경변수 > 설정 파일 (`~/.config/movie100/config.json`)

## Usage

```bash
# 2024년 인기 영화 Top 100
uv run movie100 search 2024

# 여러 년도 동시 조회
uv run movie100 search 2020 2021 2022 2023 2024 2025

# 상위 20개만
uv run movie100 search 2024 -n 20

# XLSX로도 저장
uv run movie100 search 2024 --xlsx

# CSV 저장 비활성화
uv run movie100 search 2024 --no-csv

# 출력 디렉토리 지정
uv run movie100 search 2024 -o ./results

# 상세 로그
uv run movie100 search 2024 -v
```

### Options

| 옵션 | 단축 | 설명 | 기본값 |
|------|------|------|--------|
| `--count` | `-n` | 조회할 영화 수 (최대 250) | 100 |
| `--csv/--no-csv` | | CSV 저장 | 활성화 |
| `--xlsx/--no-xlsx` | | XLSX 저장 | 비활성화 |
| `--output-dir` | `-o` | 출력 디렉토리 | `./output` |
| `--api-key` | `-k` | TMDB API 키 직접 전달 | |
| `--verbose` | `-v` | 상세 로그 출력 | |

## Ranking Algorithm

IMDB Weighted Rating (Bayesian Average)을 사용합니다:

```
WR = (v / (v + m)) × R + (m / (v + m)) × C
```

- **R**: 영화 평점
- **v**: 투표수
- **m**: 최소 투표수 기준 (후보 영화들의 투표수 중앙값)
- **C**: 전체 평균 평점

투표수가 적은 영화의 극단적 평점을 보정하여, 충분한 투표를 받은 고평점 영화가 상위에 오도록 합니다.

### 수집 과정

1. 요청 수(`-n`)의 2배 또는 최소 500개를 **투표수 순**으로 TMDB에서 후보 수집
2. 전체 후보에 대해 WR 계산
3. WR 기준 내림차순 재정렬 후 상위 N개 반환

후보를 넉넉히 모으는 이유는, 투표수는 적지만 평점이 높은 영화도 WR 상위에 올라올 수 있기 때문입니다.

## Output

기본적으로 `./output/` 디렉토리에 CSV 파일이 저장됩니다.

파일명 형식: `년도.카운트.YYYYMMDD_HHMMSS.csv`

| 컬럼 | 설명 |
|------|------|
| 순위 | WR 기준 순위 |
| 제목 | 한국어 제목 |
| 원제 | 원어 제목 |
| 년도 | 개봉 년도 |
| 평점 | TMDB 평점 |
| 투표수 | TMDB 투표수 |
| WR | Weighted Rating |
| 줄거리 | 한국어 줄거리 |

## License

MIT
