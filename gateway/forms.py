from django import forms


class TestForm(forms.Form):
    token = forms.CharField()


class SendSolutionValidationForm(forms.Form):
    solution_id = forms.URLField()
    command_id = forms.IntegerField()

