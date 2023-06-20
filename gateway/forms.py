from django import forms

from gateway.models import Contest, Tag, User


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


class ContestForm(forms.ModelForm):
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    status = forms.ChoiceField(choices=Contest.Status.choices, widget=forms.Select(attrs={'class': 'form-control'}))
    description = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    reg_start = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'form-control'}))
    reg_end = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'form-control'}))
    date_start = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'form-control'}))
    date_end = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'class': 'form-control'}))
    logo = forms.CharField(max_length=300, widget=forms.TextInput(attrs={'class': 'form-control'}))
    participant_cap = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    command_min = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    command_max = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    region = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    contest_admins = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Contest
        fields = '__all__' # указываем все поля модели
