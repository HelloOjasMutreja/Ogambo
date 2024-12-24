from django import forms
from .models import Post, Tag
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'input-field',  # Your custom CSS class
                'placeholder': field.label,
            })

class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter tags separated by #'})
    )

    class Meta:
        model = Post
        fields = '__all__'
        exclude = ['user', 'tags', 'image', 'video']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            tags_input = self.cleaned_data['tags_input']
            tags = self.parse_tags(tags_input)
            instance.tags.set(tags)
        return instance

    @staticmethod
    def parse_tags(tags_input):
        tags = [tag.strip() for tag in tags_input.split('#') if tag.strip()]
        tag_objects = []
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(name=tag)
            tag_objects.append(tag_obj)
        return tag_objects