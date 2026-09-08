from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    session,
    request
)

from app.forms import (
    ExpenseForm,
    RegisterForm,
    LoginForm,
    GroupForm,
    MemberForm,
    AddGroupMemberForm,
    ComplaintForm
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
    Expense,
    Member,
    Complaint
    )

from sqlalchemy import or_, and_

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
            username=form.username.data,
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
@login_required
def dashboard():

    return render_template(
        "dashboard.html",
        user=current_user
    )



@main.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("main.login")
    )


@main.route(
    "/add-expense",
    methods=["GET", "POST"]
)
@login_required
def add_expense():

    form = ExpenseForm()

    if form.validate_on_submit():

        expense = Expense(
            title=form.title.data,
            amount=form.amount.data,
            category=form.category.data,
            paid_by=current_user.id,
            user_id=current_user.id
        )

        db.session.add(expense)
        db.session.commit()

        flash(
            "Expense added successfully!",
            "success"
        )

        return redirect(
            url_for("main.expenses")
        )

    return render_template(
        "add_expense.html",
        form=form
    )
    
@main.route("/expenses")
@login_required
def expenses():

    all_expenses = Expense.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Expense.created_at.desc()
    ).all()

    return render_template(
        "expenses.html",
        expenses=all_expenses
    )


@main.route(
    "/delete-expense/<int:expense_id>",
    methods=["POST"]
)
def delete_expense(expense_id):

    if "user_id" not in session:

        return redirect(
            url_for("main.login")
        )

    expense = Expense.query.get_or_404(
        expense_id
    )

    if expense.user_id != current_user.id:

        flash("You cannot delete this expense.")

        return redirect(
            url_for("main.expenses")
        )

    db.session.delete(expense)

    db.session.commit()

    flash(
        "Expense deleted successfully."
    )

    return redirect(
        url_for("main.expenses")
    )

@main.route(
    "/groups",
    methods=["GET", "POST"]
)
@main.route("/groups")
@login_required
def groups():

    user_groups = Group.query.join(
        GroupMember,
        Group.id == GroupMember.group_id
    ).filter(
        GroupMember.user_id == current_user.id
    ).all()

    return render_template(
        "groups.html",
        groups=user_groups
    )

@main.route(
    "/groups/create",
    methods=["GET", "POST"]
)
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

        membership = GroupMember(
            group_id=group.id,
            user_id=current_user.id
        )

        db.session.add(membership)
        db.session.commit()

        flash(
            "Group created successfully!",
            "success"
        )

        return redirect(
            url_for("main.groups")
        )

    return render_template(
        "create_group.html",
        form=form
    )

@main.route(
    "/group/<int:group_id>"
)
@login_required
def group(group_id):

    group = Group.query.get_or_404(
        group_id
    )

    membership = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user.id
    ).first()

    if not membership:

        flash(
            "You are not a member of this group.",
            "danger"
        )

        return redirect(
            url_for("main.groups")
        )

    memberships = GroupMember.query.filter_by(
        group_id=group_id
    ).all()

    members = []

    for item in memberships:

        user = User.query.get(item.user_id)

        if user:
            members.append(user)

    form = AddGroupMemberForm()

    return render_template(
        "group.html",
        group=group,
        members=members,
        form=form
    )

@main.route(
    "/group/<int:user_id>/add-expense",
    methods=["GET", "POST"]
)
@login_required
def add_group_expense(user_id):

    if "user_id" not in session:

        return redirect(
            url_for("main.login")
        )

    group = Group.query.get_or_404(
        user_id
    )

    if request.method == "POST":

        title = request.form.get(
            "title"
        )

        amount = request.form.get(
            "amount"
        )

        paid_by = request.form.get(
            "paid_by"
        )

        expense = Expense(

            title=title,

            amount=float(amount),

            paid_by=paid_by,

            group_id=group.id

        )

        db.session.add(expense)

        db.session.commit()

        return redirect(
            url_for(
                "main.group_expenses",
                user_id=group.id
            )
        )

    return render_template(
        "add_group_expense.html",
        group=group
    )


@main.route(
    "/delete-group-expense/<int:expense_id>",
    methods=["POST"]
)
def delete_group_expense(expense_id):

    if "user_id" not in session:

        return redirect(
            url_for("main.login")
        )

    expense = Expense.query.get_or_404(
        expense_id
    )

    group = Group.query.get_or_404(
        expense.group_id
    )

    if group.user_id != session["user_id"]:

        flash(
            "You cannot delete this expense."
        )

        return redirect(
            url_for(
                "main.group_expenses",
                group_id=group.id
            )
        )

    db.session.delete(expense)

    db.session.commit()

    return redirect(
        url_for(
            "main.group_expenses",
            group_id=group.id
        )
    )


