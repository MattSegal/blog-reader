from django import forms
from django.forms import widgets

from .models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('url',)
        widgets = {
            'url': widgets.URLInput(
                attrs={
                    'placeholder': 'Enter a blog URL',
                }
            )
        }
