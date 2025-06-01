from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task, Category

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class CategoryForm(forms.ModelForm):
    color = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'color'}),
        label='Couleur'
    )

    class Meta:
        model = Category
        fields = ['name', 'color']

class TaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='Date limite'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            # Filtrer les tâches parentes possibles
            parent_tasks = Task.objects.filter(user=user, parent_task__isnull=True)
            if self.instance.pk:
                parent_tasks = parent_tasks.exclude(pk=self.instance.pk)
            self.fields['parent_task'].queryset = parent_tasks
            self.fields['parent_task'].label = 'Tâche parente (optionnel)'

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'status', 'category', 'parent_task']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'parent_task': forms.Select(attrs={'class': 'form-select'})
        } 