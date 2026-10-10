
import os
from dotenv import load_dotenv
from flask import Flask

from routes.student_routes import student_routes
from routes.company_routes import company_routes
from routes.drive_routes import drive_routes
from routes.job_routes import job_routes
from routes.application_routes import application_routes
from routes.interview_routes import interview_routes
from routes.result_routes import result_routes
from routes.offer_routes import offer_routes
from routes.user_routes import user_routes
from routes.dashboard_routes import dashboard_routes

from auth.routes import auth_routes


load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.getenv("FLASK_ENV") == "production"
)

if not app.config["SECRET_KEY"]:
    raise RuntimeError("FLASK_SECRET_KEY is missing from .env")


app.register_blueprint(student_routes)
app.register_blueprint(company_routes)
app.register_blueprint(drive_routes)
app.register_blueprint(job_routes)
app.register_blueprint(application_routes)
app.register_blueprint(interview_routes)
app.register_blueprint(result_routes)
app.register_blueprint(offer_routes)
app.register_blueprint(user_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(dashboard_routes)


@app.route("/")
def home():
    return "Backend is running!"


if __name__ == "__main__":
    app.run(debug=True)
