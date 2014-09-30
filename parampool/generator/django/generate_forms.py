def generate_forms(outfile):
    code = '''\
from django.contrib.auth.models import User
from django import forms

class CreateNewLoginForm(forms.Form):
    """
    Form for creating new login.
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=False)

    def clean(self):
        try:
            if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
                raise forms.ValidationError("Passwords entered do not match")
        except KeyError:
            pass
        if User.objects.filter(username=self.cleaned_data['username']):
            raise forms.ValidationError("User exists!")
        return self.cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
'''

    if outfile is None:
        return code
    else:
        f = open(outfile, 'w')
        f.write(code)
        f.close()
