# AgentGuard — AI Agent Runtime EDR + Autonomous SOC

## Why Agent EDR

Traditional authorization answers **may this principal perform this action?** AgentGuard answers a different question:

> **What is the agent actually doing over time, what causal inputs produced the behavior, and has the trajectory become dangerous?**

These systems are complementary:

```text
Zero-Trust Control Plane -> permission
AgentGuard EDR           -> behavior
```

## Architecture

```text
AGENT RUNTIME
 |-- Prompt
 |-- Reasoning metadata
 |-- Memory
 |-- Tool calls
 v
AGENTGUARD SENSOR PLANE
 |-- event sensor
 |-- tool sensor
 |-- file sensor
 |-- network sensor
 |-- credential sensor
 v
BEHAVIOR + DATA-FLOW ANALYTICS
 |-- prompt-injection signals
 |-- credential abuse
 |-- sequence analysis
 |-- sensitive source -> external sink
 v
THREAT CORRELATOR
 v
RISK SCORE
 |-- ALLOW
 |-- BLOCK
 |-- QUARANTINE
 `-- KILL
 v
FLIGHT RECORDER + AUTONOMOUS SOC
 |-- causal reconstruction
 |-- attack classification
 |-- explanation
 `-- remediation proposal (human-reviewed)
```

## Core invariant

A single event is often ambiguous. Security meaning emerges from a sequence:

```text
untrusted repository content
 -> secret read
 -> external POST
```

AgentGuard therefore evaluates **trajectories**, not only isolated prompts.

## Event schema

Each event contains session, agent, monotonic sequence, timestamp, kind, action, resource, data, trust, classification, and causal parents.

## Sensor plane

Sensors normalize agent-native events from prompts, tool requests/results, filesystem, network, credentials, memory and policy decisions.

## Prompt-injection sensor

The runnable detector intentionally uses transparent defensive heuristics. Production should add evaluated classifiers and provenance-aware rules; a regex is not represented as a complete prompt-injection defense.

## Credential sensor

Credential access is a high-signal event. Production sensors should recognize secrets without unnecessarily persisting their raw values.

## Network sensor

Outbound writes are important sinks for exfiltration analysis.

## Behavior engine

The behavior engine recognizes temporal patterns. It can be extended with finite-state rules, CEP, graph queries, statistical baselines and evaluated anomaly models.

## Sequence detection

The included high-value rule recognizes secret access followed by outbound transfer.

## Data-flow engine

Data-flow detection correlates sensitive sources with external sinks. Production systems should track object-level lineage rather than infer flow solely at session level.

## Threat correlator

Findings are deduplicated and converted into a risk score. High-confidence exfiltration can cause KILL; lower-confidence behavior can BLOCK or QUARANTINE.

## Why correlation matters

`read .env` may be legitimate. `POST external endpoint` may be legitimate. Their causal combination after untrusted input can be an incident.

## Response actions

### ALLOW
Continue monitoring.

### BLOCK
Block the current operation but preserve the session.

### QUARANTINE
Isolate the agent: remove network, revoke capabilities, stop new tools, preserve state.

### KILL
Terminate the runtime and revoke credentials for high-confidence critical behavior.

## Agent Flight Recorder

Every execution is reconstructed into a replayable trace:

```text
Session #84921

T+00.00 user requested repository analysis
T+01.21 README opened; source UNTRUSTED
T+04.11 .env read                         WARNING
T+05.02 external HTTP POST                CRITICAL
T+05.03 data-flow violation               CRITICAL
T+05.04 response = KILL
```

The flight recorder is the agent-security equivalent of endpoint telemetry plus causal application context.

## Causal graph

Production graph:

```text
User Task
 -> Retrieved Jira/README
 -> Agent message
 -> Tool request
 -> File read
 -> Secret object
 -> Network request
 -> Policy response
```

Edges encode causality, not merely temporal proximity.

## Hashing

Events receive deterministic hashes. A mature deployment can hash-chain batches and anchor them into append-only/WORM storage.

## Replay

Local replay:

```bash
python tools/replay.py examples/session-84921.jsonl
```

Replay is deterministic over the recorded event stream and current detector version. Production stores detector/policy versions so historical decisions can be reproduced exactly.

## Autonomous SOC Investigator

The SOC layer consumes the verdict plus flight recorder and produces:

```text
classification
root-cause narrative
affected causal chain
recommended remediation
```

The reference deliberately sets `auto_deploy_policy=false`. Security policy changes remain human-reviewed.

## Example SOC conclusion

```text
Untrusted repository content entered the agent context.
The coding agent subsequently accessed credential material.
It then attempted an outbound transfer.
Sensitive source-to-network flow was detected.
The runtime was terminated.
Recommended: revoke credentials, inspect destination logs,
preserve the trace, and review policy before deployment.
```

## Why the SOC agent should not auto-remediate everything

An investigator that can silently change security policy can create a second autonomous security risk. Recommendations should pass through deterministic validation and human approval.

## Prompt telemetry

Preserve only what is necessary, with privacy controls. Consider redaction/tokenization before central storage.

## Reasoning telemetry

Do not assume private chain-of-thought is available or appropriate to store. Record safe agent-native metadata: plan steps, tool intent, approvals, state transitions and externally observable actions.

## Memory telemetry

Track reads/writes, provenance, trust and object IDs rather than indiscriminately logging memory contents.

## Tool telemetry

Record tool identity, operation, arguments summary/hash, result classification, duration, policy decision and execution status.

## File telemetry

Record path/resource identity, operation, classification and hashes. Avoid storing secret contents.

## Network telemetry

Record destination, protocol, method, bytes, policy decision and data labels.

## Credential telemetry

Record credential identity/class and use—not secret material.

## Tool poisoning

Correlate newly discovered/changed tool definitions with unusual downstream behavior.

## Memory attack

Detect untrusted memory influencing sensitive actions and sudden changes in persistent agent behavior.

## Exfiltration detection

Production rules combine source labels, destination reputation/policy, transformation lineage, volume and user intent.

## PII

Integrate DLP/classification services and propagate labels through the trace.

## Anomaly detection

Use anomaly scores as evidence, not authority. High-impact response should combine anomaly evidence with deterministic policy or high-confidence signatures.

## Baselines

Useful baselines include tools per task, network destinations, secret access frequency, filesystem scope, command classes and delegation patterns.

## Drift

Behavior drift can be agent/model/version specific. Store deployment metadata to avoid mixing incompatible baselines.

## Sequence analytics

CEP/stream processors can recognize multi-event attack patterns across seconds or hours.

## Graph analytics

A graph representation makes it easier to answer "what caused this?" and "which sessions touched this poisoned object?"

## Session isolation

Quarantine should stop new side effects while preserving forensic state.

## Credential revocation

KILL/QUARANTINE should trigger capability and provider-token revocation where supported.

## Network quarantine

Move the runtime to deny-all egress except incident-control endpoints.

## Sandbox integration

AgentGuard should sit outside the agent process so a compromised agent cannot disable its own sensor/enforcement path.

## Out-of-band monitoring

An independent monitor is stronger than an in-process callback because it remains observable when the application layer misbehaves.

## Policy enforcement point

EDR detection without enforcement is only monitoring. BLOCK/QUARANTINE/KILL must be wired to a gateway, sandbox supervisor, workload orchestrator or equivalent PEP.

## False positives

Use staged response:
low confidence -> observe;
medium -> block operation;
high -> quarantine;
critical/high-confidence -> kill.

## Human approval

Allow security analysts to release quarantine, approve remediation, rotate credentials, or deploy a proposed rule.

## Incident lifecycle

```text
DETECTED -> TRIAGED -> CONTAINED -> INVESTIGATING
 -> REMEDIATION_PROPOSED -> HUMAN_APPROVED
 -> REMEDIATED -> CLOSED
```

## Threat model

Prompt injection, tool poisoning, memory poisoning, credential abuse, secret access, data exfiltration, malicious/compromised agents, confused deputies, unsafe command sequences, policy bypass, sandbox escape signals and telemetry tampering.

