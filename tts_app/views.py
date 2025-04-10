from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from .forms import TTSForm
from .models import TTSRequest
from .tts_engine import EnhancedTTS

def index(request):
    """Main view for the TTS application"""
    form = TTSForm()
    recent_requests = TTSRequest.objects.all()[:5]
    
    context = {
        'form': form,
        'recent_requests': recent_requests,
        'audio_file': None,
    }
    
    return render(request, 'tts_app/index.html', context)

@require_POST
def convert_text(request):
    """AJAX endpoint for text-to-speech conversion"""
    form = TTSForm(request.POST)
    if form.is_valid():
        # Get form data
        text = form.cleaned_data['text']
        language = form.cleaned_data['language']
        tld = form.cleaned_data['tld']
        slow = form.cleaned_data['slow']
        pre_process = form.cleaned_data.get('pre_process', True)
        advanced_tokenize = form.cleaned_data.get('advanced_tokenize', False)
        
        # Initialize TTS engine
        tts = EnhancedTTS(
            language=language,
            tld=tld,
            slow=slow,
            pre_process=pre_process,
            advanced_tokenize=advanced_tokenize
        )
        
        # Convert text to speech
        result = tts.text_to_speech(text)
        
        if result['success']:
            # Save request to database
            tts_request = TTSRequest(
                text=text,
                language=language,
                tld=tld,
                slow=slow,
                pre_process=pre_process,
                advanced_tokenize=advanced_tokenize,
                file_path=result['file_path'],
                file_url=result['file_url']
            )
            tts_request.save()
            
            return JsonResponse({
                'success': True,
                'audio_url': result['file_url'],
                'filename': result['filename']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Unknown error')
            })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Invalid form data',
            'form_errors': form.errors
        })

def history(request):
    """View for displaying TTS request history"""
    requests = TTSRequest.objects.all()
    return render(request, 'tts_app/history.html', {'requests': requests})