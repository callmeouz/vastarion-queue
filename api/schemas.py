from pydantic import BaseModel
from typing import Optional

class TaskSubmit(BaseModel):
    task_data: dict
    priority: Optional[int] = None

class EmailCampaign(BaseModel):
    campaign_name: str
    emails: list[str]
    subject: str
    body: str