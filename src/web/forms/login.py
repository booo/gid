from wtforms import Form, BooleanField, TextField, PasswordField, validators

class LoginForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.Required()])