## Detection engineering

Rules should have IDs, owners, versions, severity, confidence, ATT&CK-like taxonomy, tests, rollout mode and false-positive history.

## Rule shadow mode

Run new detectors without response actions before enabling quarantine.

## Canary

Enable active response for a small agent cohort first.

## Rollback

Keep known-good rule/model bundles.

## Detector versioning

Every incident stores the detector versions used to derive it.

## Evaluation

Measure:
- detection recall on attack traces;
- benign false-positive rate;
- time to detection;
- time to containment;
- exfiltration bytes before containment;
- causal root accuracy;
- SOC explanation accuracy;
- remediation acceptance rate.

## Golden traces

Maintain replayable benign and malicious traces in CI.

## Adversarial tests

Test split attacks where injection, credential access and exfiltration are separated across subagents or long time windows.

## Multi-agent correlation

Correlate by task/delegation/provenance IDs, not only a single process/session.

## Cross-session attacks

Persistent poisoned memory can bridge sessions; the graph should support cross-session lineage.

## Tenant isolation

All trace, incident, replay and graph queries are tenant scoped in production.

## Privacy

Agent telemetry may contain sensitive business context. Apply minimization, access control, encryption and retention policies.

## Retention

Keep raw/high-detail telemetry for the minimum required period; retain derived security metadata longer where appropriate.

## Immutable evidence

Critical incidents can be exported to append-only storage with hash-chain verification.

## SIEM

Export normalized events/findings/incidents to existing SOC infrastructure.

## OpenTelemetry

OTel is a natural transport for agent-native telemetry. Preserve trace/session IDs and semantic attributes for tool, approval and network events.

## Metrics

Events/sec, detector latency, risk distribution, block/quarantine/kill counts, exfiltration detections, secret access, replay failures, SOC triage time and false positives.

## SLO examples

Illustrative:
```text
event ingestion availability       99.99%
critical detection p95             <250 ms
quarantine propagation p99         <1 s
critical trace completeness        100%
cross-tenant trace violations      0
```

## Streaming architecture

```text
Agent/Sandbox
 -> collectors
 -> Kafka/Redpanda/PubSub
 -> stream detection
 -> graph/trace store
 -> correlator
 -> response orchestrator
 -> SIEM/SOC
```

## Storage architecture

Hot: stream state/Redis.
Durable: PostgreSQL/event store.
Search: OpenSearch/ClickHouse.
Graph: graph DB or relational edge tables.
Archive: object/WORM storage.

## Backpressure

Sensors must not crash agents or silently drop critical security events. Use bounded buffers, priorities and durable spooling.

## Event ordering

Use session sequence numbers plus timestamps. Distributed subagents require logical/causal clocks or parent IDs.

## Exactly-once semantics

Security pipelines generally prefer idempotent event IDs and deduplication over claiming universal exactly-once delivery.

## High availability

Collectors and correlators are horizontally scalable. Response orchestration needs idempotency.

## Multi-region

Keep telemetry in permitted regions and route global incident metadata without violating residency.

## Incident response

1. Quarantine/kill.
2. Revoke credentials.
3. Preserve flight recorder.
4. Block destination/tool.
5. Identify causal source.
6. Search related sessions.
7. Assess exposure.
8. Propose remediation.
9. Human review.
10. Replay traces before restoring.

## Applications

### Coding agents
Detect repository prompt injection -> secret read -> external transfer.

### SRE agents
Detect diagnostic task drifting into destructive production operations.

### Browser agents
Detect untrusted page content driving credential or upload behavior.

### Email agents
Detect malicious message instructions followed by sensitive attachment/data exfiltration.

### Finance agents
Detect unusual beneficiary/amount/tool sequences.

### Customer support
Detect bulk customer-data reads followed by unusual exports.

### Data agents
Detect sensitive dataset access followed by new external destinations.

### Multi-agent systems
Detect malicious influence propagating across agent boundaries.

## API

```text
GET  /health
POST /v1/events
GET  /v1/sessions/{session_id}/replay
```

## Docker run

```bash
unzip agentguard-runtime-edr-autonomous-soc.zip
cd agentguard-runtime-edr-autonomous-soc
cp .env.example .env
docker compose up --build -d
curl http://localhost:8000/health
```

## Send the example trace

```bash
while IFS= read -r line; do
  curl -s -X POST http://localhost:8000/v1/events     -H 'x-api-key: change-me'     -H 'Content-Type: application/json'     -d "$line"
  echo
done < examples/session-84921.jsonl
```

## Retrieve replay + SOC analysis

```bash
curl -s   -H 'x-api-key: change-me'   http://localhost:8000/v1/sessions/session-84921/replay
```

## Offline flight-recorder replay

```bash
python tools/replay.py examples/session-84921.jsonl
```

## Host development

```bash
docker compose up -d postgres
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
# use localhost in DATABASE_URL
uvicorn app.main:app --reload
```

## Tests

```bash
python -m pytest -q
ruff check .
```

## Database inspection

```bash
docker compose exec postgres psql -U postgres -d agentguard
```

```sql
SELECT * FROM trace_events ORDER BY session_id, seq;
SELECT * FROM incidents ORDER BY created_at DESC;
```

## Shutdown

```bash
docker compose down
```

## Kubernetes starter

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/api.yaml
```

## Code map

```text
domain.py          event/finding/verdict contracts
sensors.py         point-event security sensors
behavior.py        temporal sequence detection
dataflow.py        sensitive source -> sink detection
correlator.py      risk + response selection
flight_recorder.py deterministic trace representation
soc.py             root-cause/remediation synthesis
engine.py          detection pipeline
models.py          durable trace/incident records
store.py           event/incident persistence
api.py             ingestion + replay
tools/replay.py    offline flight recorder
```

## `sensors.py`

Point detections intentionally remain simple and explainable. They feed correlation rather than making every response decision independently.

## `behavior.py`

Encodes sequence-level detections such as secret-to-network and untrusted-input-to-secret-to-network.

## `dataflow.py`

Demonstrates source/sink correlation. Production should propagate object-level labels through transformations.

## `correlator.py`

Maps evidence to response. The maximum signal plus corroborating findings drives escalation.

## `flight_recorder.py`

Creates stable event hashes and a replay-friendly ordered representation.

## `soc.py`

Produces bounded defensive investigation output. It does not autonomously deploy policy.

## Production boundary

### Implemented and runnable
Typed event ingestion; prompt-injection signal; credential/network sensors; temporal behavior rules; sensitive-data-flow detection; risk correlation; ALLOW/BLOCK/QUARANTINE/KILL; durable event/incident SQL storage; deterministic flight recorder; replay API/CLI; SOC root-cause/remediation output; Docker; Kubernetes starter; tests.

### Enterprise integrations required
Agent/sandbox kernel sensors; eBPF/OS telemetry; MCP/gateway hooks; real DLP/secret scanners; production injection classifiers; stream bus/CEP; distributed graph store; workload orchestrator quarantine; provider credential revocation; network enforcement; immutable WORM evidence; SIEM/SOAR; OTel collectors; RBAC/SSO; multi-tenant storage controls; Alembic; Helm; HPA/PDB/NetworkPolicy; multi-region DR.

## Why this boundary matters

A Python API cannot honestly claim to be a hardware/out-of-band EDR by itself. The repository implements the control/detection logic and interfaces; production enforcement must be integrated with the infrastructure that actually controls agent processes, credentials and network paths.

## Production roadmap

```text
1 OTel/MCP/sandbox collectors
2 Kafka event backbone
3 object-level data lineage
4 DLP/secret classifiers
5 rule/model registry
6 graph-based correlation
7 sandbox/orchestrator quarantine API
8 credential revocation
9 network enforcement
10 SIEM/SOAR integration
11 immutable evidence
12 RBAC/SSO
13 multi-tenant hardening
14 chaos/load/red-team evaluation
15 multi-region deployment
```

## Principal-level questions

How is Agent EDR different from authorization? What data is safe to log? How do you reconstruct causality without chain-of-thought? How do you correlate across subagents? How do you distinguish temporal correlation from actual data flow? How quickly can quarantine propagate? What if telemetry is delayed? How do you prevent a compromised agent from disabling its monitor? How do you replay an incident under the original detector version? How do you avoid an autonomous SOC becoming a new privileged attack surface?

## References

NVIDIA, **Open Agent Safety Platform** (September 28, 2026). Public material describes OpenShell as a secure runtime boundary tracing/enforcing agent actions and Sentry as an out-of-band watchdog on BlueField-4 that continuously monitors and can quarantine agents attempting to move outside boundaries.

OpenAI, **Running Codex safely at OpenAI** (May 8, 2026). Public material describes managed technical boundaries, sandboxing, network policies, approvals, agent-native OpenTelemetry, compliance logs, and use of an AI-powered security triage agent to contextualize endpoint alerts with agent activity.

## Final principle

```text
AUTHORIZATION asks:
"May the agent do this?"

