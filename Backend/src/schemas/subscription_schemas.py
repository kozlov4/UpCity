from typing import Optional
from pydantic import BaseModel
from datetime import date

class SubscriptionOut(BaseModel):
    subscription_id: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    model_config = {
        "from_attributes": True
    }