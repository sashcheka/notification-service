from datetime import datetime

from pydantic import UUID4, BaseModel, EmailStr


class ResetPasswordMessageSchema(BaseModel):
    id: UUID4
    user_id: UUID4
    email: EmailStr
    subject: str
    body: str
    published_at: datetime
    sent_at: datetime