AGENTGUARD asks:
"What is the agent actually doing,
what caused it,
where is sensitive information flowing,
and should the runtime be contained now?"
```

# Comprehensive Production Architecture Manual

## 1. Executive architecture

AgentGuard is designed as an independent security plane surrounding an autonomous agent runtime. The model is intentionally not trusted to police itself.

```text
                         ENTERPRISE / USER TASK
                                  |
                                  v
+------------------------------------------------------------------+
|                         AGENT RUNTIME                            |
| prompt | plan metadata | memory | tools | files | network       |
+-------------------------------+----------------------------------+
                                |
                         security telemetry
                                |
                                v
+------------------------------------------------------------------+
|                         SENSOR PLANE                             |
| prompt sensor | tool sensor | file sensor | credential sensor    |
| memory sensor | network sensor | policy sensor | sandbox sensor  |
+-------------------------------+----------------------------------+
                                |
                                v
+------------------------------------------------------------------+
|                     NORMALIZATION / ENRICHMENT                   |
| session | agent | tenant | trust | classification | provenance   |
| tool | destination | hashes | causal parents | deployment ver.   |
+-------------------------------+----------------------------------+
                                |
                 +--------------+---------------+
                 |                              |
                 v                              v
+------------------------------+  +--------------------------------+
| BEHAVIOR DETECTION           |  | INFORMATION-FLOW DETECTION     |
| sequences                    |  | source -> transform -> sink     |
| anomalies                    |  | secrets / PII / confidential   |
| tool poisoning               |  | destination / egress policy    |
| credential abuse             |  | lineage / taint propagation    |
+---------------+--------------+  +---------------+----------------+
                +------------------------------+
                                               v
+------------------------------------------------------------------+
|                        THREAT CORRELATOR                         |
| rules + causal graph + confidence + severity + context           |
+-------------------------------+----------------------------------+
                                |
                                v
+------------------------------------------------------------------+
|                         RESPONSE ENGINE                          |
| ALLOW | BLOCK CURRENT ACTION | QUARANTINE | KILL                 |
+-------------------------------+----------------------------------+
                                |
                +---------------+----------------+
                |                                |
                v                                v
+------------------------------+  +--------------------------------+
| AGENT FLIGHT RECORDER        |  | AUTONOMOUS SOC INVESTIGATOR    |
| replayable event trace       |  | reconstruct -> classify        |
| causal/provenance graph      |  | explain -> recommend           |
| detector/policy versions     |  | human-approved remediation     |
+------------------------------+  +--------------------------------+
```

## 2. Security objective

Authorization systems answer whether an action is permitted. AgentGuard detects whether the runtime's observed behavior is becoming unsafe even when individual actions may appear legitimate.

## 3. Trusted computing base

The strongest deployment keeps collectors, response enforcement, credential revocation and immutable evidence outside the agent process.

## 4. Why agent-native EDR

An agent's attack surface includes natural-language inputs, retrieved documents, memory, tools, code execution, browsers, credentials, network destinations and other agents. Endpoint telemetry alone does not explain those causal relationships.

## 5. Event-driven security model

Every observable runtime operation becomes a typed security event.

## 6. Session identity

A session groups activity belonging to one execution/task while preserving links to parent tasks and subagents.

## 7. Agent identity

Every event should identify the workload/agent that emitted or caused it.

## 8. Tenant identity

Production ingestion derives tenant identity from authenticated transport rather than trusting arbitrary event fields.

## 9. Sequence number

A monotonic sequence provides stable replay ordering inside a session.

## 10. Timestamp

Wall-clock time enables cross-system correlation, but ordering must not rely solely on clocks.

## 11. Causal parents

Parent IDs distinguish causality from mere temporal adjacency.

## 12. Trust label

TRUSTED, UNTRUSTED and UNKNOWN indicate provenance trust, not whether content is factually correct.

## 13. Classification

PUBLIC, INTERNAL, CONFIDENTIAL and SECRET labels provide a baseline for data-flow controls.

## 14. Prompt sensor

Records prompt-security signals without assuming that prompt text alone determines compromise.

## 15. Tool sensor

Records tool identity, operation, argument summary/hash, result classification and execution outcome.

## 16. File sensor

Records file/resource identity, read/write/execute operation, classification and content hash where appropriate.

## 17. Network sensor

Records method, destination, bytes, protocol, policy result and labels associated with transmitted data.

## 18. Credential sensor

Records credential class and access/use event. Raw secret values should never be copied into telemetry.

## 19. Memory sensor

Records memory reads/writes, provenance IDs, trust labels and classifications.

## 20. Sandbox sensor

Records process, command, syscall class, filesystem mount, network and resource-limit events when available.

## 21. Policy sensor

Records authorization/approval decisions so behavioral detection can distinguish expected privileged operations from anomalous ones.

## 22. Normalization

Provider-specific events are mapped into a stable security schema before detection.

## 23. Enrichment

Enrichment can add user/task IDs, deployment version, model, tool registry metadata, destination category and data classification.

## 24. Prompt injection

Prompt-injection detection is treated as evidence rather than the entire defense.

## 25. Indirect prompt injection

Retrieved pages, tickets, documents and tool output can introduce instructions that were not supplied by the user.

## 26. Tool poisoning

A tool definition, MCP description or tool response can contain adversarial content that changes later behavior.

## 27. Memory poisoning

Persistent malicious content can bridge tasks and sessions.

## 28. Credential abuse

Unexpected credential access is high-value telemetry even when the read itself is technically permitted.

## 29. Secret access

Secret access becomes more dangerous when followed by network, clipboard, publish, email or tool-output sinks.

## 30. Behavioral sequences

The reference includes sequence rules because dangerous behavior often emerges only across multiple events.

## 31. Secret-to-network sequence

```text
credential/file secret read
          ->
external POST/upload/send
          ->
high-severity finding
```

## 32. Injection-to-exfiltration chain

```text
UNTRUSTED input
    ->
credential access
    ->
outbound write
    ->
