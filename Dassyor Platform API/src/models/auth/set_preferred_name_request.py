from pydantic import BaseModel


class SetPreferredNameRequest(BaseModel):
    preferred_name: str = ""
