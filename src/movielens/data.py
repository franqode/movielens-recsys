"""Raw MovieLens 1M dataset loader.

Parses the ``::``-separated files in ``data/raw`` into pandas DataFrames.
Paths are resolved relative to the repository root so the loader works from
any working directory.
"""

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "data" / "raw"

RATINGS_COLS = ["user_id", "movie_id", "rating", "timestamp"]
MOVIES_COLS = ["movie_id", "title", "genres"]
USERS_COLS = ["user_id", "gender", "age", "occupation", "zip_code"]

RATINGS_DTYPES = {
    "user_id": "int64",
    "movie_id": "int64",
    "rating": "int64",
    "timestamp": "int64",
}
MOVIES_DTYPES = {
    "movie_id": "int64",
    "title": "string",
    "genres": "string",
}
USERS_DTYPES = {
    "user_id": "int64",
    "gender": "category",
    "age": "int64",
    "occupation": "int64",
    "zip_code": "string",
}


def load_ratings() -> pd.DataFrame:
    return pd.read_csv(
        RAW_DIR / "ratings.dat",
        sep="::",
        header=None,
        names=RATINGS_COLS,
        dtype=RATINGS_DTYPES,
        engine="python",
    )


def load_movies() -> pd.DataFrame:
    return pd.read_csv(
        RAW_DIR / "movies.dat",
        sep="::",
        header=None,
        names=MOVIES_COLS,
        dtype=MOVIES_DTYPES,
        encoding="latin-1",
        engine="python",
    )


def load_users() -> pd.DataFrame:
    return pd.read_csv(
        RAW_DIR / "users.dat",
        sep="::",
        header=None,
        names=USERS_COLS,
        dtype=USERS_DTYPES,
        engine="python",
    )


def load_all() -> dict[str, pd.DataFrame]:
    return {
        "ratings": load_ratings(),
        "movies": load_movies(),
        "users": load_users(),
    }


def extract_release_year(titles: pd.Series) -> pd.Series:
    return titles.str.extract(r"\((\d{4})\)\s*$", expand=False).astype("Int64")


def explode_genres(movies: pd.DataFrame) -> pd.DataFrame:
    return movies.assign(genres=movies["genres"].str.split("|")).explode("genres")
