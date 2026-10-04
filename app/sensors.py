from app.domain import Finding
def inspect(e):
 f=[]; text=(e.action+" "+e.resource+" "+str(e.data)).lower()
 if e.trust=="UNTRUSTED" and any(x in text for x in ["ignore previous","system prompt","override instruction"]):
  f.append(Finding(rule="PROMPT_INJECTION",severity=45,message="Untrusted content contains instruction-override signal",event_seq=e.seq))
 if e.kind=="credential" or any(x in text for x in [".env","aws_access_key","private_key","secret"]):
  f.append(Finding(rule="CREDENTIAL_ACCESS",severity=35,message="Credential/secret access observed",event_seq=e.seq))
 if e.kind=="network" and e.action.lower() in {"post","upload","send"}:
  f.append(Finding(rule="OUTBOUND_WRITE",severity=25,message="Outbound network write observed",event_seq=e.seq))
 return f
