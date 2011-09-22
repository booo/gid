from flaskext.wtf import Form, TextField, TextAreaField, BooleanField, validators

class RepositoryForm(Form):
    name = TextField('Name', [validators.Length(min=2, max=25)])
    description = TextAreaField('Description')
    contributers = TextField('Contributers')
    private = BooleanField('Private Repository', default = False)


    def toDict(self):
        return {
            'name'          : self.name.data,
            'description'   : self.description.data,
            'contributers'  : self.contributers.data,
            'private'       : self.private.data
          }
