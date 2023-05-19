from django import forms


class TestForm(forms.Form):
    token = forms.CharField()
