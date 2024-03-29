from flaskext.wtf import Form, TextField, PasswordField, validators

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=2, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


    def toDict(self):
        return {
            'username'  : self.username.data,
            'email'     : self.email.data,
            'password'  : self.password.data,
            'confirm'   : self.confirm.data

          }