critical causal pattern
```

## 33. Data-flow model

A mature implementation tracks sensitive objects through transformations rather than inferring flow from session co-occurrence.

## 34. Sources

Secrets, credentials, confidential files, customer records, retrieved documents, memory and tool responses.

## 35. Transforms

Summarization, parsing, code generation, compression, encryption, serialization and agent-to-agent messages.

## 36. Sinks

HTTP requests, email, public publishing, uploads, external tools, logs and generated artifacts.

## 37. Taint propagation

Derived objects inherit relevant source labels until an explicitly trusted declassification step.

## 38. Declassification

Only trusted policy-controlled components should remove security labels.

## 39. DLP integration

Production systems should integrate proven secret/PII/classification detectors and avoid storing raw sensitive content.

## 40. Behavioral anomaly detection

Useful features include tool mix, destination novelty, secret access frequency, write/read ratio, command class and task duration.

## 41. Baseline scope

Baselines should be segmented by agent type, model version, task family, environment and deployment version.

## 42. Drift

Model/runtime upgrades can change benign behavior; detector baselines must be version-aware.

## 43. Explainable rules

High-impact containment should retain deterministic reason codes.

## 44. ML detectors

ML anomaly scores are evidence. They should not silently become unrestricted policy authority.

## 45. Threat correlation

The correlator combines point findings, sequence findings, data-flow findings, provenance and context.

## 46. Risk score

The reference uses a simple explainable score. Production scoring should be calibrated against attack and benign trace corpora.

## 47. Confidence

Severity and confidence should be distinct fields in a mature detector model.

## 48. ALLOW

No current response action is required; monitoring continues.

## 49. BLOCK

Stop the current operation while keeping the session alive.

## 50. QUARANTINE

Prevent new side effects, revoke capabilities, isolate network and preserve state.

## 51. KILL

Terminate the workload and revoke active credentials/capabilities.

## 52. Response idempotency

Containment commands need idempotency because distributed systems can retry.

## 53. Quarantine propagation

Production response must reach gateway, sandbox, credential broker and network enforcement rapidly.

## 54. Credential revocation

Containment should revoke short-lived capabilities and provider tokens where supported.

## 55. Network containment

Switch the workload to deny-all egress except approved incident-control destinations.

## 56. Process containment

Stop child process creation and terminate dangerous processes through the runtime supervisor.

## 57. Tool containment

Disable selected tools or entire tool classes without necessarily killing the agent.

## 58. Flight recorder objective

Reconstruct what happened, why it happened and which security decision was made.

## 59. Flight recorder record

```text
event ID
session
agent
sequence
timestamp
event type
action/resource
trust
classification
causal parents
event hash
detector versions
policy versions
response
```

## 60. Hash-addressed events

Stable hashes help detect accidental/tampered modifications and provide graph node IDs.

## 61. Hash chaining

Production can hash-chain batches and anchor them into immutable storage.

## 62. Replay semantics

Replay should run the historical event stream against the original detector/policy versions for forensic reproduction.

## 63. Counterfactual replay

A second mode can replay an old incident against a proposed new detector bundle to measure whether it would have been stopped earlier.

## 64. Flight recorder CLI

```bash
python tools/replay.py examples/session-84921.jsonl
```

## 65. Replay output

The CLI prints the ordered trace and resulting verdict.

## 66. Causal graph

Graph edges should encode explicit parent/derived-from relationships where possible.

## 67. Temporal edges

Temporal adjacency is weaker evidence and should be distinguished from causal lineage.

## 68. Cross-agent graph

Messages and delegated tasks create edges between supervisor and subagent sessions.

## 69. Cross-session graph

Persistent memory creates lineage between sessions.

## 70. Root-cause reconstruction

The investigator identifies the earliest relevant untrusted/security event and the chain leading to containment.

## 71. Autonomous SOC role

The SOC agent explains and recommends. It should not have unlimited autonomous remediation privileges.

## 72. SOC input

Use normalized evidence, not unrestricted access to all enterprise data.

## 73. SOC output

Classification, root-cause graph, evidence summary, blast-radius hypotheses, remediation and confidence.

## 74. Human review

Policy deployment and broad remediation should remain subject to approval.

## 75. SOC hallucination control

Every factual claim in an investigation should point to trace evidence.

## 76. Evidence grounding

Use event IDs and graph paths as citations inside incident reports.

## 77. Attack classification

Maintain a versioned taxonomy for prompt injection, tool poisoning, credential access, exfiltration, policy bypass and other classes.

## 78. Remediation proposals

Examples: revoke credentials, quarantine runtime, block destination, disable tool, rotate secret, remove poisoned memory, add rule.

## 79. Proposed policy validation

A proposed rule is tested against golden benign and attack traces before deployment.

## 80. Shadow deployment

Run proposed policies without enforcement to estimate false positives.

## 81. Canary deployment

Enable response for a small workload cohort.

## 82. Rollback

Keep immutable known-good detector and policy bundles.

## 83. Detection-as-code

Store detector rules, metadata, tests and rollout configuration in version control.

## 84. Rule metadata

ID, owner, description, severity, confidence, event requirements, response, version and references.

## 85. Golden traces

CI should replay known benign and malicious sessions.

## 86. Unit tests

Test individual sensors and correlator behavior.

## 87. Sequence tests

Verify split attack chains and event-order edge cases.

## 88. Data-flow tests

Verify sensitive objects cannot reach prohibited sinks.

## 89. False-positive tests

Include realistic benign secret access and network activity.

## 90. Adversarial tests

Attempt to split an attack across tools, agents, sessions and time windows.

## 91. Evasion tests

Test encoding, chunking, delayed exfiltration and intermediate transforms.

## 92. Telemetry tampering

Detect gaps, impossible sequence jumps, invalid signatures and collector outages.

## 93. Collector authentication

Production collectors should use workload identity/mTLS and signed event envelopes.

## 94. Event integrity

Validate schema, identity, monotonicity and signatures before accepting security telemetry.

## 95. Backpressure

Critical security events should receive priority and durable local spooling.

## 96. Event loss

Expose dropped-event counters and mark affected traces incomplete.

## 97. Stream backbone

Kafka/Redpanda/PubSub-style infrastructure is appropriate for high-volume durable ingestion.

## 98. Partitioning

Partition by tenant/session while preserving enough locality for sequence processing.

## 99. Stream processing

CEP/stateful processors maintain short-lived behavioral state.

## 100. Hot cache

Redis can hold bounded detector state, rate limits and session summaries.

## 101. Durable event store

PostgreSQL/event stores preserve incident and control-plane metadata.

## 102. Analytical store

ClickHouse/OpenSearch can support high-volume security hunting.

## 103. Graph store

Graph databases or relational edge tables can support causal traversal.

## 104. Archive

Object/WORM storage preserves compressed evidence under retention policy.

## 105. Tenant isolation

Every store, stream key, cache key and query is tenant scoped.

## 106. Residency

Telemetry routing and backups must honor regional data rules.

## 107. Privacy minimization

Store hashes, classifications and summaries instead of raw prompts/secrets whenever possible.

## 108. Reasoning telemetry boundary

Do not depend on hidden chain-of-thought. Record externally observable plans, tool intent and state transitions.

## 109. Encryption

Encrypt telemetry in transit and at rest.

## 110. Access control

Security analysts receive least-privilege access to traces.

## 111. Break-glass access

Emergency trace access is time-bounded and heavily audited.

## 112. Retention tiers

High-detail raw telemetry can expire earlier than derived incident metadata.

## 113. Immutable audit

Critical response and analyst actions should be append-only/auditable.

## 114. SIEM integration

Export normalized findings and incidents into enterprise SIEM.

## 115. SOAR integration

Remediation workflows can call SOAR after deterministic policy and human approval.

## 116. OpenTelemetry

OTel can transport agent-native spans/events and preserve trace correlation.

## 117. Metrics

Ingestion rate, detector latency, event loss, response latency, finding rate, containment count, false-positive rate and SOC triage latency.

## 118. Detection SLO

Measure time from dangerous event to decision.

## 119. Containment SLO

Measure time from decision to effective enforcement.

## 120. Trace completeness SLO

Critical incidents should have complete required event classes.

## 121. Availability

Security infrastructure should be redundant because loss of monitoring can become a security failure.

## 122. Fail-safe mode

Define whether high-risk agents pause when telemetry or enforcement becomes unavailable.

## 123. Collector outage

Agents with high-risk privileges may need to stop or enter reduced capability mode.

## 124. Correlator outage

Preserve events durably and apply local deterministic safeguards.

## 125. Database outage

Spool telemetry and avoid losing critical containment commands.

## 126. Network partition

Local enforcement should continue using the last known safe policy where appropriate.

## 127. Quarantine service outage

Escalate to sandbox/workload termination if quarantine cannot be guaranteed.

## 128. High availability

Stateless APIs scale horizontally; stateful stream processing uses replicated partitions/checkpoints.

## 129. Multi-region

Run regional collectors/detectors and a privacy-safe global incident coordination layer.

## 130. Disaster recovery

Test event-store restore, rule-bundle restore and incident continuity.

## 131. Capacity planning

Size for peak events/sec, bursty tool loops, replay workloads and security hunting.

## 132. Sampling

Do not sample away critical security events.

## 133. Cost controls

Tier low-risk verbose telemetry while preserving high-value security evidence.

## 134. Coding-agent application

Repository content can inject instructions that cause shell, secret or network behavior.

## 135. SRE-agent application

Detect drift from diagnostics into destructive production activity.

## 136. Browser-agent application

Treat web content as untrusted and detect sensitive form/upload/network flows.

## 137. Email-agent application

Detect email-borne instructions that lead to sensitive forwarding or exports.

## 138. Finance-agent application

Detect unusual beneficiary, amount, credential and transaction sequences.

## 139. Support-agent application

Detect bulk customer access followed by export or unauthorized account operations.

## 140. Analytics-agent application

Detect sensitive warehouse reads followed by external transfer.

## 141. HR-agent application

Detect employee-record access inconsistent with the task and destination.

## 142. Multi-agent application

Track attack propagation across supervisor/subagent boundaries.

## 143. MCP application

Monitor MCP tool discovery, requests, results and destinations.

## 144. Memory-system application

Trace poisoned memory into later actions and identify affected sessions.

## 145. Zero-Trust integration

Authorization decisions become AgentGuard events; AgentGuard behavior can trigger revocation/quarantine.

## 146. Permission Firewall integration

A permitted action can still be blocked by EDR if the broader trajectory indicates compromise.

## 147. Tool Router integration

AgentGuard can detect sudden tool-selection changes or poisoned registry/tool metadata.

## 148. API surface

```text
GET  /health
POST /v1/events
GET  /v1/sessions/{session_id}/replay
```

## 149. Production API evolution

```text
POST /v1/events:batch
POST /v1/incidents/{id}:quarantine
POST /v1/incidents/{id}:kill
POST /v1/incidents/{id}:release
GET  /v1/incidents/{id}
GET  /v1/sessions/{id}/graph
POST /v1/replay
POST /v1/detectors:simulate
POST /v1/detectors:deploy
GET  /metrics
```

## 150. Repository code map

```text
app/config.py          service configuration
app/domain.py          event/finding/verdict contracts
app/db.py              async database setup
app/models.py          trace + incident persistence
app/hashutil.py        canonical event/graph hashing
app/sensors.py         point-event sensors
app/behavior.py        temporal behavior detection
app/dataflow.py        sensitive source/sink detection
app/correlator.py      score + response selection
app/flight_recorder.py replay representation
app/soc.py             bounded SOC investigation
app/engine.py          detection pipeline
app/store.py           durable persistence
app/security.py        local API authentication
app/api.py             ingestion/replay endpoints
app/main.py            FastAPI bootstrap
tools/replay.py        offline flight-recorder CLI
```

## 151. `domain.py`

Typed contracts prevent arbitrary event payloads from silently becoming security decisions.

## 152. `sensors.py`

Point sensors identify prompt-injection signals, credential access and outbound writes.

## 153. `behavior.py`

Temporal correlation detects secret-to-network and injection-to-secret-to-network chains.

## 154. `dataflow.py`

The baseline detector recognizes sensitive-source/external-sink co-occurrence. Production should implement object-level lineage.

## 155. `correlator.py`

Deduplicates findings, computes score and selects ALLOW/BLOCK/QUARANTINE/KILL.

## 156. `flight_recorder.py`

Produces deterministic hashes and ordered replay records.

## 157. `soc.py`

Builds evidence-bounded root-cause and remediation suggestions. It intentionally cannot auto-deploy policy.

## 158. `engine.py`

```text
events
 -> point sensors
 -> behavior sequences
 -> data-flow
 -> correlation
 -> response
