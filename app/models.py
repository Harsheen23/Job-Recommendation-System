from pydantic import BaseModel
from typing import List, Optional

class Job(BaseModel):
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    apply_link: Optional[str] = None
    description: Optional[str] = None
    score: Optional[float] = None
