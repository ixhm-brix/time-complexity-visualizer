"""SQLite storage for saved analyses, via the SQLAlchemy ORM."""
import os
from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analyses.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    algo: Mapped[str] = mapped_column(String(64), index=True)
    step: Mapped[int] = mapped_column(Integer)
    n_min: Mapped[int] = mapped_column(Integer)
    n_max: Mapped[int] = mapped_column(Integer)
    input_sizes: Mapped[list[int]] = mapped_column(JSON)
    times: Mapped[list[float]] = mapped_column(JSON)
    snapshot_path: Mapped[str] = mapped_column(String(512))
    image_base64: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "algo": self.algo,
            "step": self.step,
            "n_min": self.n_min,
            "n_max": self.n_max,
            "input_sizes": self.input_sizes,
            "times": self.times,
            "snapshot_path": self.snapshot_path,
            "image_base64": self.image_base64,
            "created_at": self.created_at.isoformat(),
        }


def init_db():
    Base.metadata.create_all(engine)
