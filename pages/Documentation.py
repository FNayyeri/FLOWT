import streamlit as st
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))
from sidebar_config import setup_sidebar

# Page configuration
st.set_page_config(page_title="Documentation", page_icon="📖", layout="wide")

# Setup sidebar
setup_sidebar()

st.title("📖 Documentation")


# st.markdown('<hr style="margin: 5px 0; border: 1px solid #ddd;">', unsafe_allow_html=True)

# Create tabs for different documents
st.markdown("""
    <style>
    /* --- TAB CONTAINER --- */
    /* Make the whole tab container stretch across the page */
    div[data-baseweb="tab-list"] {
        display: flex;
        justify-content: space-between;
        width: 100%;
        background-color: #f8f9fa;  /* Dark background for the tab bar */
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }


    /* --- INDIVIDUAL TABS --- */
    /* Make each tab take equal space */
    div[data-baseweb="tab"] {
        flex: 1 !important;
        text-align: center;
    }

    /* Default state of tab buttons */
    div[data-baseweb="tab"] > button {
        width: 100%;
        background-color: #8CD2FB;  
        color: #fff !important;
        border-radius: 8px;
        padding: 10px;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }

    /* Hover effect: Blue background and white text */
    div[data-baseweb="tab"] > button:hover {
        background-color: #007BFF !important;
        color: white !important;
    }

    /* Active tab style */
    div[data-baseweb="tab"][aria-selected="true"] > button {
        background-color: #0056b3 !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["README", "Installation", "Features", "Model Cards", "LICENSE"])

with tab1:
    st.header("README")
    readme_path = Path("docs/README.md")
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        import re
        def color_text(text):
            # Replace word 'red' with red color
            text = re.sub(r'\bred\b', r'<span style="color:red;">red</span>', text, flags=re.IGNORECASE)
            # Replace word 'green' with green color
            text = re.sub(r'\bgreen\b', r'<span style="color:green;">green</span>', text, flags=re.IGNORECASE)
            return text
        # Replace the flowchart image markdown with actual image display
        if "## Overview" in readme_content:
            parts = readme_content.split("## Overview")
            col1, col2 = st.columns([2,1])
            with col1:
                st.markdown(f'{parts[1]}')
                # parts[1]
            with col2:
                # Display the actual image
                flowchart_path = Path("config/Flowchart.png")
                if flowchart_path.exists():
                    st.image(str(flowchart_path), caption="FLOWT Pipeline Workflow", width="stretch")
            
            # Display content after image
            if len(parts) > 1:
                st.markdown(parts[2])

        else:
            st.markdown(readme_content)
    else:
        st.error("README.md file not found")

with tab2:
    setup_path = Path("docs/installation.md")
    if setup_path.exists():
        with open(setup_path, 'r', encoding='utf-8') as f:
            setup_content = f.read()
        st.markdown(setup_content)

with tab3:
    core_features_path = Path("docs/Features.md")
    if core_features_path.exists():
        with open(core_features_path, 'r', encoding='utf-8') as f:
            core_features_content = f.read()
        st.markdown(core_features_content)

with tab4:
    # st.header("Model Cards")
    model_cards_path = Path("docs/Model_Cards.md")
    if model_cards_path.exists():
        with open(model_cards_path, 'r', encoding='utf-8') as f:
            model_cards_content = f.read()
        st.markdown(model_cards_content)
    
       
        # Replace the flowchart image markdown with actual image display
        if "## Comparison Table" in model_cards_content:
            data = {
                "Model": ["Model1", "Model2", "Model3", "Model4"],
                "Speed": ["⭐⭐⭐⭐☆ (Very Fast)", "⭐⭐⭐⭐☆ (Fast)", "⭐⭐⭐☆☆ (Medium)", "⭐⭐⭐⭐⭐ (Fastest)"],
                "Accuracy": ["⭐⭐⭐☆☆ (Good)", "⭐⭐⭐☆☆ (Better)", "⭐⭐⭐⭐⭐ (High)", "⭐⭐⭐⭐⭐ (Highest)"],
                "Hardware Needs": ["⭐☆☆☆☆ (Low)", "⭐⭐☆☆☆ (Moderate)", "⭐⭐⭐⭐☆ (Medium-High)", "⭐⭐⭐⭐☆ (High)"],
                "Best Use Case": [
                    "Small projects, quick tests",
                    "Balanced speed & accuracy",
                    "High-accuracy applications",
                    "Best overall if hardware allows"
                ]
            }
            import pandas as pd
            # Create a DataFrame
            df = pd.DataFrame(data)

            st.dataframe(df, width='content')
    else:
        st.error(f"Model Cards file not found in {model_cards_path}")


with tab5:
    st.header("LICENSE")
    license_path = Path("docs/LICENSE")
    if license_path.exists():
        with open(license_path, 'r', encoding='utf-8') as f:
            license_content = f.read()
        st.text(license_content)
    else:
        st.error("LICENSE file not found")