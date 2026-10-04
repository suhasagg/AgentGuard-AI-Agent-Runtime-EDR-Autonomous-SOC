from app.domain import Finding
def detect(events):
 f=[]
 sensitive=[x for x in events if x.classification in {"CONFIDENTIAL","SECRET"} or x.kind=="credential"]
 sinks=[x for x in events if x.kind=="network" and x.action.lower() in {"post","upload","send"}]
 if sensitive and sinks:
  f.append(Finding(rule="DATA_EXFILTRATION",severity=90,message="Sensitive source and external write sink in session",event_seq=sinks[-1].seq))
 return f
