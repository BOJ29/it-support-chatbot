import google.generativeai as genai
import os

class GeminiIntegration:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY', '')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-3.6-flash')
            print("✅ Gemini initialized with gemini-3.6-flash")
        else:
            print("❌ GEMINI_API_KEY not set")
    
    def get_ai_response(self, user_message):
        if not self.api_key:
            print("❌ No API key available")
            return None
        try:
            prompt = f"""You are an IT support assistant for Agmas Ltd, a commodity export company.
Help the staff member with their IT issue.

Staff issue: {user_message}

Provide a helpful, numbered, step-by-step solution. Be concise but thorough."""
            
            print(f"🤖 Calling Gemini: {user_message[:50]}...")
            response = self.model.generate_content(prompt)
            print(f"✅ Gemini responded")
            return response.text
        except Exception as e:
            print(f"❌ Gemini error: {e}")
            import traceback
            traceback.print_exc()
            return None