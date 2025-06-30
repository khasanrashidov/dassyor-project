import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
from src.tasks import process_search_and_email
from src.models import get_db_session, SearchTask, RelevantPost
from functools import wraps

# region Load environment variables

load_dotenv()

CLIENT_APP_HOMEPAGE_URL = os.getenv("CLIENT_APP_HOMEPAGE_URL")
TASKS_ACCESS_PASSWORD = os.getenv("TASKS_ACCESS_PASSWORD")

# endregion

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {  # This will enable CORS for all routes under /api/
            "origins": ["http://localhost:8080", CLIENT_APP_HOMEPAGE_URL],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    },
)


def check_auth(password):
    """Check if the provided password matches the stored password."""
    return password == TASKS_ACCESS_PASSWORD


def authenticate():
    """Send a 401 response that enables basic auth."""
    return Response(
        "Could not verify your access level for that URL.\n"
        "You have to login with proper credentials",
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'},
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@app.route("/api/v1/search", methods=["POST"])
def search_and_email():
    try:
        data = request.get_json()
        user_email = data.get("email")
        user_query = data.get("query")
        problem_statement = data.get("problem_statement", "")
        target_audience = data.get("target_audience", "")

        if not user_email or not user_query:
            return jsonify({"error": "Email and query are required"}), 400

        # Queue the task
        task = process_search_and_email.delay(
            user_email, user_query, problem_statement, target_audience
        )

        return (
            jsonify(
                {
                    "message": "Your request has been received. Results will be emailed to you shortly.",
                    "email": user_email,
                }
            ),
            202,
        )

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500


@app.route("/api/v1/tasks/<task_id>", methods=["GET"])
@requires_auth
def get_task_status(task_id):
    """Get the status and results of a specific task."""
    try:
        session = get_db_session()
        task = session.query(SearchTask).filter(SearchTask.task_id == task_id).first()

        if not task:
            return jsonify({"error": "Task not found"}), 404

        # Get relevant posts for this task
        relevant_posts = (
            session.query(RelevantPost).filter(RelevantPost.task_id == task_id).all()
        )

        posts_list = []
        for post in relevant_posts:
            posts_list.append({"title": post.title, "link": post.link})

        response = {
            "task_id": task.task_id,
            "email": task.email,
            "query": task.query,
            "problem_statement": task.problem_statement,
            "target_audience": task.target_audience,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "completed_at": (
                task.completed_at.isoformat() if task.completed_at else None
            ),
            "analysis": task.analysis,
            "relevant_posts": posts_list,
        }

        session.close()
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500


@app.route("/api/v1/tasks", methods=["GET"])
@requires_auth
def list_tasks():
    """List all tasks with optional filtering."""
    try:
        session = get_db_session()

        # Get query parameters for filtering
        email = request.args.get("email")
        status = request.args.get("status")

        # Build the query
        query = session.query(SearchTask)

        if email:
            query = query.filter(SearchTask.email == email)
        if status:
            query = query.filter(SearchTask.status == status.upper())

        # Get results and order by creation time (newest first)
        tasks = query.order_by(SearchTask.created_at.desc()).all()

        results = []
        for task in tasks:
            results.append(
                {
                    "task_id": task.task_id,
                    "email": task.email,
                    "query": task.query,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": (
                        task.completed_at.isoformat() if task.completed_at else None
                    ),
                }
            )

        session.close()
        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
