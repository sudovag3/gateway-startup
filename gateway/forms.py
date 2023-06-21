from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from django import forms

from gateway.models import Contest, Tag, User, Task, Award, Command


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
    description = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    reg_start = forms.DateTimeField(widget=DateTimePickerInput())
    reg_end = forms.DateTimeField(widget=DateTimePickerInput())
    date_start = forms.DateTimeField(widget=DateTimePickerInput())
    date_end = forms.DateTimeField(widget=DateTimePickerInput())
    logo = forms.CharField(max_length=300, widget=forms.TextInput(attrs={'class': 'form-control'}))
    participant_cap = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    command_min = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    command_max = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    region = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Contest
        fields = ['name', 'description', 'reg_start', 'reg_end', 'date_start', 'date_end', 'logo', 'participant_cap',
                  'command_min', 'command_max', 'region', 'tags']


class CommandForm(forms.ModelForm):
    command_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    task = forms.ModelChoiceField(
        queryset=Task.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    open_to_invite = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input m-1'}),
        required=False
    )

    class Meta:
        model = Command
        fields = ['command_name', 'task', 'open_to_invite']

    def __init__(self, *args, **kwargs):
        self.contest = kwargs.pop('contest', None)
        super(CommandForm, self).__init__(*args, **kwargs)
        if self.contest:
            self.fields['task'].queryset = Task.objects.filter(contest=self.contest)


class TaskForm(forms.ModelForm):
    contest = forms.ModelChoiceField(
        queryset=Contest.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    task_name = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    task_description = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Task
        fields = ['contest', 'task_name', 'task_description', 'tags']

    def __init__(self, *args, **kwargs):
        self.contest = kwargs.pop('contest', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        if self.contest:
            self.fields['contest'].initial = self.contest
            self.fields['contest'].queryset = Contest.objects.filter(id=self.contest.id)


class AwardForm(forms.ModelForm):
    task = forms.ModelChoiceField(
        queryset=Task.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    command = forms.ModelChoiceField(
        queryset=Command.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    description = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    award = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Award
        fields = ['task', 'command', 'name', 'description', 'award']

    def __init__(self, *args, **kwargs):
        self.contest = kwargs.pop('contest', None)
        super(AwardForm, self).__init__(*args, **kwargs)
        if self.contest:
            self.fields['task'].queryset = Task.objects.filter(contest=self.contest)
            self.fields['command'].queryset = Command.objects.filter(contest=self.contest)
