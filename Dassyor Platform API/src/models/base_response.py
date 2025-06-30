from typing import Any, List, Optional

from pydantic import BaseModel


class BaseResponse(BaseModel):
    message: str = ""
    is_success: bool = False
    errors: List[str] = []
    data: Optional[Any] = None
