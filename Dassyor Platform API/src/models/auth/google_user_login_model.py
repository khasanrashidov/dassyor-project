from pydantic import BaseModel


class GoogleUserLoginModel(BaseModel):
    email: str = ""
    first_name: str = ""
    last_name: str = ""
