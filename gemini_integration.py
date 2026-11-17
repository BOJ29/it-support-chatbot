from google import genai
import os

class GeminiIntegration:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY', '')
        if self.api_key:
            # New SDK: create a client, no more genai.configure()
            self.client = genai.Client(api_key=self.api_key)
            # 'gemini-3.6-flash' is a valid stable model name[citation:1][citation:2]
            self.model_name = 'gemini-3.6-flash'
            print(f"✅ Gemini initialized with {self.model_name}")
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
            # New SDK call syntax
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            print(f"✅ Gemini responded")
            return response.text
        except Exception as e:
            print(f"❌ Gemini error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None