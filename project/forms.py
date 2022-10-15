from django import forms
from .models import PullRequest


class PRSubmissionForm(forms.ModelForm):

    class Meta:
        model = PullRequest
        fields = ('pr_link',)


class PRJudgeForm(forms.ModelForm):

    class Meta:
        model = PullRequest
        fields = ('bonus', 'penalty', 'remark',)
