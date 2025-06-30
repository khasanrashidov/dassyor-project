import os
from datetime import datetime
from typing import Dict, Any, List, Union

from dotenv import load_dotenv

from config.logging_config import get_logger
from models.email.email_template_models import (
    EmailTemplate,
    EmailTextBlock,
    EmailHeaderBlock,
    EmailButtonBlock,
    EmailListBlock,
    EmailImageBlock,
    EmailDividerBlock,
    EmailSpacerBlock,
    EmailButton,
)

# Load environment variables
load_dotenv()
APP_NAME = os.getenv("APP_NAME", "Dassyor")

# Create logger for this module
logger = get_logger(__name__)


class EmailTemplateService:
    """Service for generating HTML email templates with consistent Dassyor styling"""

    def __init__(self):
        self.app_name = APP_NAME
        logger.info("Email Template Service initialized")

    def generate_html_email(self, template: EmailTemplate) -> str:
        """
        Generate complete HTML email from template

        Args:
            template: EmailTemplate object with dynamic content

        Returns:
            str: Complete HTML email string
        """
        logger.debug("Generating HTML email from template")

        try:
            # Generate content blocks HTML
            content_html = self._generate_content_blocks(template.content_blocks)

            # Generate header HTML if provided
            header_html = ""
            if template.header:
                header_html = self._generate_header_block(template.header)

            # Generate footer HTML
            footer_html = self._generate_footer(
                template.footer_text, template.include_default_footer
            )

            # Combine everything into the main template
            full_html = self._generate_base_template(
                content=content_html, header=header_html, footer=footer_html
            )

            logger.info("HTML email generated successfully")
            return full_html

        except Exception as e:
            logger.error(f"Failed to generate HTML email: {str(e)}")
            raise

    def _generate_base_template(
        self, content: str, header: str = "", footer: str = ""
    ) -> str:
        """Generate the base HTML template with Dassyor styling"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.app_name} Email</title>
        </head>
        <body style="font-family: 'Google Sans', Verdana, sans-serif; color: #333; line-height: 1.6; background-color: #f4f4f4; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #ffffff; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
                {header}
                {content}
                {footer}
            </div>
        </body>
        </html>
        """

    def _generate_header_block(self, header: EmailHeaderBlock) -> str:
        """Generate header block HTML"""
        subtitle_html = ""
        if header.subtitle:
            subtitle_html = f'<p style="font-size: 14px; color: #666; margin: 5px 0 0 0;">{header.subtitle}</p>'

        return f"""
        <div style="color: {header.color}; border-bottom: 2px solid #ddd; padding-bottom: 5px; margin-bottom: 20px;">
            <h2 style="font-size: 22px; margin-top: 0; margin-bottom: 0;">{header.title}</h2>
            {subtitle_html}
        </div>
        """

    def _generate_content_blocks(
        self,
        blocks: List[
            Union[
                EmailTextBlock,
                EmailButtonBlock,
                EmailListBlock,
                EmailImageBlock,
                EmailDividerBlock,
                EmailSpacerBlock,
            ]
        ],
    ) -> str:
        """Generate HTML for all content blocks"""
        html_blocks = []

        for block in blocks:
            if block.type == "text":
                html_blocks.append(self._generate_text_block(block))
            elif block.type == "button":
                html_blocks.append(self._generate_button_block(block))
            elif block.type == "list":
                html_blocks.append(self._generate_list_block(block))
            elif block.type == "image":
                html_blocks.append(self._generate_image_block(block))
            elif block.type == "divider":
                html_blocks.append(self._generate_divider_block(block))
            elif block.type == "spacer":
                html_blocks.append(self._generate_spacer_block(block))
            else:
                logger.warning(f"Unknown block type: {block.type}")

        return "".join(html_blocks)

    def _generate_text_block(self, block: EmailTextBlock) -> str:
        """Generate text block HTML"""
        return f"""
        <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
            <p style="font-size: {block.font_size}px; color: {block.color}; margin: 0; text-align: {block.alignment};">{block.content}</p>
        </div>
        """

    def _generate_button_block(self, block: EmailButtonBlock) -> str:
        """Generate button block HTML"""
        buttons_html = []

        for button in block.buttons:
            button_html = f"""
            <a href="{button.url}" style="background-color: {button.color}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; margin: 5px;">{button.text}</a>
            """
            buttons_html.append(button_html)

        return f"""
        <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
            <div style="text-align: {block.alignment}; margin: 10px 0;">
                {"".join(buttons_html)}
            </div>
        </div>
        """

    def _generate_list_block(self, block: EmailListBlock) -> str:
        """Generate list block HTML"""
        title_html = ""
        if block.title:
            title_html = f'<h3 style="color: #4084f4; margin-top: 0; font-size: 20px; margin-bottom: 15px;">{block.title}</h3>'

        list_tag = "ul" if block.list_type == "bullet" else "ol"
        list_items = []

        for item in block.items:
            list_items.append(f"<li>{item.text}</li>")

        return f"""
        <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
            {title_html}
            <{list_tag} style="font-size: 16px; margin-bottom: 0; padding-left: 20px;">
                {"".join(list_items)}
            </{list_tag}>
        </div>
        """

    def _generate_image_block(self, block: EmailImageBlock) -> str:
        """Generate image block HTML"""
        width_style = f"width: {block.width}px;" if block.width else ""
        height_style = f"height: {block.height}px;" if block.height else ""

        return f"""
        <div style="margin-bottom: 20px; text-align: {block.alignment};">
            <img src="{block.src}" alt="{block.alt}" style="{width_style} {height_style} max-width: 100%; border-radius: 5px;">
        </div>
        """

    def _generate_divider_block(self, block: EmailDividerBlock) -> str:
        """Generate divider block HTML"""
        return f"""
        <div style="margin: 20px 0;">
            <hr style="border: none; height: {block.height}px; background-color: {block.color};">
        </div>
        """

    def _generate_spacer_block(self, block: EmailSpacerBlock) -> str:
        """Generate spacer block HTML"""
        return f"""
        <div style="height: {block.height}px;"></div>
        """

    def _generate_footer(
        self, custom_footer_text: str = None, include_default_footer: bool = True
    ) -> str:
        """Generate footer HTML"""
        footer_parts = []

        if custom_footer_text:
            footer_parts.append(f"<p>{custom_footer_text}</p>")

        if include_default_footer:
            current_year = datetime.now().year
            default_footer = f"""
            <p>This email was sent automatically by {self.app_name}.</p>
            <p>&copy; {current_year} {self.app_name}. All rights reserved.</p>
            <p>Tashkent, Uzbekistan</p>
            """
            footer_parts.append(default_footer)

        if footer_parts:
            return f"""
            <div style="margin-top: 20px; font-size: 12px; color: #666; text-align: center;">
                {"".join(footer_parts)}
            </div>
            """

        return ""

    def generate_preview_metadata(self, template: EmailTemplate) -> Dict[str, Any]:
        """
        Generate metadata for email preview

        Args:
            template: EmailTemplate object

        Returns:
            Dict with preview metadata
        """
        try:
            # Count different block types
            block_counts = {}
            for block in template.content_blocks:
                block_type = block.type
                block_counts[block_type] = block_counts.get(block_type, 0) + 1

            # Estimate email size
            html_content = self.generate_html_email(template)
            estimated_size = len(html_content.encode("utf-8"))

            return {
                "subject": template.subject,
                "has_header": template.header is not None,
                "content_block_counts": block_counts,
                "total_blocks": len(template.content_blocks),
                "estimated_size_bytes": estimated_size,
                "estimated_size_kb": round(estimated_size / 1024, 2),
                "has_custom_footer": template.footer_text is not None,
                "includes_default_footer": template.include_default_footer,
            }

        except Exception as e:
            logger.error(f"Failed to generate preview metadata: {str(e)}")
            raise
