from app.domain import Finding
def sequence_findings(events):
 f=[]; kinds=[x.kind for x in events]
 secret=any(x.kind=="credential" or ".env" in (x.resource or "").lower() for x in events)
 outbound=any(x.kind=="network" and x.action.lower() in {"post","upload","send"} for x in events)
 untrusted=any(x.trust=="UNTRUSTED" for x in events)
 if secret and outbound: f.append(Finding(rule="SECRET_TO_NETWORK_SEQUENCE",severity=65,message="Secret access followed by outbound write",event_seq=events[-1].seq))
 if untrusted and secret and outbound: f.append(Finding(rule="INJECTION_EXFIL_CHAIN",severity=85,message="Untrusted input -> secret access -> outbound network causal pattern",event_seq=events[-1].seq))
 return f
