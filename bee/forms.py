from django import forms
from .models import *

class CommentFormAnime(forms.ModelForm):
    class Meta:
        model = Comment_anime
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

class CommentFormManga(forms.ModelForm):
    class Meta:
        model = Comment_manga
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }
