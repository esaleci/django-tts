from django.db import models
from django.utils import timezone

class TTSRequest(models.Model):
    """Model to store TTS request information"""
    text = models.TextField()
    language = models.CharField(max_length=10)
    tld = models.CharField(max_length=10)
    slow = models.BooleanField(default=False)
    pre_process = models.BooleanField(default=True)
    advanced_tokenize = models.BooleanField(default=False)
    file_path = models.CharField(max_length=255)
    file_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"TTS Request {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"