from pydantic import BaseModel, Field
from typing import Optional

class AppointmentBase(BaseModel):
    patient_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100, 
        description="Name of the patient requesting the appointment"
    )
    contact_number: str = Field(
        ..., 
        min_length=7, 
        max_length=20, 
        description="Active contact number for confirmation"
    )
    preferred_date: str = Field(
        ..., 
        description="Preferred date of appointment (YYYY-MM-DD)"
    )
    preferred_time: str = Field(
        ..., 
        description="Preferred time of appointment (HH:MM)"
    )
    service_requested: Optional[str] = Field(
        None, 
        max_length=250, 
        description="Specific dental treatment being requested"
    )

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(AppointmentBase):
    id: int
    status: str = "Pending"

    class Config:
        from_attributes = True