```

## 159. `store.py`

Persists telemetry and incidents using transactional SQL operations.

## 160. `security.py`

API-key auth exists for local reference use. Replace with workload identity/mTLS/OIDC in production.

## 161. `main.py`

`create_all` is development convenience. Production uses Alembic migrations.

## 162. Example attack trace

`examples/session-84921.jsonl` demonstrates untrusted repository content, secret access and outbound POST.

## 163. Offline replay

```bash
python tools/replay.py examples/session-84921.jsonl
```

## 164. Docker run

```bash
unzip agentguard-runtime-edr-autonomous-soc-comprehensive.zip
cd agentguard-runtime-edr-autonomous-soc
cp .env.example .env
docker compose up --build -d
docker compose ps
curl http://localhost:8000/health
```

## 165. Send example events

```bash
while IFS= read -r line; do
  curl -s -X POST http://localhost:8000/v1/events \
    -H 'x-api-key: change-me' \
    -H 'Content-Type: application/json' \
    -d "$line"
  echo
done < examples/session-84921.jsonl
```

## 166. Retrieve replay

```bash
curl -s \
  -H 'x-api-key: change-me' \
  http://localhost:8000/v1/sessions/session-84921/replay
```

## 167. Development run

```bash
docker compose up -d postgres
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
# Set DATABASE_URL to localhost.
uvicorn app.main:app --reload
```

## 168. Test suite

```bash
python -m pytest -q
ruff check .
```

## 169. Database inspection

```bash
docker compose exec postgres psql -U postgres -d agentguard
```

```sql
SELECT * FROM trace_events ORDER BY session_id, seq;
SELECT * FROM incidents ORDER BY created_at DESC;
```

## 170. Logs

```bash
docker compose logs -f api
docker compose logs -f postgres
```

## 171. Shutdown

```bash
docker compose down
```

Use `docker compose down -v` only when intentionally deleting local data.

## 172. Kubernetes starter

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/api.yaml
kubectl get pods -n agentguard
```

## 173. Kubernetes production additions

Service, HPA, PDB, topology spread, NetworkPolicy, ServiceAccount/workload identity, managed secrets, probes, resource requests/limits and admission policy.

## 174. Container hardening

Non-root, no privilege escalation, read-only root filesystem, dropped Linux capabilities and seccomp/AppArmor where supported.

## 175. Supply-chain security

Pin dependencies, generate SBOMs, scan/sign images and enforce trusted artifacts.

## 176. Database migrations

Replace automatic schema creation with Alembic.

## 177. Authentication

Replace local API key with mTLS/workload identity and analyst OIDC/SSO.

## 178. Authorization

Add tenant-aware RBAC/ABAC for analysts, responders and detector administrators.

## 179. Streaming

Add Kafka/Redpanda/PubSub collectors and stateful stream processing.

## 180. Real collectors

Integrate MCP gateways, browser runtimes, code sandboxes, container telemetry and OS/eBPF where appropriate.

## 181. Real enforcement

Integrate sandbox supervisor, workload orchestrator, network policy, credential broker and tool gateway.

## 182. Production DLP

Use tested secret/PII/classification services with privacy-preserving telemetry.

## 183. Graph correlation

Implement causal graph traversal across tasks, agents, memory and tools.

## 184. Detector registry

Store rule/model versions, signatures, owners and rollout state.

## 185. Policy deployment

Use signed bundles, shadow mode, canary and rollback.

## 186. Incident management

Persist incident lifecycle, analyst notes, evidence, approvals and remediation state.

## 187. Case management

Integrate tickets/cases with enterprise SOC workflows.

## 188. Immutable evidence

Export critical traces to WORM/append-only storage.

## 189. Security evaluation pipeline

```text
attack corpus
 + benign corpus
 + production-safe sampled traces
 -> replay
 -> detector metrics
 -> regression gates
 -> shadow
 -> canary
 -> production
```

## 190. Performance evaluation

Benchmark ingestion throughput, p50/p95/p99 detector latency, graph traversal and quarantine propagation.

## 191. Load testing

Generate realistic agent event bursts, tool loops and multi-agent fanout.

## 192. Chaos testing

Kill collectors, stream partitions, database nodes, correlators and quarantine services.

## 193. Red-team scenarios

Prompt injection, poisoned MCP tool, poisoned memory, credential theft, chunked exfiltration, delayed exfiltration, multi-agent laundering and telemetry suppression.

