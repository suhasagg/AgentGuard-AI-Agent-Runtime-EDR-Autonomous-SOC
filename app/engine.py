from app.sensors import inspect
from app.behavior import sequence_findings
from app.dataflow import detect
from app.correlator import correlate
def evaluate(events):
 findings=[]
 for e in events: findings+=inspect(e)
 findings+=sequence_findings(events); findings+=detect(events)
 return correlate(events[0].session_id,events,findings)
