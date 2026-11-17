from google import genai
from google.genai import types
import os

class GeminiIntegration:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY', '')
        if self.api_key:
            # Create client with automatic retry for overloaded/temporary errors
            self.client = genai.Client(
                api_key=self.api_key,
                http_options=types.HttpOptions(
                    retry_options=types.HttpRetryOptions(
                        initial_delay=2.0,          # Wait 2s before first retry
                        attempts=6,                 # Max 6 retries
                        exp_base=2,                 # Exponential backoff: 2s, 4s, 8s...
                        max_delay=60,               # Cap each wait at 60s
                        http_status_codes=[429, 500, 502, 503, 504]
                    )
                )
            )
            self.model_name = 'gemini-3.8-flash'
            print(f"✅ Gemini initialized with {self.model_name} (retry enabled)")
        else:
            print("❌ GEMINI_API_KEY not set")
            self.client = None
    
    def get_ai_response(self, user_message):
        if not self.client:
            print("❌ No API key available")
            return None
        try:
            prompt = f"""You are an IT support assistant helping staff with IT issues.
Help the staff member with their IT issue.

Staff issue: {user_message}

Provide a helpful, numbered, step-by-step solution. Be concise but thorough.
Do not mention any company names."""
            
            print(f"🤖 Calling Gemini: {user_message[:50]}...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            print(f"✅ Gemini responded")
            return response.text
        except Exception as e:
            print(f"❌ Gemini error: {type(e).__name__}: {e}")
            return None