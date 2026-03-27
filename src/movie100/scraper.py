"""TMDB API를 사용하여 년도별 인기 영화 Top 100을 조회"""

from __future__ import annotations

from dataclasses import dataclass

import httpx
from loguru import logger

from movie100.config import get_api_key

TMDB_BASE_URL = "https://api.themoviedb.org/3"


@dataclass
class Movie:
    rank: int
    title: str
    original_title: str
    year: str
    rating: float
    votes: int
    overview: str
    weighted_rating: float = 0.0


def fetch_movies(year: int, count: int = 100, api_key: str = "") -> list[Movie]:
    """주어진 년도의 인기 영화 목록을 TMDB에서 가져옵니다."""
    key = get_api_key(api_key)
    if not key:
        raise ValueError(
            "TMDB API 키가 필요합니다.\n"
            "  설정: movie100 config --api-key YOUR_KEY\n"
            "  또는 환경변수: export TMDB_API_KEY='your_key'\n"
            "  API 키 발급: https://www.themoviedb.org/settings/api"
        )

    # 충분한 후보를 가져온 뒤 weighted rating으로 재정렬
    fetch_count = max(count * 2, 500)
    pages_needed = (fetch_count + 19) // 20
    raw_movies: list[Movie] = []

    logger.info(f"{year}년 영화 목록을 가져오는 중... (후보 {fetch_count}개, {pages_needed}페이지)")

    with httpx.Client(timeout=30) as client:
        for page in range(1, pages_needed + 1):
            params = {
                "api_key": key,
                "language": "ko-KR",
                "sort_by": "vote_count.desc",
                "primary_release_year": year,
                "page": page,
                "vote_count.gte": 50,
            }
            logger.debug(f"페이지 {page}/{pages_needed} 요청 중...")
            resp = client.get(f"{TMDB_BASE_URL}/discover/movie", params=params)
            resp.raise_for_status()
            data = resp.json()

            results = data.get("results", [])
            if not results:
                logger.debug(f"페이지 {page}에 결과 없음, 중단")
                break

            for item in results:
                release_date = item.get("release_date", "")
                raw_movies.append(
                    Movie(
                        rank=0,
                        title=item.get("title", ""),
                        original_title=item.get("original_title", ""),
                        year=release_date[:4] if release_date else "-",
                        rating=round(item.get("vote_average", 0), 1),
                        votes=item.get("vote_count", 0),
                        overview=item.get("overview", ""),
                    )
                )

            if len(raw_movies) >= fetch_count:
                break

    # IMDB Weighted Rating (베이지안 평균)
    if raw_movies:
        raw_movies = _apply_weighted_rating(raw_movies)

    # 상위 count개만 반환
    movies = raw_movies[:count]
    for i, m in enumerate(movies, 1):
        m.rank = i

    logger.info(f"{len(movies)}개 영화를 찾았습니다.")
    return movies


def _apply_weighted_rating(movies: list[Movie]) -> list[Movie]:
    """IMDB Weighted Rating 공식으로 점수를 계산하고 재정렬합니다.

    WR = (v / (v + m)) * R + (m / (v + m)) * C
    - R: 영화 평점, v: 투표수
    - m: 최소 투표수 기준 (투표수 중앙값)
    - C: 전체 평균 평점
    """
    import statistics

    votes_list = [m.votes for m in movies]
    m = statistics.median(votes_list)
    c = statistics.mean([m_.rating for m_ in movies])

    logger.debug(f"WR 파라미터: m(최소투표기준)={m:.0f}, C(평균평점)={c:.2f}")

    for movie in movies:
        v = movie.votes
        r = movie.rating
        movie.weighted_rating = round((v / (v + m)) * r + (m / (v + m)) * c, 2)

    movies.sort(key=lambda x: x.weighted_rating, reverse=True)
    return movies
