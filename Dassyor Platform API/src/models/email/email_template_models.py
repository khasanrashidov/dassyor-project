from typing import List, Optional, Union
from pydantic import BaseModel, EmailStr, Field


class EmailButton(BaseModel):
    """Model for email buttons"""

    text: str = Field(..., description="Button text")
    url: str = Field(..., description="Button URL")
    color: Optional[str] = Field(
        default="#4084f4", description="Button background color"
    )


class EmailListItem(BaseModel):
    """Model for list items"""

    text: str = Field(..., description="List item text")


class EmailContentBlock(BaseModel):
    """Base model for email content blocks"""

    type: str = Field(..., description="Content block type")


class EmailTextBlock(EmailContentBlock):
    """Model for text content blocks"""

    type: str = Field(default="text", description="Content block type")
    content: str = Field(..., description="Text content")
    font_size: Optional[int] = Field(default=16, description="Font size in pixels")
    color: Optional[str] = Field(default="#333", description="Text color")
    alignment: Optional[str] = Field(default="left", description="Text alignment")


class EmailHeaderBlock(EmailContentBlock):
    """Model for header content blocks"""

    type: str = Field(default="header", description="Content block type")
    title: str = Field(..., description="Header title")
    subtitle: Optional[str] = Field(None, description="Header subtitle")
    color: Optional[str] = Field(default="#4084f4", description="Header color")


class EmailButtonBlock(EmailContentBlock):
    """Model for button content blocks"""

    type: str = Field(default="button", description="Content block type")
    buttons: List[EmailButton] = Field(..., description="List of buttons")
    alignment: Optional[str] = Field(default="center", description="Button alignment")


class EmailListBlock(EmailContentBlock):
    """Model for list content blocks"""

    type: str = Field(default="list", description="Content block type")
    title: Optional[str] = Field(None, description="List title")
    items: List[EmailListItem] = Field(..., description="List items")
    list_type: Optional[str] = Field(
        default="bullet", description="List type: bullet or numbered"
    )


class EmailImageBlock(EmailContentBlock):
    """Model for image content blocks"""

    type: str = Field(default="image", description="Content block type")
    src: str = Field(..., description="Image URL")
    alt: str = Field(..., description="Image alt text")
    width: Optional[int] = Field(None, description="Image width")
    height: Optional[int] = Field(None, description="Image height")
    alignment: Optional[str] = Field(default="center", description="Image alignment")


class EmailDividerBlock(EmailContentBlock):
    """Model for divider content blocks"""

    type: str = Field(default="divider", description="Content block type")
    color: Optional[str] = Field(default="#ddd", description="Divider color")
    height: Optional[int] = Field(default=1, description="Divider height in pixels")


class EmailSpacerBlock(EmailContentBlock):
    """Model for spacer content blocks"""

    type: str = Field(default="spacer", description="Content block type")
    height: int = Field(default=20, description="Spacer height in pixels")


class EmailTemplate(BaseModel):
    """Model for complete email template"""

    subject: str = Field(..., description="Email subject")
    header: Optional[EmailHeaderBlock] = Field(None, description="Email header")
    content_blocks: List[
        Union[
            EmailTextBlock,
            EmailButtonBlock,
            EmailListBlock,
            EmailImageBlock,
            EmailDividerBlock,
            EmailSpacerBlock,
        ]
    ] = Field(..., description="Email content blocks")
    footer_text: Optional[str] = Field(None, description="Custom footer text")
    include_default_footer: Optional[bool] = Field(
        default=True, description="Include default Dassyor footer"
    )


class SendEmailRequest(BaseModel):
    """Model for sending a single email"""

    to_email: EmailStr = Field(..., description="Recipient email address")
    template: EmailTemplate = Field(..., description="Email template")


class BulkEmailRequest(BaseModel):
    """Model for sending bulk emails"""

    to_emails: List[EmailStr] = Field(
        ..., min_items=1, description="List of recipient email addresses"
    )
    template: EmailTemplate = Field(..., description="Email template")
    batch_size: Optional[int] = Field(
        default=50, ge=1, le=100, description="Email batch size"
    )


class PreviewEmailRequest(BaseModel):
    """Model for previewing an email"""

    template: EmailTemplate = Field(..., description="Email template to preview")
    to_email: Optional[EmailStr] = Field(
        None, description="Sample recipient email for preview"
    )
