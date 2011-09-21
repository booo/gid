from flaskext.wtf import Form, TextField, PasswordField, validators

class LoginForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password')

    def toDict(self):
      return {
          'username' : self.username.data,
          'password' : self.password.data
        }
