from flaskext.wtf import Form, TextField, TextAreaField, BooleanField, validators

class RepositoryForm(Form):
    name = TextField('Name', [validators.Length(min=4, max=25)])
    description = TextAreaField('Description')
    collaborators = TextField('Collaborators')
    private = BooleanField('Private Repository')
