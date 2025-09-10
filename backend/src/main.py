import os
from fastapi import FastAPI, Depends
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional, List
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker, Session

# ---------- DB Config ----------
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Add connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=50,            # number of connections to keep
    max_overflow=100,        # extra connections allowed under burst
    pool_timeout=30,         # wait time before giving up on a connection
    pool_recycle=1800,       # recycle connections every 30 min
    pool_pre_ping=True,      # auto-reconnect dead connections
    pool_reset_on_return='commit'  # Reset connections on return
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------- DB Model ----------
class IoTEvent(Base):
    __tablename__ = "iot_events"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    site = Column(String)
    lat = Column(Float)
    lon = Column(Float)

    ac_power = Column(Float)
    dc_voltage = Column(Float)
    dc_current = Column(Float)
    temperature_module = Column(Float)
    temperature_ambient = Column(Float)

    operational = Column(Boolean)
    fault_code = Column(String, nullable=True)

    firmware_version = Column(String)
    connection_type = Column(String)

    # ---------- Hybrid properties for nested API ----------
    @hybrid_property
    def location(self):
        return {"site": self.site, "coordinates": {"lat": self.lat, "lon": self.lon}}

    @hybrid_property
    def measurements(self):
        return {
            "ac_power": self.ac_power,
            "dc_voltage": self.dc_voltage,
            "dc_current": self.dc_current,
            "temperature_module": self.temperature_module,
            "temperature_ambient": self.temperature_ambient,
        }

    @hybrid_property
    def status(self):
        return {"operational": self.operational, "fault_code": self.fault_code}

    @hybrid_property
    def meta_info(self):
        return {"firmware_version": self.firmware_version, "connection_type": self.connection_type}


Base.metadata.create_all(bind=engine)

# ---------- Pydantic Schemas ----------
class Coordinates(BaseModel):
    lat: float
    lon: float

class Location(BaseModel):
    site: str
    coordinates: Coordinates

class Measurements(BaseModel):
    ac_power: float
    dc_voltage: float
    dc_current: float
    temperature_module: float
    temperature_ambient: float

class Status(BaseModel):
    operational: bool
    fault_code: Optional[str] = None

class Metadata(BaseModel):
    firmware_version: str
    connection_type: str

class IoTPayload(BaseModel):
    device_id: str
    timestamp: datetime
    location: Location
    measurements: Measurements
    status: Status
    metadata: Metadata = Field(alias="meta_info")

    # allow both metadata & meta_info in payloads
    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    def allow_meta_info(cls, values):
        if isinstance(values, dict):
            if "meta_info" in values and "metadata" not in values:
                values["metadata"] = values.pop("meta_info")
        return values

class IoTResponse(IoTPayload):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------- FastAPI App ----------
app = FastAPI(title="IoT PV Data Service")

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        try:
            db.close()
        except Exception:
            pass

@app.post("/api/submit", response_model=IoTResponse)
def submit_data(payload: IoTPayload, db: Session = Depends(get_db)):
    event = IoTEvent(
        device_id=payload.device_id,
        timestamp=payload.timestamp,
        site=payload.location.site,
        lat=payload.location.coordinates.lat,
        lon=payload.location.coordinates.lon,
        ac_power=payload.measurements.ac_power,
        dc_voltage=payload.measurements.dc_voltage,
        dc_current=payload.measurements.dc_current,
        temperature_module=payload.measurements.temperature_module,
        temperature_ambient=payload.measurements.temperature_ambient,
        operational=payload.status.operational,
        fault_code=payload.status.fault_code,
        firmware_version=payload.metadata.firmware_version,
        connection_type=payload.metadata.connection_type,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@app.get("/api/events", response_model=List[IoTResponse])
def get_events(db: Session = Depends(get_db)):
    return db.query(IoTEvent).all()

