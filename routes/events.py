from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from models.events import Event, EventUpdate
from database.connection import get_db
from typing import List

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=Event)
async def create(event: Event, db=Depends(get_db)):
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.get("/", response_model=List[Event])
async def read_all(db=Depends(get_db)):
    return db.exec(select(Event)).all()

@router.get("/{event_id}", response_model=Event)
async def read_one(event_id: int, db=Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(404, "Event not found")
    return event

@router.put("/{event_id}", response_model=Event)
async def update(event_id: int, updated: EventUpdate, db=Depends(get_db)):  # Изменено на EventUpdate
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(404, "Event not found")
    event_data = updated.dict(exclude_unset=True)  # Только изменённые поля
    for key, value in event_data.items():
        setattr(event, key, value)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.delete("/{event_id}")
async def delete(event_id: int, db=Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(404, "Event not found")
    db.delete(event)
    db.commit()
    return {"message": "Event deleted"}
'''
from fastapi import APIRouter, Path, HTTPException, status
from models.events import Event
from typing import List

router = APIRouter(prefix="/events", tags=["events"])

events_db: list[dict] = []

@router.post("/", response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event(event: Event, owner_id: int):
    event_dict = event.dict()
    event_dict["id"] = len(events_db) + 1
    event_dict["owner_id"] = owner_id
    events_db.append(event_dict)

    # Связь с пользователем
    from routes.users import users_db
    for user in users_db:
        if user["id"] == owner_id:
            user["events"].append(event_dict)
            break

    return event_dict

@router.get("/", response_model=List[Event])
async def get_events():
    return events_db

@router.get("/{event_id}", response_model=Event)
async def get_event(event_id: int = Path(..., title="ID of the event")):
    for event in events_db:
        if event["id"] == event_id:
            return event
    raise HTTPException(status_code=404, detail="Event not found")

# ИСПРАВЛЕНО: updated_event ПЕРЕД event_id
@router.put("/{event_id}", response_model=Event)
async def update_event(updated_event: Event, event_id: int = Path(..., title="The ID of the event to update")):
    for i, event in enumerate(events_db):
        if event["id"] == event_id:
            updated = updated_event.dict()
            updated["id"] = event_id
            updated["owner_id"] = event["owner_id"]
            events_db[i] = updated

            from routes.users import users_db
            for user in users_db:
                for j, e in enumerate(user["events"]):
                    if e["id"] == event_id:
                        user["events"][j] = updated
            return updated
    raise HTTPException(status_code=404, detail="Event not found")

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: int = Path(...)):
    for i, event in enumerate(events_db):
        if event["id"] == event_id:
            del events_db[i]
            from routes.users import users_db
            for user in users_db:
                user["events"] = [e for e in user["events"] if e["id"] != event_id]
            return
    raise HTTPException(status_code=404, detail="Event not found")
    '''