@main.route(
    "/members",
    methods=["GET", "POST"]
)
@login_required
def members():

    form = MemberForm()

    if form.validate_on_submit():

        member = Member(
            name=form.name.data,
            room_no=form.room_no.data,
            user_id=current_user.id
        )

        db.session.add(member)
        db.session.commit()

        flash(
            "Hostel member added successfully!",
            "success"
        )

        return redirect(
            url_for("main.members")
        )

    member_list = Member.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "members.html",
        form=form,
        members=member_list
    )

@main.route(
    "/group/<int:group_id>/add-member",
    methods=["POST"]
)
@login_required
def add_group_member(group_id):

    group = Group.query.get_or_404(
        group_id
    )

    membership = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=current_user.id
    ).first()

    if not membership:

        flash(
            "You are not a member of this group.",
            "danger"
        )

        return redirect(
            url_for("main.groups")
        )

    username = request.form.get(
        "username"
    )

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:

        flash(
            "User not found.",
            "danger"
        )

        return redirect(
            url_for(
                "main.group",
                group_id=group_id
            )
        )

    already_member = GroupMember.query.filter_by(
        group_id=group_id,
        user_id=user.id
    ).first()

    if already_member:

        flash(
            "User is already a group member.",
            "warning"
        )

        return redirect(
            url_for(
                "main.group",
                group_id=group_id
            )
        )

    new_member = GroupMember(
        group_id=group_id,
        user_id=user.id
    )

    db.session.add(new_member)
    db.session.commit()

    flash(
        "User added to group.",
        "success"
    )

    return redirect(
        url_for(
            "main.group",
            group_id=group_id
        )
    )


@main.route(
    "/complaint/new",
    methods=["GET", "POST"]
)
@login_required
def new_complaint():

    form = ComplaintForm()

    if form.validate_on_submit():

        complaint = Complaint(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            status="Pending",
            visibility="admin",
            created_by=current_user.id
        )

        db.session.add(complaint)
        db.session.commit()

        flash(
            "Complaint submitted successfully!",
            "success"
        )

        return redirect(
            url_for("main.my_complaints")
        )

    return render_template(
        "new_complaint.html",
        form=form
    )

@main.route("/my-complaints")
@login_required
def my_complaints():

    complaints = Complaint.query.filter(
        or_(
            Complaint.created_by == current_user.id,

            Complaint.visibility == "everyone",

            and_(
                Complaint.visibility == "specific",
                Complaint.target_user_id ==
                current_user.id
            )
        )
    ).order_by(
        Complaint.created_at.desc()
    ).all()

    return render_template(
        "my_complaints.html",
        complaints=complaints
    )

@main.route("/admin/complaints")
@login_required
def admin_complaints():

    if not current_user.is_admin:

        flash(
            "Admin access required.",
            "danger"
        )

        return redirect(
            url_for("main.dashboard")
        )

    complaints = Complaint.query.order_by(
        Complaint.created_at.desc()
    ).all()

    users = User.query.order_by(
        User.username
    ).all()

    return render_template(
        "admin_complaints.html",
        complaints=complaints,
        users=users
    )

@main.route(
    "/admin/complaint/<int:complaint_id>/update",
    methods=["POST"]
)
@login_required
def update_complaint(complaint_id):

    if not current_user.is_admin:

        flash(
            "Admin access required.",
            "danger"
        )

        return redirect(
            url_for("main.dashboard")
        )

    complaint = Complaint.query.get_or_404(
        complaint_id
    )

    status = request.form.get(
        "status"
    )

    visibility = request.form.get(
        "visibility"
    )

    if status not in [
        "Pending",
        "Clear",
        "Unclear"
    ]:

        flash(
            "Invalid complaint status.",
            "danger"
        )

        return redirect(
            url_for("main.admin_complaints")
        )

    if visibility not in [
        "admin",
        "everyone",
        "specific"
    ]:

        flash(
            "Invalid complaint visibility.",
            "danger"
        )

        return redirect(
            url_for("main.admin_complaints")
        )

    complaint.status = status
    complaint.visibility = visibility

    if visibility == "specific":

        target_user_id = request.form.get(
            "target_user_id"
        )

        if not target_user_id:

            flash(
                "Please select a user.",
                "danger"
            )

            return redirect(
                url_for("main.admin_complaints")
            )

        target_user = User.query.get(
            int(target_user_id)
        )

        if not target_user:

            flash(
                "Selected user does not exist.",
                "danger"
            )

            return redirect(
                url_for("main.admin_complaints")
            )

        complaint.target_user_id = target_user.id

    else:

        complaint.target_user_id = None

    db.session.commit()

    flash(
        "Complaint updated successfully!",
        "success"
    )

    return redirect(
        url_for("main.admin_complaints")
    )

