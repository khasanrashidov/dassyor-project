from pydantic import BaseModel


class GoogleLoginRequest(BaseModel):
    credential: str = ""
