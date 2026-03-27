"""CLI 엔트리포인트"""

from __future__ import annotations

import sys

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table

from pathlib import Path

from movie100.config import CONFIG_FILE, load_config, save_config
from movie100.exporter import export_csv, export_xlsx
from movie100.scraper import fetch_movies

app = typer.Typer(
    name="movie100",
    help="각 년도별 Best 100 영화를 조회합니다.",
    no_args_is_help=True,
)
config_app = typer.Typer(help="설정 관리")
app.add_typer(config_app, name="config")
console = Console()

# loguru 기본 설정: stderr, WARNING 레벨
logger.remove()
logger.add(sys.stderr, level="WARNING")


@app.command()
def search(
    year: list[int] = typer.Argument(..., help="조회할 년도 (여러 개 가능, 예: 2024 2025)"),
    count: int = typer.Option(100, "--count", "-n", help="조회할 영화 수 (기본: 100, 최대: 250)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="상세 로그 출력"),
    api_key: str = typer.Option("", "--api-key", "-k", help="TMDB API 키"),
    csv: bool = typer.Option(True, "--csv/--no-csv", help="CSV 파일 저장 (기본: 활성화)"),
    xlsx: bool = typer.Option(False, "--xlsx/--no-xlsx", help="XLSX 파일 저장"),
    output_dir: Path = typer.Option("./output", "--output-dir", "-o", help="출력 디렉토리"),
) -> None:
    """특정 년도의 인기 영화 Top N을 조회합니다."""
    if verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    if count < 1 or count > 250:
        console.print("[red]조회 수는 1~250 사이여야 합니다.[/red]")
        raise typer.Exit(1)

    for y in year:
        if y < 1900 or y > 2030:
            console.print(f"[red]잘못된 년도입니다: {y}[/red]")
            raise typer.Exit(1)

        try:
            movies = fetch_movies(y, count, api_key)
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            logger.error(f"영화 목록 조회 실패: {e}")
            console.print(f"[red]오류: {e}[/red]")
            raise typer.Exit(1)

        if not movies:
            console.print(f"[yellow]{y}년 영화를 찾을 수 없습니다.[/yellow]")
            continue

        # 테이블 출력
        table = Table(
            title=f"🎬 {y}년 인기 영화 Top {len(movies)}",
            show_lines=False,
        )
        table.add_column("순위", justify="right", style="cyan", width=4)
        table.add_column("제목", style="bold white", max_width=40)
        table.add_column("원제", style="dim", max_width=30)
        table.add_column("평점", justify="center", style="yellow", width=5)
        table.add_column("투표수", justify="right", style="magenta", width=8)
        table.add_column("WR", justify="center", style="green", width=5)

        for movie in movies:
            table.add_row(
                str(movie.rank),
                movie.title,
                movie.original_title if movie.original_title != movie.title else "",
                str(movie.rating),
                f"{movie.votes:,}",
                str(movie.weighted_rating),
            )

        console.print(table)

        # 파일 내보내기
        if csv:
            path = export_csv(movies, y, len(movies), output_dir)
            console.print(f"[green]CSV 저장: {path}[/green]")
        if xlsx:
            path = export_xlsx(movies, y, len(movies), output_dir)
            console.print(f"[green]XLSX 저장: {path}[/green]")

        console.print()


@config_app.command("set")
def config_set(
    api_key: str = typer.Option("", "--api-key", "-k", help="TMDB API 키 설정"),
) -> None:
    """설정 값을 저장합니다."""
    cfg = load_config()
    if api_key:
        cfg["api_key"] = api_key
        save_config(cfg)
        console.print(f"[green]API 키가 저장되었습니다: {CONFIG_FILE}[/green]")
    else:
        console.print("[yellow]설정할 값을 지정해주세요. (예: --api-key YOUR_KEY)[/yellow]")


@config_app.command("show")
def config_show() -> None:
    """현재 설정을 표시합니다."""
    cfg = load_config()
    key = cfg.get("api_key", "")
    masked = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else ("(미설정)" if not key else "****")
    console.print(f"설정 파일: {CONFIG_FILE}")
    console.print(f"API 키: {masked}")


if __name__ == "__main__":
    app()
