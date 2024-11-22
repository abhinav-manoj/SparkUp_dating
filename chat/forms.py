from .models import Messages, Conversations
from django import forms
from django.forms import Textarea

class MessageForm(forms.ModelForm):
    message_content = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type a message',
            'style': '''
                background-color: #202C33;
                border: 1px solid #2A3942;
                color: #E9EDEF;
                border-radius: 20px;
                padding: 10px 20px;
                width: 100%;
                outline: none;
            ''',
        })
    )

    class Meta:
        model = Messages
        fields = ('message_content',)

# class SmallMessageForm(forms.ModelForm):
#     class Meta:
#         model = Messages
#         fields = ('message_content',)
#         widgets = {
#             'message_content': Textarea(attrs={'rows':3, 'cols':50}),
#         }