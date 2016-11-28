from django import forms

class SignInForm(forms.Form):
	emailFi = forms.EmailField()
	passwordField = forms.PasswordInput()