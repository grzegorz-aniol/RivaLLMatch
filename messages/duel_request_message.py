from typing import Optional

from pydantic import BaseModel


class DuelRequestMessage(BaseModel):
    master_model: str
    student_model: str
    template_id: str
    task: str
    message_id: Optional[int] = None
