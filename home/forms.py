from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='Name',
        widget=forms.TextInput(attrs={'placeholder': 'Name'})
    )
    subject = forms.CharField(
        max_length=100,
        label='Subject',
        widget=forms.TextInput(attrs={'placeholder': 'Subject'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.TextInput(attrs={'placeholder': 'Email'})
    )
    body = forms.CharField(
        min_length=10,
        max_length=1000,
        label='Message',
        widget=forms.Textarea(attrs={'rows': 5, 'col': 2, 'placeholder': 'Message'})
    )
