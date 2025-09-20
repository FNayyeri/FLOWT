import streamlit as st
from typing import Optional

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

class GenAIService:
    def __init__(self):
        self.genai_model = None
        self.openai_client = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize AI models with API keys"""
        # Initialize Google GenAI
        if GENAI_AVAILABLE:
            try:
                api_key = st.session_state.get("google_api_key")
                if not api_key:
                    try:
                        api_key = st.secrets.get("GOOGLE_API_KEY")
                    except:
                        pass
                
                if api_key:
                    genai.configure(api_key=api_key)
                    self.genai_model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                self.genai_model = None
        
        # Initialize OpenAI
        if OPENAI_AVAILABLE:
            try:
                api_key = st.session_state.get("openai_api_key")
                if not api_key:
                    try:
                        api_key = st.secrets.get("OPENAI_API_KEY")
                    except:
                        pass
                
                if api_key:
                    self.openai_client = openai.OpenAI(api_key=api_key)
            except Exception:
                self.openai_client = None
    
    def generate_analysis(self, prompt: str, provider: str = "google") -> Optional[str]:
        """Generate analysis using specified AI provider"""
        if provider == "google":
            return self._generate_with_genai(prompt)
        elif provider == "openai":
            return self._generate_with_openai(prompt)
        return None
    
    def _generate_with_genai(self, prompt: str) -> Optional[str]:
        """Generate analysis using Google GenAI"""
        if not self.genai_model:
            return None
        
        try:
            response = self.genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"Error with Google GenAI: {str(e)}")
            return None
    
    def _generate_with_openai(self, prompt: str) -> Optional[str]:
        """Generate analysis using OpenAI"""
        if not self.openai_client:
            return None
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Error with OpenAI: {str(e)}")
            return None
    
    def is_genai_configured(self) -> bool:
        """Check if Google GenAI is configured"""
        return self.genai_model is not None
    
    def is_openai_configured(self) -> bool:
        """Check if OpenAI is configured"""
        return self.openai_client is not None
    
    def get_available_providers(self) -> list:
        """Get list of available AI providers"""
        providers = []
        if self.is_genai_configured():
            providers.append("google")
        if self.is_openai_configured():
            providers.append("openai")
        return providers