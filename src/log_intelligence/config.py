from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class PipelineConfig:
    """
    Central configuration for the log intelligence pipeline.

    The project is local-first by default. Paths can be overridden through
    environment variables, which makes the pipeline easier to adapt later
    without hardcoding values across the codebase.
    """

    db_path: Path = Path(os.getenv("LOG_PIPELINE_DB_PATH", "warehouse/logs.duckdb"))
    raw_dir: Path = Path(os.getenv("LOG_PIPELINE_RAW_DIR", "data/raw"))
    rejected_dir: Path = Path(os.getenv("LOG_PIPELINE_REJECTED_DIR", "data/rejected"))
    processed_dir: Path = Path(os.getenv("LOG_PIPELINE_PROCESSED_DIR", "data/processed"))
    reports_dir: Path = Path(os.getenv("LOG_PIPELINE_REPORTS_DIR", "reports"))

    def ensure_directories(self) -> None:
        """Create required local directories if they do not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.rejected_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)


config = PipelineConfig()