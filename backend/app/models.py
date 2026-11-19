from sqlalchemy import CheckConstraint, ForeignKey, String, false
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


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


class MoviePrerequisite(Base):
    __tablename__ = "movie_prerequisites"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), primary_key=True)
    prerequisite_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), primary_key=True)


class Cinema(Base):
    __tablename__ = "cinemas"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    bundles: Mapped[list["CinemaBundleSize"]] = relationship(order_by="CinemaBundleSize.size")


class CinemaBundleSize(Base):
    __tablename__ = "cinema_bundle_sizes"
    __table_args__ = (CheckConstraint("size BETWEEN 1 AND 500"),)

    cinema_id: Mapped[int] = mapped_column(ForeignKey("cinemas.id"), primary_key=True)
    size: Mapped[int] = mapped_column(primary_key=True)
