# Form = User se data lene ka form

from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    FloatField,
    PasswordField,
    SubmitField,
    TextAreaField
)

from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    NumberRange,
    Length
)

class RegisterForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[DataRequired()]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(),
                    Length(min=6)]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password")
        ]
    )

    submit = SubmitField("Register")


class LoginForm(FlaskForm):

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    submit = SubmitField("Login")


class GroupForm(FlaskForm):

    name = StringField(
        "Group Name",
        validators=[DataRequired()]
    )

    submit = SubmitField("Create Group")


from wtforms import FloatField

class ExpenseForm(FlaskForm):

    title = StringField(
        "Expense Title",
        validators=[DataRequired()]
    )

    amount = FloatField(
        "Amount",
        validators=[DataRequired()]
    )

    category = StringField(
        "Category",
        validators=[DataRequired()]
    )

    submit = SubmitField(
        "Add Expense"
    )

class MemberForm(FlaskForm):

    name = StringField(
        "Member Name",
        validators=[DataRequired()]
    )

    room_no = StringField(
        "Room Number",
        validators=[DataRequired()]
    )

    submit = SubmitField(
        "Add Member"
    )

class AddGroupMemberForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[DataRequired()]
    )

    submit = SubmitField(
        "Add Member"
    )

class ComplaintForm(FlaskForm):

    title = StringField(
        "Complaint Title",
        validators=[DataRequired()]
    )

    description = TextAreaField(
        "Complaint Description",
        validators=[DataRequired()]
    )

    category = StringField(
        "Category",
        validators=[DataRequired()]
    )

    submit = SubmitField(
        "Submit Complaint"
    )

