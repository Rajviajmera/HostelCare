from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    session
)

from app.forms import (
    RegisterForm,
    LoginForm
)

from app.models import User
from app import db

main = Blueprint(
    "main",
    __name__
)

@main.route("/")
def home():
    return redirect(
        url_for("main.login")
    )

@main.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        user = User(
            username=form.username.data,
            email=form.email.data
        )

        user.set_password(
            form.password.data
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration Successful")

        return redirect(
            url_for("main.login")
        )

    return render_template(
        "register.html",
        form=form
    )

@main.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and user.check_password(
            form.password.data
        ):

            session["user_id"] = user.id

            return redirect(
                url_for(
                    "main.dashboard"
                )
            )

        flash(
            "Invalid Credentials"
        )

    return render_template(
        "login.html",
        form=form
    )

@main.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(
            url_for("main.login")
        )

    return render_template(
        "dashboard.html"
    )

@main.route("/logout")
def logout():

    session.pop(
        "user_id",
        None
    )

    return redirect(
        url_for("main.login")
    )