## 194. Incident reconstruction scenario

```text
Jira issue #582 (UNTRUSTED)
 -> coding agent context
 -> .env read
 -> AWS credential object
 -> MCP HTTP tool
 -> external destination
 -> data-flow violation
 -> network operation blocked
 -> workload quarantined
```

## 195. SOC output scenario

```text
Root cause:
Indirect prompt injection entered through Jira issue #582.

Propagation:
The instruction influenced the coding agent and caused a credential read.

Attempted impact:
The agent attempted to send secret-bearing data through an HTTP tool.

Containment:
The outbound operation was blocked and the runtime quarantined.

Recommended:
Rotate affected credentials, inspect destination logs,
remove poisoned content/memory, add tested detection policy,
and replay related sessions.
```

## 196. Principal design questions

What is the TCB? How do you observe behavior without chain-of-thought? How do you prove causal flow rather than temporal correlation? Can a compromised agent disable sensors? What happens when telemetry is delayed? How do you quarantine within one second? How do you revoke credentials? How do you correlate across agents/sessions? How do you replay the original detector version? How do you prevent the SOC agent from becoming a privileged attacker?

## 197. Relationship to classic EDR

Classic EDR sees process/file/network activity. AgentGuard adds task, tool, memory, trust, provenance and agent-level causal semantics.

## 198. Relationship to SIEM

SIEM aggregates security events across the enterprise. AgentGuard supplies specialized high-context agent runtime events and incidents.

## 199. Relationship to SOAR

SOAR executes response workflows. AgentGuard provides agent-specific detections and evidence that can trigger approved SOAR actions.

## 200. Relationship to authorization

Authorization is preventive permission checking; EDR is continuous behavioral detection and response.

## 201. Relationship to prompt firewalls

Prompt filters are one sensor. AgentGuard correlates prompt evidence with actual runtime side effects.

## 202. Relationship to sandboxing

Sandboxing limits what can physically happen; AgentGuard decides when observed behavior warrants blocking/quarantine/kill.

## 203. Relationship to provenance

Provenance makes causal reconstruction stronger and helps distinguish trusted task instructions from hostile external influence.

## 204. Research opportunity: causal EDR

A major research direction is moving from event correlation to causal agent-security graphs with provenance-carrying tool and memory objects.

## 205. Research opportunity: cross-agent attacks

Detect malicious influence that enters Agent A, is summarized into Agent B, and causes a side effect through Agent C.

## 206. Research opportunity: behavioral invariants

Learn task-specific invariants such as "repository analysis should not require external credential export."

## 207. Research opportunity: counterfactual replay

Ask whether a new policy/detector would have prevented a historical incident and at which event.

## 208. Research opportunity: autonomous SOC safety

Constrain investigator/remediator agents with the same zero-trust controls applied to application agents.

## 209. Production readiness matrix

```text
Capability                         Reference   Enterprise deployment
Typed event schema                 yes         yes
Point sensors                      yes         replace/extend
Sequence detection                 yes         extend
Data-flow detection                baseline    object-level lineage
Risk correlation                   yes         calibrate
Flight recorder                    yes         distributed + versioned
SOC investigation                  yes         evidence-grounded LLM
SQL persistence                    yes         HA/migrations
Agent collectors                   interface   integrate
Streaming backbone                 design      integrate
DLP                                design      integrate
Quarantine enforcement             design      integrate
Credential revocation              design      integrate
Network enforcement                design      integrate
SIEM/SOAR                          design      integrate
Immutable evidence                 design      integrate
Multi-region                       design      deploy
```

## 210. Honest production boundary

The code is a substantive runnable production-oriented reference, not a claim that a FastAPI service alone is a complete enterprise EDR. Real enforcement must be connected to the infrastructure that controls the agent's process, tools, credentials and network.

## 211. Recommended production implementation order

```text
1 workload-authenticated collectors
2 event signatures + trusted tenant
3 Kafka/event backbone
4 detector/rule registry
5 object-level data lineage
6 DLP/secret classifiers
7 graph correlation
8 sandbox/orchestrator quarantine
9 credential revocation
10 network/tool enforcement
11 immutable evidence
12 SIEM/SOAR
13 SSO/RBAC
14 OTel/metrics
15 migrations/HA
16 red-team/load/chaos gates
17 multi-region/residency
```

## 212. Portfolio framing

A strong concise description:

> Built an AI-agent runtime EDR and autonomous SOC reference platform that records agent-native telemetry, correlates prompt/tool/file/credential/network behavior, detects secret-to-egress attack chains, reconstructs replayable causal traces, and drives BLOCK/QUARANTINE/KILL containment with evidence-grounded SOC investigation.

## 213. References

### NVIDIA Open Agent Safety Platform

NVIDIA's public 2026 Open Agent Safety Platform material is relevant to the runtime-boundary, monitoring, watchdog and quarantine direction. AgentGuard is independent code and does not claim to reproduce NVIDIA internals.

### OpenAI — Running Codex safely

OpenAI's public description of running coding agents safely is relevant to sandbox boundaries, network controls, approvals and agent-native security telemetry. AgentGuard is an independent architecture.

### OWASP GenAI Security Project

OWASP guidance on prompt injection and excessive agency provides useful threat-model context for agent runtimes with tools and sensitive resources.

### MITRE ATT&CK

MITRE ATT&CK provides a useful precedent for structured detection engineering and incident classification, though agent-specific techniques require additional taxonomy.

## 214. Citation placement guidance

Use references to support public context and design motivation, not to imply vendor implementation equivalence. Keep repository-specific claims grounded in this codebase and tests.

## 215. Final security model

```text
Agent event
   ->
Authenticated sensor
   ->
Normalized security event
   ->
Point detection
   +
Sequence detection
   +
Data-flow analysis
   +
Causal/provenance graph
   ->
Threat correlation
   ->
ALLOW / BLOCK / QUARANTINE / KILL
   ->
Flight Recorder
   ->
Evidence-grounded SOC investigation
   ->
Human-approved remediation
```

## 216. Final invariant

```text
THE AGENT DOES NOT DECIDE
WHETHER ITS OWN BEHAVIOR IS SAFE.

Observe externally.
Correlate over time.
Track sensitive flows.
Preserve causal evidence.
Contain independently.
Remediate with review.
```

# Research Foundations, References, and Further Reading

AgentGuard is an **independent AI-agent runtime security / EDR reference architecture**. It is informed by publicly available research, security frameworks, and production-system documentation.

The references below motivate specific AgentGuard concepts including:

- agent-native runtime telemetry;
- continuous behavioral monitoring;
- out-of-band enforcement;
- sandbox isolation;
- prompt-injection detection;
- behavioral sequence detection;
- credential-abuse monitoring;
- sensitive-data-flow analysis;
- runtime containment;
- quarantine and kill controls;
- replayable security traces;
- autonomous SOC investigation;
- AI-specific threat classification.

References to NVIDIA, OpenAI, OWASP, MITRE, or other organizations do **not** imply that AgentGuard reproduces their internal systems.

---

# 1. NVIDIA — Open Agent Safety Platform

**NVIDIA. _NVIDIA Launches Open Agent Safety Platform to Secure Agents From Testing to Deployment_. September 28, 2026.**

Official NVIDIA announcement:

NVIDIA Open Agent Safety Platform, NVIDIA OpenShell, and NVIDIA Sentry provide one of the strongest current industry examples of moving agent security outside the model/application boundary.

NVIDIA publicly describes the platform as combining:

```text
NVIDIA OpenShell
       +
Secure Agent Runtime
       +
Runtime Policy Enforcement
       +
NVIDIA Sentry
       +
Out-of-Band Watchdog
       +
BlueField-4 Enforcement
```

OpenShell provides a secure runtime boundary that traces agent actions and enforces policy.

NVIDIA Sentry provides an independent watchdog running on BlueField-4 DPUs that continuously monitors agent activity and can quarantine agents that move outside defined boundaries.

### AgentGuard relevance

This directly motivates AgentGuard's:

