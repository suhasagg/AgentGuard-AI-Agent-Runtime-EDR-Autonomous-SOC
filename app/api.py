from fastapi import APIRouter,Depends,HTTPException
from app.security import auth
from app.domain import Event
from app.store import append,load,incident
from app.engine import evaluate
from app.flight_recorder import replay
from app.soc import investigate
router=APIRouter(prefix="/v1",dependencies=[Depends(auth)])
@router.post("/events")
async def ingest(e:Event):
 await append(e); events=await load(e.session_id); v=evaluate(events)
 if v.action!="ALLOW": await incident(v)
 return v
@router.get("/sessions/{sid}/replay")
async def get_replay(sid:str):
 es=await load(sid)
 if not es: raise HTTPException(404,"session not found")
 v=evaluate(es); return {"trace":replay(es),"verdict":v,"soc":investigate(v,es)}
