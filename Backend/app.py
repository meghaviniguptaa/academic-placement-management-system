from flask import Flask

from routes.student_routes import student_routes
from routes.company_routes import company_routes


app = Flask(__name__)

app.register_blueprint(student_routes)
app.register_blueprint(company_routes)


@app.route("/")
def home():
    return "Backend is running!"


if __name__ == "__main__":
    app.run(debug=True)