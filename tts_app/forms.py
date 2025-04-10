from django import forms
from .tts_engine import EnhancedTTS

class TTSForm(forms.Form):
    """Form for text-to-speech conversion"""
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 5,
            'placeholder': 'Enter text to convert to speech...'
        }),
        required=True
    )
    
    language = forms.ChoiceField(
        choices=[('en', 'English')] + EnhancedTTS.get_language_choices(),
        widget=forms.Select(attrs={'class': 'form-input'}),
        required=True
    )
    
    tld = forms.ChoiceField(
        choices=[('com', 'US accent (default)')] + EnhancedTTS.get_tld_choices(),
        widget=forms.Select(attrs={'class': 'form-input'}),
        required=True
    )
    
    slow = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    
    advanced_options = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    
    pre_process = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    
    advanced_tokenize = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )