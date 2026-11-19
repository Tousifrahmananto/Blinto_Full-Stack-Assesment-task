from sqlalchemy import CheckConstraint, String, false
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (CheckConstraint("runtime_minutes BETWEEN 1 AND 300"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, unique=True)
    release_year: Mapped[int]
    runtime_minutes: Mapped[int]
    watched: Mapped[bool] = mapped_column(server_default=false())
