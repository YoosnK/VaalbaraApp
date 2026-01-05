from django import forms
from .models import Task
from django.contrib.auth import get_user_model
User = get_user_model()

class CreateTask(forms.ModelForm):
    title = forms.CharField(
        label="Tiêu đề",
        widget=forms.TextInput(attrs={'class': 'form-textinput'})
    )
    task_for = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='Giao nhiệm vụ cho',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    body = forms.CharField(
        required=False,
        label="Thông tin",
        widget=forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3})
    )
    completion_deadline = forms.DateTimeField(
        label='Hạn hoàn thành',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-datetime'}, format='%Y-%m-%dT%H:%M')
    )
    class Meta:
        model = Task
        fields = ['title','body','completion_deadline', 'task_for']