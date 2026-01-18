from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .database import Base, engine, get_db
from .schemas import VoziloCreate, VoziloUpdate, VoziloOut
from . import crud

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Garaza v3 API")

@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/vozila", response_model=list[VoziloOut])
def sva_vozila(db: Session = Depends(get_db)):
    return crud.list_vozila(db)

@app.post("/vozila", response_model=VoziloOut, status_code=201)
def dodaj_vozilo(payload: VoziloCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_vozilo(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Tablice već postoje.")

@app.get("/vozila/search", response_model=list[VoziloOut])
def pretraga(marka: str | None = None, tablice: str | None = None, db: Session = Depends(get_db)):
    return crud.search_vozila(db, marka=marka, tablice=tablice)

@app.get("/vozila/{vozilo_id}", response_model=VoziloOut)
def jedno_vozilo(vozilo_id: int, db: Session = Depends(get_db)):
    obj = crud.get_vozilo(db, vozilo_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Vozilo nije pronađeno.")
    return obj

@app.put("/vozila/{vozilo_id}", response_model=VoziloOut)
def izmeni_vozilo(vozilo_id: int, payload: VoziloUpdate, db: Session = Depends(get_db)):
    try:
        obj = crud.update_vozilo(db, vozilo_id, payload)
        if not obj:
            raise HTTPException(status_code=404, detail="Vozilo nije pronađeno.")
        return obj
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Tablice već postoje.")

@app.delete("/vozila/{vozilo_id}")
def obrisi_vozilo(vozilo_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_vozilo(db, vozilo_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Vozilo nije pronađeno.")
    return {"deleted": True}
@app.get("/vozila/search", response_model=list[VoziloOut])
def pretraga(
    tip: str | None = None,
    marka: str | None = None,
    tablice: str | None = None,
    db: Session = Depends(get_db),
):
    return crud.search_vozila(db, tip=tip, marka=marka, tablice=tablice)

