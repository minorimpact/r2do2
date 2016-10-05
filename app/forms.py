from app.models import User, Task
from flask import g
from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms import StringField, BooleanField, TextAreaField, PasswordField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Length, Optional

def get_task(id):
    i = int(id)
    return Task.query.filter_by(id=i).first()


class LoginForm(Form):
    #openid = StringField('openid', validators = [DataRequired()])
    email = StringField('Email Address', validators = [DataRequired(), Length(min=7, max=120)])
    password = PasswordField('Password', validators = [DataRequired()])
    remember_me = BooleanField('Remember Me', default=False)

class EditUserForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(min=0, max=255)])
    email = StringField('Email Address', validators=[DataRequired(), Length(min=7, max=120)])
    password = PasswordField('password')
    new_password = PasswordField('new_password')
    confirm_new_password = PasswordField('confirm_new_password')

    #def __init__(self, original_name, *args, **kwargs):
    #    Form.__init__(self, *args, **kwargs)
    #    self.original_name = original_name

    def validate(self):
        if not Form.validate(self):
            return False
        #if self.name.data == self.original_name:
        #    return True
        #if self.name.data != User.make_valid_name(self.name.data):
        #    self.name.errors.append('This name has invalid characters. Please use letters, numbers, dots and underscores only.')
        #    return False
        #user = User.query.filter_by(name = self.name.data).first()
        #if user is not None:
        #     self.name.errors.append('This name is already in use. Please choose another one.')
        #     return False
        return True

class RegisterForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Length(min=7, max=140)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=7)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=7)])
    remember_me = BooleanField('Remember Me', default=False)

    def validate(self):
        if not Form.validate(self):
            return False
        if self.password.data != self.confirm_password.data:
            self.confirm_password.errors.append('Passwords do not match!')
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user != None:
            self.email.errors.append('Invalid email address. Please choose another one.')
            return False
        return True

class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])

class NewTaskForm(Form):
    blocked_by = QuerySelectMultipleField('Blocked By', get_label='name', query_factory=lambda: g.user.tasks)
    blocks = QuerySelectMultipleField('Blocks', get_label='name', query_factory=lambda: g.user.tasks)
    description = StringField('Description', validators=[Length(max=255)])
    name = StringField('Name', validators=[DataRequired()])

class EditTaskForm(Form):
    blocked_by = QuerySelectMultipleField('Blocked By', get_label='name')
    blocks = QuerySelectMultipleField('Blocks', get_label='name')
    description = StringField('Description', validators=[Optional(), Length(max=255)])
    done = BooleanField('Done')
    due_date = DateTimeField('Due Date', validators=[Optional()])
    name = StringField('Name', validators=[DataRequired()])

