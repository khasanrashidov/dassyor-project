from pydantic import BaseModel, Field

from models.project.project_status import ProjectStatus


class UpdateProjectRequest(BaseModel):
    name: str = Field(None, min_length=1, max_length=100)
    description: str = Field(None, max_length=1000)
    status: ProjectStatus = None
