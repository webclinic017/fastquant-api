from typing import Dict, Any, Text, List
from pydantic import BaseModel


class DashboardSubscriptionConfiguration(BaseModel):
    columns: Dict[Text, List[Text]] # publisher name -- list of columns
    