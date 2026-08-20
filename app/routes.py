from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    session
)

from app.forms import (
    ExpenseForm,
    RegisterForm,
    LoginForm,
    GroupForm
)

from flask_login import (
    login_required, 
    current_user, 
    login_user, 
    logout_user)

from app.models import (
    User,
    Group,
    GroupMember,
    Expense)

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

        existing_user = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_user:

            flash(
                "Email already registered."
            )

            return redirect(
                url_for("main.login")
            )

        user = User(
            name=form.name.data,
            email=form.email.data
        )

        user.set_password(
            form.password.data
        )

        db.session.add(user)

        db.session.commit()

        flash(
            "Registration successful."
        )

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

            login_user(user)

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

    user = User.query.get(
        session["user_id"]
    )

    return render_template(
        "dashboard.html",
        user=user
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


@main.route("/add-expense/<int:group_id>", methods=["GET", "POST"])
@login_required
def add_expense(group_id):

    group = Group.query.get_or_404(group_id)

    member = GroupMember.query.filter_by(
        user_id=current_user.id,
        group_id=group_id
    ).first()

    if not member:
        flash("You are not a member of this group.", "danger")
        return redirect(url_for("main.groups"))

    form = ExpenseForm()

    if form.validate_on_submit():

        expense = Expense(
            title=form.title.data,
            amount=form.amount.data,
            category=form.category.data,
            paid_by=current_user.id,
            group_id=group_id
        )

        db.session.add(expense)
        db.session.commit()

        flash("Expense added successfully!", "success")

        return redirect(
            url_for(
                "main.expenses",
                group_id=group_id
            )
        )

    return render_template(
        "add_expense.html",
        form=form,
        group=group
    )

@main.route("/expenses/<int:group_id>")
@login_required
def expenses(group_id):

    group = Group.query.get_or_404(group_id)

    member = GroupMember.query.filter_by(
        user_id=current_user.id,
        group_id=group_id
    ).first()

    if not member:
        flash("You are not a member of this group.", "danger")
        return redirect(url_for("main.groups"))

    all_expenses = Expense.query.filter_by(
        group_id=group_id
    ).order_by(
        Expense.date.desc()
    ).all()

    return render_template(
        "expenses.html",
        expenses=all_expenses,
        group=group
    )

@main.route("/delete-expense/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):

    expense = Expense.query.get_or_404(
        expense_id
    )

    if expense.paid_by != current_user.id:
        flash(
            "You can delete only your own expenses.",
            "danger"
        )

        return redirect(
            url_for(
                "main.expenses",
                group_id=expense.group_id
            )
        )

    group_id = expense.group_id

    db.session.delete(expense)
    db.session.commit()

    flash(
        "Expense deleted successfully!",
        "success"
    )

    return redirect(
        url_for(
            "main.expenses",
            group_id=group_id
        )
    )

@main.route(
    "/groups",
    methods=["GET", "POST"]
)
def groups():

    if "user_id" not in session:

        return redirect(
            url_for("main.login")
        )

    if request.method == "POST":

        name = request.form.get("name")

        group = Group(
            name=name,
            user_id=session["user_id"]
        )

        db.session.add(group)

        db.session.commit()

        return redirect(
            url_for("main.groups")
        )

    groups = Group.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "groups.html",
        groups=groups
    )


@main.route("/groups/create", methods=["GET", "POST"])
@login_required
def create_group():
    form = GroupForm()

    if form.validate_on_submit():
        group = Group(
            name=form.name.data,
            user_id=current_user.id
        )
        db.session.add(group)
        db.session.flush()

        db.session.add(GroupMember(
            group_id=group.id,
            user_id=current_user.id
        ))
        db.session.commit()

        flash("Group created successfully!", "success")
        return redirect(url_for("main.groups"))

    return render_template("create_group.html", form=form)


