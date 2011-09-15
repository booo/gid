from flaskext.wtf import Form, TextField, PasswordField, TextAreaField, validators

class ProfileForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    key = TextAreaField('SSH-Key')
