from django import forms
from .models import Post, Tag

class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter tags separated by #'})
    )

    class Meta:
        model = Post
        fields = '__all__'
        exclude = ['user']

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