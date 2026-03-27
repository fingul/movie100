"""결과를 CSV/XLSX 파일로 내보내기"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from loguru import logger

from movie100.scraper import Movie


def make_filename(year: int, count: int, ext: str) -> str:
    """파일명 생성: YYYYMMDD_HHMMSS.년도.카운트.ext"""
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{now}.{year}.{count}.{ext}"


def export_csv(movies: list[Movie], year: int, count: int, output_dir: Path) -> Path:
    """CSV 파일로 내보냅니다."""
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / make_filename(year, count, "csv")

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["순위", "제목", "원제", "년도", "평점", "투표수", "WR", "줄거리"])
        for m in movies:
            writer.writerow([m.rank, m.title, m.original_title, m.year, m.rating, m.votes, m.weighted_rating, m.overview])

    logger.info(f"CSV 저장: {filepath}")
    return filepath


def export_xlsx(movies: list[Movie], year: int, count: int, output_dir: Path) -> Path:
    """XLSX 파일로 내보냅니다."""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font
    except ImportError:
        raise ImportError("XLSX 내보내기에는 openpyxl이 필요합니다: uv add openpyxl")

    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / make_filename(year, count, "xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = f"{year}년 Top {count}"

    headers = ["순위", "제목", "원제", "년도", "평점", "투표수", "WR", "줄거리"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for m in movies:
        ws.append([m.rank, m.title, m.original_title, m.year, m.rating, m.votes, m.weighted_rating, m.overview])

    # 열 너비 조정
    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 35
    ws.column_dimensions["D"].width = 6
    ws.column_dimensions["E"].width = 6
    ws.column_dimensions["F"].width = 10
    ws.column_dimensions["G"].width = 6
    ws.column_dimensions["H"].width = 60

    wb.save(filepath)
    logger.info(f"XLSX 저장: {filepath}")
    return filepath
