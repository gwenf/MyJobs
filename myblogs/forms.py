from django import forms
from django.forms.widgets import SplitDateTimeWidget
from myblogs.models import BlogEntry
from ckeditor.widgets import CKEditorWidget


class BlogEntryForm(forms.ModelForm):
    class Meta:
        model = BlogEntry
        fields = ('title', 'body', 'published_on', 'tags')

    body = forms.CharField(widget=CKEditorWidget())
