from typing import Dict, Any, Text, List
from pydantic import BaseModel


class TargetDataFrame(BaseModel):
    columns: Dict[Text, Any]