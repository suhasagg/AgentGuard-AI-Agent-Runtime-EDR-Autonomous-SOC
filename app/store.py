from sqlalchemy import select
from app.db import Session
from app.models import TraceEvent,Incident
from app.domain import Event
from app.flight_recorder import event_record
async def append(e):
 r=event_record(e)
 async with Session.begin() as s:
  s.add(TraceEvent(session_id=e.session_id,agent_id=e.agent_id,seq=e.seq,ts=e.ts,kind=e.kind,payload=e.model_dump(),event_hash=r["event_hash"]))
async def load(session_id):
 async with Session() as s:
  rows=(await s.execute(select(TraceEvent).where(TraceEvent.session_id==session_id).order_by(TraceEvent.seq))).scalars().all()
  return [Event.model_validate(x.payload) for x in rows]
async def incident(v):
 async with Session.begin() as s: s.add(Incident(session_id=v.session_id,score=v.score,action=v.action,findings=[x.model_dump() for x in v.findings],root=v.causal_root))