```text
Agent Runtime
     ↓
Independent Sensors
     ↓
Behavior Detection
     ↓
Threat Correlation
     ↓
QUARANTINE / KILL
```

It also supports a central AgentGuard design principle:

> **A compromised or manipulated agent should not be responsible for enforcing its own security boundary.**

Relevant AgentGuard components:

- external runtime monitoring;
- quarantine;
- kill/containment;
- agent behavior monitoring;
- independent security plane;
- sandbox supervision;
- policy enforcement;
- continuous runtime security.

**Suggested citation:** `[1]`

---

# 2. NVIDIA — OpenShell Secure Agent Runtime

**NVIDIA. _OpenShell — Open, Secure Runtime for AI Agents_.**

NVIDIA describes OpenShell as a secure runtime that governs agent execution, access, filesystem behavior and network interaction.

Its security model is particularly relevant because enforcement occurs **outside the agent process**.

Conceptually:

```text
Agent
  │
  ▼
Sandbox
  │
  ▼
Supervisor
  │
  ├── Filesystem Policy
  ├── Network Policy
  ├── Process Policy
  └── Runtime Monitoring
          │
          ▼
       Environment
```

### AgentGuard relevance

AgentGuard follows the same fundamental systems-security principle:

```text
Agent
    ≠
Security Monitor
```

Instead:

```text
Agent
   ↓
Externally Observable Runtime
   ↓
AgentGuard Sensor / Enforcement Plane
```

A compromised agent therefore cannot simply decide:

```text
disable_monitoring = true
```

and remove the surrounding security boundary.

This reference is particularly relevant to:

- out-of-process enforcement;
- sandbox monitoring;
- filesystem monitoring;
- network monitoring;
- process monitoring;
- deny-by-default execution;
- auditable runtime decisions.

**Suggested citation:** `[2]`

---

# 3. NVIDIA — Continuous In-Silicon Agent Monitoring

**NVIDIA Technical Blog. _NVIDIA Open Agent Safety Platform: A Reference for Continuous In-Silicon Agent Monitoring_. September 28, 2026.**

This technical description presents an especially relevant architectural pattern:

```text
Agent Runtime
      ↓
OpenShell
      ↓
Software Enforcement
      ↓
Independent Sentry Monitor
      ↓
Hardware / Out-of-Band Enforcement
```

The architecture separates the monitored agent from the monitoring system.

### AgentGuard relevance

This motivates the AgentGuard architecture:

```text
AGENT
  │
  │ telemetry
  ▼
AgentGuard EDR
  │
  ├── Behavior Analysis
  ├── Data-Flow Analysis
  ├── Threat Correlation
  └── Flight Recorder
          │
          ▼
Independent Enforcement
```

The long-term production version of AgentGuard could therefore combine:

```text
Application telemetry
        +
MCP / Gateway telemetry
        +
Sandbox telemetry
        +
OS / eBPF telemetry
        +
Network telemetry
        +
Hardware / infrastructure telemetry
```

This reference is relevant to:

- independent watchdog architecture;
- continuous monitoring;
- quarantine;
- infrastructure-level enforcement;
- agent behavior detection;
- tamper-resistant monitoring.

**Suggested citation:** `[3]`

---

# 4. OpenAI — Running Codex Safely

**OpenAI. _Running Codex safely at OpenAI_. May 8, 2026.**

OpenAI's public description of operating coding agents provides particularly strong motivation for **agent-native telemetry**.

The documented security architecture includes:

- sandboxing;
- constrained execution;
- network policies;
- approval boundaries;
- managed configuration;
- agent-aware logging;
- OpenTelemetry export;
- security triage using agent context.

OpenAI describes telemetry covering events such as:

```text
User Prompt
Tool Approval
Tool Execution
MCP Usage
Network Policy Decision
```

### AgentGuard relevance

This directly motivates AgentGuard's sensor model:

```text
Prompt
   ↓
Plan / Action Metadata
   ↓
Tool Activity
   ↓
Filesystem Activity
   ↓
Credential Activity
   ↓
Network Activity
   ↓
Policy Decisions
```

This provides more security context than conventional endpoint telemetry alone.

**Suggested citation:** `[4]`

---

# 5. OpenAI — Agent-Native Security Telemetry

The same OpenAI Codex security architecture highlights an important distinction between conventional endpoint telemetry and **agent-aware telemetry**.

Traditional security telemetry can tell defenders:

```text
process started
file opened
network connection attempted
```

Agent-aware telemetry can additionally explain:

```text
user requested repository analysis
        ↓
agent selected filesystem tool
        ↓
approval decision occurred
        ↓
tool accessed file
        ↓
network policy blocked destination
```

### AgentGuard relevance

This distinction is fundamental to the **Agent Flight Recorder**.

AgentGuard attempts to combine:

```text
Traditional EDR Context
        +
Agent Context
        +
Tool Context
        +
Policy Context
        +
Provenance Context
```

into one replayable security trace.

**Suggested citation:** `[4]`

---

# 6. OpenAI — AI-Assisted Security Triage

OpenAI also publicly describes using Codex logs alongside an AI-powered security triage agent.

The triage system can use contextual information such as:

```text
Original request
Tool activity
Approval decisions
Tool results
Network-policy decisions
```

to help security teams distinguish expected activity, benign mistakes and events requiring escalation.

### AgentGuard relevance

This closely motivates the AgentGuard:

```text
Autonomous SOC Investigator
```

architecture:

```text
EDR Alert
    ↓
Flight Recorder
    ↓
Trace Reconstruction
    ↓
Investigator Agent
    ↓
Root Cause
    ↓
Attack Classification
    ↓
Remediation Proposal
    ↓
Human Security Analyst
```

AgentGuard deliberately stops short of allowing the SOC agent to deploy arbitrary security policy autonomously.

**Suggested citation:** `[4]`

---

# 7. OWASP — Prompt Injection

**OWASP GenAI Security Project. _LLM01:2025 Prompt Injection_.**

OWASP identifies prompt injection as a major security risk for LLM applications.

Prompt injection can manipulate model behavior and can influence downstream security-sensitive decisions.

### AgentGuard relevance

Prompt injection becomes an AgentGuard **security event**, rather than automatically being treated as proof of compromise.

For example:

```text
Prompt Injection Signal
          ↓
      severity = medium

Prompt Injection
      +
Secret Access
      +
External Upload
          ↓
      severity = critical
```

This distinction is important.

AgentGuard is not simply:

```text
PROMPT_INJECTION = TRUE
```

It is:

```text
What behavior followed the suspicious input?
```

**Suggested citation:** `[5]`

---

# 8. OWASP — Excessive Agency

**OWASP GenAI Security Project. _LLM06:2025 Excessive Agency_.**

OWASP identifies three important sources of excessive agency:

```text
Excessive Functionality
        +
Excessive Permissions
        +
Excessive Autonomy
```

An agent may therefore produce damaging actions following manipulated, ambiguous or otherwise incorrect model output.

### AgentGuard relevance

This motivates monitoring the actual consequences of agent autonomy.

For example:

```text
Agent possesses email-send capability
           ↓
Malicious email enters context
           ↓
Agent reads sensitive messages
           ↓
Agent attempts outbound email
           ↓
AgentGuard observes trajectory
           ↓
BLOCK / QUARANTINE
```

Relevant AgentGuard controls include:

- credential monitoring;
- behavioral sequence detection;
- sensitive-data-flow analysis;
- side-effect monitoring;
- quarantine;
- kill;
- human escalation.

**Suggested citation:** `[6]`

---

# 9. MITRE ATLAS

**MITRE. _Adversarial Threat Landscape for Artificial-Intelligence Systems (ATLAS™)_.**

MITRE ATLAS provides a structured knowledge base of adversarial tactics and techniques affecting AI-enabled systems.

ATLAS is modeled after the broader ATT&CK approach while addressing AI-specific threats.

### AgentGuard relevance

AgentGuard's detection engineering can use an ATLAS-inspired taxonomy:

