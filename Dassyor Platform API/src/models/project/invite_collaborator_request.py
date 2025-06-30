from pydantic import BaseModel, EmailStr


class InviteCollaboratorRequest(BaseModel):
    """Request model for inviting a collaborator to a project"""

    email: EmailStr
