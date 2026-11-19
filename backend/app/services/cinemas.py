from sqlalchemy import select, text
from sqlalchemy.orm import Session, selectinload

from app.algorithms.min_bundles import minimum_bundles
from app.models import Cinema, CinemaBundleSize
from app.schemas import BookingQuote, BundleQuantity, CinemaCreate, CinemaDetails


class CinemaError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _details(cinema: Cinema) -> CinemaDetails:
    return CinemaDetails(id=cinema.id, name=cinema.name,
                         bundle_sizes=[bundle.size for bundle in cinema.bundles])


def list_cinemas(session: Session):
    query = select(Cinema).options(selectinload(Cinema.bundles)).order_by(Cinema.id)
    return [_details(cinema) for cinema in session.scalars(query)]


def create_cinema(session: Session, payload: CinemaCreate) -> CinemaDetails:
    with session.begin():
        session.execute(text("BEGIN IMMEDIATE"))
        if session.scalar(select(Cinema.id).where(Cinema.name == payload.name)) is not None:
            raise CinemaError("DUPLICATE_CINEMA_NAME", "A cinema already has this name.")
        cinema = Cinema(name=payload.name, bundles=[
            CinemaBundleSize(size=size) for size in sorted(payload.bundle_sizes)
        ])
        session.add(cinema)
        session.flush()
        return _details(cinema)


def booking_quote(session: Session, cinema_id: int, group_size: int) -> BookingQuote:
    cinema = session.get(Cinema, cinema_id)
    if cinema is None:
        raise CinemaError("CINEMA_NOT_FOUND", "Cinema not found.")
    quantities = minimum_bundles([bundle.size for bundle in cinema.bundles], group_size)
    if quantities is None:
        return BookingQuote(possible=False, bundle_count=None, bundles=[])
    return BookingQuote(
        possible=True,
        bundle_count=sum(quantities.values()),
        bundles=[
            BundleQuantity(size=size, quantity=quantities[size])
            for size in sorted(quantities, reverse=True)
        ],
    )
