import streamlit as st
import sys
import os
import tempfile
from io import BytesIO

# Ensure matplotlib can cache fonts on hosts with restricted home directories.
matplotlib_cache_dir = os.path.join(tempfile.gettempdir(), "lapin_mpl_cache")
os.makedirs(matplotlib_cache_dir, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", matplotlib_cache_dir)

# Add src/ to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_processor import SurveyDataProcessor
from chart_generator import ChartGenerator
from presentation_builder import PresentationBuilder

# --- Page config ---
st.set_page_config(
    page_title="Lapin Trust Index Report Generator",
    page_icon="assets/logos/Lapin_Symbol_RGB_Navy.png" if os.path.exists("assets/logos/Lapin_Symbol_RGB_Navy.png") else None,
    layout="centered",
)

# --- Custom styling ---
st.markdown("""
<style>
    /* Background */
    .stApp { background-color: #ffffff; }

    /* All text black */
    h1, h2, h3, h4, h5, h6, p, span, label, div,
    .stMarkdown, .stText, [data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
    }

    /* File uploader box */
    [data-testid="stFileUploader"] {
        background-color: #f5f5f5 !important;
        border: 1.5px solid #000000 !important;
        border-radius: 6px !important;
    }
    [data-testid="stFileUploader"] * {
        color: #000000 !important;
    }

    /* All buttons */
    .stButton > button, .stDownloadButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.6rem 2rem !important;
        font-size: 1rem !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #333333 !important;
        color: #ffffff !important;
    }
    .stButton > button *, .stDownloadButton > button * {
        color: #ffffff !important;
    }

    /* Info / success / error boxes */
    [data-testid="stAlert"] {
        background-color: #f5f5f5 !important;
        border: 1px solid #cccccc !important;
        color: #000000 !important;
        border-radius: 6px !important;
    }
    [data-testid="stAlert"] * {
        color: #000000 !important;
    }

    /* Progress bar */
    .stProgress > div > div {
        background-color: #000000 !important;
    }

    /* Metrics */
    [data-testid="stMetric"] * {
        color: #000000 !important;
    }

    /* Hide Streamlit top bar */
    header[data-testid="stHeader"] { background: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# --- Logo + Header ---
logo_path = "assets/logos/Lapin_LogoLockup_RGB_DarkGray.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=200)

st.title("Trust Index Report Generator")
st.markdown("Upload your survey data spreadsheet and generate a branded PowerPoint report.")

st.divider()

# --- File upload ---
uploaded_file = st.file_uploader(
    "Upload Survey Data (.xlsx)",
    type=["xlsx"],
    help="Select the Excel file containing survey responses."
)

if uploaded_file is not None:
    st.success(f"Uploaded: **{uploaded_file.name}**")

    if st.button("Generate Report", type="primary"):
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            progress = st.progress(0, text="Processing survey data...")

            # Step 1: Process data
            processor = SurveyDataProcessor(tmp_path)
            progress.progress(10, text="Survey data loaded.")

            # Step 2: Initialize chart generator
            chart_gen = ChartGenerator(processor)
            progress.progress(20, text="Chart generator ready.")

            # Step 3: Build presentation
            progress.progress(25, text="Building presentation slides...")
            builder = PresentationBuilder(processor, chart_gen)
            prs = builder.build_full_report()
            progress.progress(90, text="Presentation built.")

            # Step 4: Save to bytes
            output_buf = BytesIO()
            prs.save(output_buf)
            output_buf.seek(0)
            progress.progress(100, text="Done!")

            # Summary
            st.divider()
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Slides", len(prs.slides))
            col2.metric("Roles", len(processor.roles))
            col3.metric("Categories", len(processor.get_all_categories()))

            st.markdown(f"**Roles found:** {', '.join(processor.roles)}")

            # Download button
            output_name = uploaded_file.name.replace('.xlsx', '_report.pptx')
            st.download_button(
                label="Download Report",
                data=output_buf,
                file_name=output_name,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
            st.exception(e)

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

else:
    st.info("Please upload an .xlsx survey data file to get started.")
