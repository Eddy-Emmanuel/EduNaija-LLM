from typing import Literal
from pydantic import BaseModel, Field

class ResponseVerificationSchema(BaseModel):
    is_answered: Literal['yes', 'no'] = Field(..., description="Indicates if the response is accurate")