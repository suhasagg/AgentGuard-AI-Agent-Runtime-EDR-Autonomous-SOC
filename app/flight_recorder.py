from app.hashutil import h
def event_record(e):
 d=e.model_dump(); d["event_hash"]=h(d); return d
def replay(events):
 return [{"t":e.ts,"seq":e.seq,"kind":e.kind,"action":e.action,"resource":e.resource,"trust":e.trust,"classification":e.classification} for e in sorted(events,key=lambda x:x.seq)]
