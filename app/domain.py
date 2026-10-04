from pydantic import BaseModel,Field
from typing import Literal,Any
class Event(BaseModel):
 session_id:str; agent_id:str; seq:int; ts:float; kind:Literal["prompt","reasoning","memory","tool_request","tool_result","file","network","credential","policy"]
 action:str=""; resource:str=""; data:dict[str,Any]=Field(default_factory=dict)
 trust:Literal["TRUSTED","UNTRUSTED","UNKNOWN"]="UNKNOWN"
 classification:Literal["PUBLIC","INTERNAL","CONFIDENTIAL","SECRET"]="INTERNAL"
 parent_ids:list[str]=Field(default_factory=list)
class Finding(BaseModel):
 rule:str; severity:int; message:str; event_seq:int
class Verdict(BaseModel):
 session_id:str; score:int; action:Literal["ALLOW","BLOCK","QUARANTINE","KILL"]; findings:list[Finding]; causal_root:str