```text
Incident
   ↓
Technique Classification
   ↓
Behavior Sequence
   ↓
Evidence
   ↓
Detection Rule
   ↓
Response
```

Instead of storing only:

```text
risk = 90
```

an incident should eventually carry information such as:

```text
attack class
technique
affected component
source
target
evidence
confidence
response
```

This reference is relevant to:

- threat classification;
- AI red teaming;
- detection engineering;
- attack taxonomies;
- incident reporting;
- security evaluation.

**Suggested citation:** `[7]`

---

# 10. MITRE ATT&CK

**MITRE. _ATT&CK — Adversarial Tactics, Techniques & Common Knowledge_.**

MITRE ATT&CK provides the broader model that modern EDR and SOC platforms commonly use for organizing adversary behavior.

### AgentGuard relevance

AgentGuard applies the same broad detection-engineering philosophy to autonomous agents:

```text
Raw Event
    ↓
Behavior
    ↓
Technique
    ↓
Incident
    ↓
Response
```

Future AgentGuard rule metadata can therefore include:

```text
rule_id
agent_technique
ATT&CK mapping
ATLAS mapping
severity
confidence
data sources
response
version
owner
```

**Suggested citation:** `[8]`

---

# Reference-to-Architecture Mapping

| AgentGuard subsystem | Primary references |
|---|---|
| External runtime monitoring | [1], [2], [3] |
| Independent watchdog | [1], [3] |
| Sandbox monitoring | [2], [4] |
| Runtime enforcement | [1], [2], [3], [4] |
| Agent-native telemetry | [4] |
| OpenTelemetry integration | [4] |
| Prompt telemetry | [4], [5] |
| Tool telemetry | [4] |
| MCP telemetry | [4] |
| Network-policy telemetry | [2], [4] |
| Prompt-injection detection | [5] |
| Excessive-agency monitoring | [6] |
| Credential-abuse monitoring | [2], [4], [6] |
| Sequence analysis | [1], [3], [7] |
| Data-flow / exfiltration detection | [1], [2], [6], [7] |
| Agent quarantine | [1], [3] |
| Kill / containment | [1], [3] |
| Agent Flight Recorder | [3], [4] |
| Root-cause reconstruction | [4], [7] |
| Autonomous SOC investigator | [4] |
| Threat taxonomy | [7], [8] |
| Detection engineering | [7], [8] |
| AI red-team evaluation | [7] |

---

# Suggested Inline Citations

The README should use the bibliography throughout the architecture discussion rather than leaving all references at the end.

For example:

> Agent monitoring and policy enforcement are strongest when implemented outside the agent process so that manipulated model behavior cannot simply disable the security boundary [1,2,3].

For telemetry:

> Agent-native telemetry augments conventional endpoint logs with user intent, tool activity, approvals, MCP activity, and network-policy decisions [4].

For AgentGuard's EDR concept:

> Runtime agent security increasingly combines sandbox boundaries, agent-aware telemetry, continuous monitoring, and independent containment [1,2,3,4].

For prompt injection:

> Prompt injection should be treated as a security signal whose downstream behavioral consequences must also be observed [5].

For excessive autonomy:

> Tool-using agents can cause damaging actions through excessive functionality, permissions, or autonomy even when the underlying failure begins with ambiguous or manipulated model output [6].

For threat classification:

> Agent security detections should be mapped into structured adversarial techniques rather than represented solely as opaque anomaly scores [7,8].

---

# Research Positioning of AgentGuard

AgentGuard combines several emerging security directions:

```text
Runtime Isolation                         [1,2,3]
        +
Out-of-Band Monitoring                   [1,3]
        +
Agent-Native Telemetry                   [4]
        +
Prompt-Injection Signals                 [5]
        +
Behavior Sequence Detection
        +
Sensitive Data-Flow Analysis
        +
Threat Correlation
        +
Runtime Quarantine                       [1,3]
        +
Agent Flight Recorder                    [3,4]
        +
AI SOC Investigation                     [4]
        +
AI Threat Classification                 [7]
```

The key research question is therefore not simply:

> **Can we detect a malicious prompt?**

It is:

> **Can we continuously reconstruct the causal behavior of an autonomous agent, detect when benign-looking actions combine into a dangerous trajectory, contain the runtime before material damage occurs, and provide a replayable explanation of exactly why containment happened?**

That is the central systems-security problem explored by **AgentGuard**.

---

# AgentGuard vs. Traditional EDR

Traditional endpoint security primarily observes:

```text
Process
Filesystem
Network
Memory
Credentials
```

AgentGuard additionally understands:

```text
User Task
Agent Identity
Agent Session
Tool Invocation
MCP Interaction
External Content Trust
Memory Provenance
Approval Decision
Policy Decision
Agent-to-Agent Message
Sensitive Data Flow
```

The result is:

```text
Traditional EDR telemetry
           +
Agent-native telemetry
           +
Causal/provenance context
           ↓
AI Agent EDR
```

---

# AgentGuard Flight Recorder Research Motivation

The Flight Recorder is especially motivated by the combination of runtime monitoring architectures [1,3] and agent-native telemetry [4].

Its intended trace is:

```text
User Task
   ↓
Untrusted Input
   ↓
Agent Decision
   ↓
Tool Request
   ↓
Sensitive Resource
   ↓
Network Sink
   ↓
Security Finding
   ↓
Runtime Response
```

For example:

```text
T+00.00  repository analysis requested
T+01.21  README read
T+01.22  source classified UNTRUSTED
T+04.11  .env access
T+04.12  SECRET classification
T+05.02  HTTP POST external destination
T+05.03  SECRET → NETWORK violation
T+05.04  operation blocked
T+05.06  runtime quarantined
```

This enables security engineers to investigate **causal agent behavior**, not merely isolated alerts.

---

# Autonomous SOC Safety Principle

An important AgentGuard design decision is:

```text
SOC Agent
   ↓
Investigate
   ↓
Explain
   ↓
Recommend
   ↓
Human Approval
   ↓
Deploy
```

rather than:

```text
SOC Agent
   ↓
Unrestricted autonomous security-policy modification
```

The investigator itself is an autonomous agent and therefore must remain subject to the same principles of least privilege, observability, bounded execution and approval applied to application agents.

---

# Citation Disclaimer

AgentGuard is an **independent research and engineering reference implementation**.

References to NVIDIA, OpenAI, OWASP, MITRE, or other organizations are included to:

- document relevant public research and products;
- establish industry context;
- motivate architecture;
- identify related security techniques;
- provide further reading.

They do **not** imply:

- endorsement;
- affiliation;
- compatibility certification;
- access to proprietary implementations;
- reproduction of vendor source code.

Unless explicitly stated otherwise, AgentGuard's event model, behavior engine, data-flow architecture, Flight Recorder, threat correlator, risk model, SOC workflow and implementation are independent designs.

---

# References

**[1] NVIDIA.** _NVIDIA Launches Open Agent Safety Platform to Secure Agents From Testing to Deployment._ September 28, 2026.

**[2] NVIDIA.** _OpenShell — Open, Secure Runtime for AI Agents._

**[3] NVIDIA Technical Blog.** _NVIDIA Open Agent Safety Platform: A Reference for Continuous In-Silicon Agent Monitoring._ September 28, 2026.

**[4] OpenAI.** _Running Codex safely at OpenAI._ May 8, 2026.

**[5] OWASP GenAI Security Project.** _LLM01:2025 Prompt Injection._

**[6] OWASP GenAI Security Project.** _LLM06:2025 Excessive Agency._

**[7] MITRE.** _Adversarial Threat Landscape for Artificial-Intelligence Systems (ATLAS™)._

**[8] MITRE.** _ATT&CK — Adversarial Tactics, Techniques & Common Knowledge._

---

# Final Research Principle

```text
A suspicious prompt is an event.
A secret read is an event.
A network request is an event.

The security incident exists in
the relationship between them.

              ↓

Observe behavior.
Preserve causality.
Track information flow.
Correlate sequences.
Contain independently.
Replay exactly.
Explain with evidence.
Remediate with control.
```
