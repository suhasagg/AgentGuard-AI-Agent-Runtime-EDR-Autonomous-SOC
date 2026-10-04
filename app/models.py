import uuid
from datetime import datetime
from sqlalchemy import String,Integer,DateTime,Float
from sqlalchemy.dialects.postgresql import UUID,JSONB
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy.sql import func
from app.db import Base
class TraceEvent(Base):
 __tablename__="trace_events"
 id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
 session_id:Mapped[str]=mapped_column(String(128),index=True); agent_id:Mapped[str]=mapped_column(String(256),index=True)
 seq:Mapped[int]=mapped_column(Integer); ts:Mapped[float]=mapped_column(Float); kind:Mapped[str]=mapped_column(String(32))
 payload:Mapped[dict]=mapped_column(JSONB); event_hash:Mapped[str]=mapped_column(String(64),unique=True)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class Incident(Base):
 __tablename__="incidents"
 id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
 session_id:Mapped[str]=mapped_column(String(128),index=True); score:Mapped[int]=mapped_column(Integer)
 action:Mapped[str]=mapped_column(String(32)); findings:Mapped[list]=mapped_column(JSONB); root:Mapped[str]=mapped_column(String(64))
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
