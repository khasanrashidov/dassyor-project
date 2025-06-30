import os
import logging
from src.celery_config import celery_app
from src.services.ai_web_search_service import perform_search_and_summarize
from src.services.email_service import send_email
from datetime import datetime
from src.models import get_db_session, SearchTask, RelevantPost
from dotenv import load_dotenv

# Load environment variables

load_dotenv()

CLIENT_APP_HOMEPAGE_URL = os.getenv("CLIENT_APP_HOMEPAGE_URL")

# endregion


@celery_app.task(bind=True, max_retries=3, name="tasks.process_search_and_email")
def process_search_and_email(
    self, user_email, user_query, problem_statement, target_audience
):
    """
    Background task to perform search and send email with results.
    This task is executed asynchronously by Celery workers.
    """
    task_id = self.request.id
    session = get_db_session()

    try:
        # Create a new task record
        task_record = SearchTask(
            task_id=task_id,
            email=user_email,
            query=user_query,
            problem_statement=problem_statement,
            target_audience=target_audience,
        )
        session.add(task_record)
        session.commit()

        logging.info(
            f"Starting background search for query: {user_query} (Task ID: {task_id})"
        )

        # Perform search and get results
        search_results = perform_search_and_summarize(
            user_query, problem_statement, target_audience
        )

        if not search_results:
            logging.warning(f"No search results found for query: {user_query}")
            # Update task status
            task_record.status = "FAILURE"
            task_record.completed_at = datetime.utcnow()
            session.commit()
            return False

        # Extract key fields
        final_summary = search_results.get("final_summary", {})
        analysis = final_summary.get("analysis", "No analysis available.")
        relevant_posts = final_summary.get("relevant_posts", [])

        # Store analysis and relevant posts
        task_record.analysis = analysis
        task_record.status = "SUCCESS"
        task_record.completed_at = datetime.utcnow()
        session.commit()

        # Store relevant posts
        for post in relevant_posts:
            post_record = RelevantPost(
                task_id=task_id,
                title=post.get("title", "Untitled"),
                link=post.get("link", ""),
            )
            session.add(post_record)
        session.commit()

        # Format and send email
        send_results_email(user_email, user_query, analysis, relevant_posts)

        logging.info(f"Search and email completed for {user_email}")
        return True

    except Exception as e:
        logging.error(f"Error in background task: {e}")
        # Update task status in database
        if task_record:
            task_record.status = "FAILURE"
            task_record.completed_at = datetime.utcnow()
            session.commit()
        # Retry the task up to max_retries times
        self.retry(exc=e, countdown=60)  # Retry after 1 minute
        return False
    finally:
        session.close()


def format_relevant_posts(posts):
    """Formats links as clickable text with titles instead of displaying raw URLs."""
    if not posts:
        return "<p>No relevant posts found.</p>"

    formatted_links = ""
    for post in posts:
        title = post.get("title", "Untitled Article")
        url = post.get("link")
        formatted_links += f'<li><a href="{url}" target="_blank">{title}</a></li>'
    return formatted_links


def send_results_email(user_email, user_query, analysis, relevant_posts):
    """Format and send email with search results."""
    # Get current year
    current_year = datetime.now().year

    # Format email content with HTML
    email_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: 'Google Sans', Verdana, sans-serif; color: #333; line-height: 1.6; background-color: #f4f4f4; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #ffffff; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
            <div style="color: #4084f4; border-bottom: 2px solid #ddd; padding-bottom: 5px; margin-bottom: 20px;">
                <h2 style="font-size: 22px;margin-top: 0;">Dassyor AI Search Analysis</h2>
            </div>

            <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #4084f4;margin-top: 0;font-size: 20px;">Analysis</h3>
                <p style="font-size: 16px;margin-bottom: 0;white-space: pre-wrap;">{analysis}</p>
            </div>

            <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #4084f4;margin-top: 0;font-size: 20px;">Relevant Resources</h3>
                <ul style="padding-left: 20px;font-size: 16px;">
                    {format_relevant_posts(relevant_posts)}
                </ul>
            </div>

            <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);">
                <h3 style="color: #4084f4;margin-top: 0;font-size: 20px;">Next Step</h3>
                <p style="font-size: 16px;margin-top: 0;margin-bottom: 0;">
                    Startups face numerous challenges, and your tool has the potential to
                    make a real impact in solving them. To refine and validate your idea
                    further, explore the idea validation phase on Dassyor. Our advanced AI
                    will provide insights and guidance to help you shape your concept
                    effectively. This phase is completely free, and you can get started by
                    signing up <a href="{CLIENT_APP_HOMEPAGE_URL}" target="_blank" style="color: #4084f4; text-decoration: none; font-weight: bold;">here</a>.
                </p>
            </div>

            <div style="margin-top: 20px; font-size: 12px; color: #666; text-align: center;">
                <p>This email was generated automatically by Dassyor AI.</p>
                <p>&copy; {current_year} Dassyor. All rights reserved.</p>
                <p>Tashkent, Uzbekistan</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(user_email, "Your Idea Validation Results", email_body)


# Optional (removed from the final code)
# <div style="margin-bottom: 20px; padding: 15px; background: #f9f9f9; border-radius: 5px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);font-size: 16px;">
#     <strong style="color: #4084f4;">Your search query:</strong>
#     <em>{user_query}</em>
# </div>
