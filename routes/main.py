from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route("/")
def home():
    return redirect(url_for("auth.login"))
