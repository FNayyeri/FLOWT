import streamlit as st
from pathlib import Path


def setup_sidebar():
    """Setup sidebar navigation and AI configuration for all pages"""
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown("Select a component from the pages above to get started.")

    # AI API Configuration in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 AI Configuration")

    # Initialize session state for API keys
    if "google_api_key" not in st.session_state:
        st.session_state.google_api_key = ""
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""

    # Check if AI service is available
    try:
        import sys
        sys.path.append(str(Path(__file__).parent))
        from genai_service import GenAIService, GENAI_AVAILABLE, OPENAI_AVAILABLE
        genai_service = GenAIService()
        available_providers = genai_service.get_available_providers()
        
        if not GENAI_AVAILABLE and not OPENAI_AVAILABLE:
            st.sidebar.error("No AI packages installed")
        elif not available_providers:
            # Show API key inputs
            if GENAI_AVAILABLE:
                google_key = st.sidebar.text_input(
                    "Google GenAI API Key",
                    value=st.session_state.google_api_key,
                    type="password",
                    help="Get from Google AI Studio"
                )
                st.sidebar.markdown("[Get Google AI Studio Key](https://aistudio.google.com/apikey)")
                if google_key != st.session_state.google_api_key:
                    st.session_state.google_api_key = google_key
                    st.rerun()
            
            if OPENAI_AVAILABLE:
                openai_key = st.sidebar.text_input(
                    "OpenAI API Key",
                    value=st.session_state.openai_api_key,
                    type="password",
                    help="Get from OpenAI"
                )
                st.sidebar.markdown("[Get OpenAI API Key](https://platform.openai.com/api-keys)")
                if openai_key != st.session_state.openai_api_key:
                    st.session_state.openai_api_key = openai_key
                    st.rerun()
            
            if not available_providers:
                st.sidebar.warning("Enter API key to enable AI features")
        else:
            # Show configured providers
            provider_status = []
            if genai_service.is_genai_configured():
                provider_status.append("Google GenAI")
            if genai_service.is_openai_configured():
                provider_status.append("OpenAI")
            
            st.sidebar.success(f"✅ AI: {', '.join(provider_status)}")
            
            if st.sidebar.button("Reset API Keys", type="primary"):
                st.session_state.google_api_key = ""
                st.session_state.openai_api_key = ""
                st.rerun()

    except ImportError:
        st.sidebar.info("AI features not available")