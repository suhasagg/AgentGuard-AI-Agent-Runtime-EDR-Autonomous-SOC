import json,sys
from pathlib import Path
from app.domain import Event
from app.engine import evaluate
from app.flight_recorder import replay
p=Path(sys.argv[1]); es=[Event.model_validate(json.loads(x)) for x in p.read_text().splitlines()]
for x in replay(es): print(f"T+{x['t']:05.2f} {x['kind']:12} {x['action']:10} {x['resource']}")
print(evaluate(es()).model_dump_json(indent=2))
