import json
from pathlib import Path
from app.domain import Event
from app.engine import evaluate
def es():
 return [Event.model_validate(json.loads(x)) for x in (Path(__file__).parents[1]/"examples/session-84921.jsonl").read_text().splitlines()]
def test_exfil_kills(): assert evaluate(es()).action=="KILL"
def test_dataflow(): assert "DATA_EXFILTRATION" in [x.rule for x in evaluate(es()).findings]
def test_chain(): assert "INJECTION_EXFIL_CHAIN" in [x.rule for x in evaluate(es()).findings]
def test_benign():
 x=[Event(session_id="s",agent_id="a",seq=1,ts=0,kind="file",action="read",resource="README",trust="TRUSTED")]
 assert evaluate(x).action=="ALLOW"
