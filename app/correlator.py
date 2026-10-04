from app.config import settings
from app.domain import Verdict
from app.hashutil import h
def correlate(session_id,events,findings):
 unique={ (x.rule,x.event_seq):x for x in findings}; fs=list(unique.values())
 score=min(100,max([x.severity for x in fs],default=0)+min(20,max(0,len(fs)-1)*5))
 if score>=settings.kill_threshold: action="KILL"
 elif score>=settings.quarantine_threshold: action="QUARANTINE"
 elif score>=40: action="BLOCK"
 else: action="ALLOW"
 root=h([{"seq":e.seq,"kind":e.kind,"parents":e.parent_ids,"resource":e.resource} for e in events])
 return Verdict(session_id=session_id,score=score,action=action,findings=fs,causal_root=root)
