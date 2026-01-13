from sqlalchemy.orm import Session
from sqlalchemy import select
from .models import VoziloDB
from .schemas import VoziloCreate, VoziloUpdate

def create_vozilo(db: Session, data: VoziloCreate) -> VoziloDB:
    obj = VoziloDB(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_vozila(db: Session) -> list[VoziloDB]:
    return list(db.scalars(select(VoziloDB).order_by(VoziloDB.id.desc())).all())

def get_vozilo(db: Session, vozilo_id: int) -> VoziloDB | None:
    return db.get(VoziloDB, vozilo_id)

def delete_vozilo(db: Session, vozilo_id: int) -> bool:
    obj = get_vozilo(db, vozilo_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

def update_vozilo(db: Session, vozilo_id: int, data: VoziloUpdate) -> VoziloDB | None:
    obj = get_vozilo(db, vozilo_id)
    if not obj:
        return None
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

def search_vozila(db: Session, marka: str | None = None, tablice: str | None = None) -> list[VoziloDB]:
    stmt = select(VoziloDB)
    if marka:
        stmt = stmt.where(VoziloDB.marka.ilike(f"%{marka}%"))
    if tablice:
        stmt = stmt.where(VoziloDB.tablice.ilike(f"%{tablice}%"))
    stmt = stmt.order_by(VoziloDB.id.desc())
    return list(db.scalars(stmt).all())
