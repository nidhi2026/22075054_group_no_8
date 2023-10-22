from django import forms
from .models import *

# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment_anime
#         fields = ['content', 'type', 'parent']
#         widgets = {
#             'content': forms.Textarea(attrs={'class': 'form-control'}),
#             'type': forms.Select(choices=Comment_anime, attrs={'class': 'form-control'}),
#             'parent': forms.HiddenInput(),
#         }
