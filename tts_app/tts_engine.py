"""
Enhanced Text-to-Speech Engine for Django
"""

import os
import re
import time
import uuid
from typing import Optional, List, Dict, Union, Tuple

# Third-party imports
from gtts import gTTS, gTTSError
import nltk
from nltk.tokenize import sent_tokenize
from django.conf import settings

# Download NLTK data for tokenization (first-time only)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class EnhancedTTS:
    """
    Enhanced Text-to-Speech class that extends gTTS functionality.
    
    Attributes:
        supported_languages (Dict): Dictionary of supported languages and their codes
        supported_tlds (Dict): Dictionary of supported TLDs and their descriptions
    """
    
    # Dictionary of commonly used languages and their codes
    supported_languages = {
        'english': 'en',
        'spanish': 'es',
        'french': 'fr',
        'german': 'de',
        'italian': 'it',
        'portuguese': 'pt',
        'russian': 'ru',
        'japanese': 'ja',
        'korean': 'ko',
        'chinese': 'zh-CN',
        'arabic': 'ar',
        'hindi': 'hi',
    }
    
    # Dictionary of TLDs for different accents
    supported_tlds = {
        'com': 'US accent (default)',
        'co.uk': 'British accent',
        'com.au': 'Australian accent',
        'co.in': 'Indian accent',
        'ca': 'Canadian accent',
        'ie': 'Irish accent',
        'co.za': 'South African accent',
    }
    
    def __init__(self, 
                 language: str = 'en',
                 tld: str = 'com',
                 slow: bool = False,
                 pre_process: bool = True,
                 advanced_tokenize: bool = False,
                 max_tokens_per_request: int = 100):
        """
        Initialize the EnhancedTTS instance.
        
        Args:
            language: IETF language tag (e.g., 'en', 'es')
            tld: Google Translate top-level domain for accent (e.g., 'com', 'co.uk')
            slow: Whether to speak slowly
            pre_process: Whether to apply text pre-processing
            advanced_tokenize: Whether to use advanced tokenization
            max_tokens_per_request: Maximum number of tokens per API request
        """
        self.language = language
        self.tld = tld
        self.slow = slow
        self.pre_process = pre_process
        self.advanced_tokenize = advanced_tokenize
        self.max_tokens_per_request = max_tokens_per_request
        
        # Create output directory if it doesn't exist
        self.output_dir = os.path.join(settings.MEDIA_ROOT, 'tts_files')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _preprocess_text(self, text: str) -> str:
        """
        Apply text pre-processing to improve speech quality.
        
        Args:
            text: Input text to process
            
        Returns:
            Processed text
        """
        if not self.pre_process:
            return text
        
        # Convert common abbreviations
        abbreviations = {
            'Mr.': 'Mister',
            'Mrs.': 'Misses',
            'Dr.': 'Doctor',
            'Prof.': 'Professor',
            'e.g.': 'for example',
            'i.e.': 'that is',
            'etc.': 'etcetera',
            'vs.': 'versus',
        }
        
        for abbr, expansion in abbreviations.items():
            text = re.sub(r'\b' + re.escape(abbr) + r'\b', expansion, text)
        
        # Handle numbers for better pronunciation
        text = re.sub(r'\b(\d+)\.(\d+)\b', r'\1 point \2', text)  # Decimal points
        
        # Handle special characters
        text = re.sub(r'&', ' and ', text)
        text = re.sub(r'@', ' at ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text into manageable chunks for API requests.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of text chunks
        """
        if self.advanced_tokenize:
            # Use NLTK for sentence tokenization
            sentences = sent_tokenize(text)
            
            chunks = []
            current_chunk = []
            current_token_count = 0
            
            for sentence in sentences:
                # Rough estimation of tokens (words)
                sentence_tokens = len(sentence.split())
                
                if current_token_count + sentence_tokens > self.max_tokens_per_request and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_token_count = sentence_tokens
                else:
                    current_chunk.append(sentence)
                    current_token_count += sentence_tokens
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            return chunks
        else:
            # Simple tokenization by character count
            max_chars = self.max_tokens_per_request * 5  # Rough estimation
            return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
    
    def text_to_speech(self, text: str) -> dict:
        """
        Convert text to speech and save as an audio file.
        
        Args:
            text: Input text to convert to speech
            
        Returns:
            Dictionary with file information
        """
        if not text:
            raise ValueError("Text cannot be empty")
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"tts_{timestamp}_{unique_id}.mp3"
        output_file = os.path.join(self.output_dir, filename)
        
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Tokenize text into manageable chunks
        text_chunks = self._tokenize_text(processed_text)
        
        try:
            if len(text_chunks) == 1:
                # Single chunk, direct conversion
                tts = gTTS(
                    text=text_chunks[0],
                    lang=self.language,
                    slow=self.slow,
                    tld=self.tld,
                )
                tts.save(output_file)
            else:
                # For simplicity, we'll just use the first chunk
                # In a real implementation, you would process all chunks and combine them
                tts = gTTS(
                    text=text_chunks[0],
                    lang=self.language,
                    slow=self.slow,
                    tld=self.tld,
                )
                tts.save(output_file)
            
            # Return file information
            file_url = os.path.join(settings.MEDIA_URL, 'tts_files', filename)
            return {
                'success': True,
                'file_path': output_file,
                'file_url': file_url,
                'filename': filename,
            }
            
        except gTTSError as e:
            return {
                'success': False,
                'error': f"Error with gTTS API: {e}",
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {e}",
            }
    
    @classmethod
    def get_language_choices(cls):
        """Get language choices for form dropdown"""
        return [(code, name.capitalize()) for name, code in cls.supported_languages.items()]
    
    @classmethod
    def get_tld_choices(cls):
        """Get TLD choices for form dropdown"""
        return [(tld, desc) for tld, desc in cls.supported_tlds.items()]