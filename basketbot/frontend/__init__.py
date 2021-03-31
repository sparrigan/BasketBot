from flask import Blueprint

frontend = Blueprint("frontend", __name__)

@frontend.route("/", methods=["GET"])
def index():
    return "hello"
