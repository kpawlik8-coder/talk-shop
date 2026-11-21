"""Create the SQLite database and prepare its tables."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from talk_shop.models.product import DatabaseModel


def prepare_db() -> Engine:
    """Create the database directory and any missing tables."""
    project_dir = Path(__file__).resolve().parents[3]
    database_dir = project_dir / "local"
    database_dir.mkdir(parents=True, exist_ok=True)

    database_path = database_dir / "shop.db"
    engine = create_engine(f"sqlite:///{database_path}")

    DatabaseModel.metadata.create_all(engine)
    return engine
