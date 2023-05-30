from django import forms


class TestForm(forms.Form):
    token = forms.CharField()


class SendSolutionValidationForm(forms.Form):
    solution_url = forms.URLField()
    command_id = forms.IntegerField()


class SetContestAdminValidationForm(forms.Form):
    participant_id = forms.IntegerField()
    contest_id = forms.IntegerField()


class SetParticipantValidationForm(forms.Form):
    contest_id = forms.IntegerField()