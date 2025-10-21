import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.arima.model import ARIMA
import datetime
import time
import io
import warnings
warnings.filterwarnings('ignore')

# ---------- HELPER FUNCTIONS ----------
def hex_to_rgba(hex_color, alpha=0.2):
    """
    Convert hex color string to rgba string with specified alpha (0-1).
    Example: hex_to_rgba("#6ea8fe", 0.18) -> "rgba(110,168,254,0.18)"
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
    except Exception:
        return "rgba(110,168,254,0.18)"

# ---- Additional imports for enhancements ----
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
except ImportError:
    AgGrid = None
try:
    import kaleido  # noqa: F401
except ImportError:
    kaleido = None
import tempfile
from PIL import Image

# Additional imports for new tabs
import importlib
from io import BytesIO

# Prophet for forecasting
try:
    from prophet import Prophet
except ImportError:
    Prophet = None
try:
    import seaborn as sns
    import matplotlib.pyplot as plt
except ImportError:
    sns = None
    plt = None
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
except ImportError:
    canvas = None

# ---------- PAGE CONFIG AND THEME ----------
st.set_page_config(
    page_title="COVID-19 Analytics Hub",
    layout="wide",
    page_icon="🦠",
    initial_sidebar_state="expanded"
)

#####################
# ---------- CUSTOM CSS FOR ENHANCED STYLING (MODERN LIGHT THEME) ----------
# Highly attractive, clean, pastel, light-themed dashboard
st.markdown("""
<style>
    /* --- Modern Typography --- */
    html, body, .stApp {
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif !important;
        background: #f7f9fb !important;
        color: #222 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif !important;
        letter-spacing: -0.01em;
    }
    h1 {font-size: 2.6rem !important; font-weight: 900 !important; margin-bottom: 0.2em;}
    h2 {font-size: 1.7rem !important; font-weight: 700 !important;}
    h3 {font-size: 1.3rem !important; font-weight: 600 !important;}
    .subtitle {
        font-size: 1.15rem;
        margin-top: -1em;
        margin-bottom: 1.1em;
        color: #666;
        opacity: 0.85;
    }

    /* --- Sidebar Modernization --- */
    section[data-testid="stSidebar"] {
        /* Very light, skin-toned gradient for subtle, attractive look */
        background: linear-gradient(135deg, #fff7f1 0%, #ffeede 100%);
        box-shadow: 2px 0 20px 0 rgba(224,192,168,0.08), 0 2px 8px 0 rgba(255,238,222,0.05);
        border-radius: 0 22px 22px 0;
        min-width: 320px !important;
        padding-top: 1.2rem !important;
        padding-bottom: 1rem !important;
    }
    .sidebar-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.4rem;
        padding-left: 6px;
    }
    .sidebar-logo {
        width: 50px; height: 50px;
        border-radius: 12px;
        background: linear-gradient(135deg, #6ea8fe 0%, #f7f9fb 100%);
        display: flex; align-items: center; justify-content: center;
    }
    .sidebar-title {
        font-size: 1.13rem;
        font-weight: 700;
        color: #2a3a5f;
        letter-spacing: 0.01em;
    }

    /* --- Animated Logo --- */
    @keyframes floatLogo {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-6px) rotate(10deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    .sidebar-logo img {
        animation: floatLogo 3s ease-in-out infinite;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .sidebar-logo img:hover {
        transform: scale(1.15) rotate(5deg);
        box-shadow: 0 0 18px rgba(110,168,254,0.35);
    }

    /* --- Animated Gradient Title --- */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .sidebar-title .gradient-text {
        background: linear-gradient(270deg, #ff7b7b, #6ea8fe, #b39ddb, #ffd6f9);
        background-size: 600% 600%;
        -webkit-background-clip: text;
        color: transparent;
        font-weight: 800;
        font-size: 1.22rem;
        animation: gradientShift 6s ease infinite;
    }
    .sidebar-card {
        background: linear-gradient(135deg, #ffffff 60%, #f4f7fa 100%);
        border-radius: 16px;
        box-shadow: 0 2px 10px 0 rgba(110,168,254,0.07);
        padding: 1.1rem 1rem 0.3rem 1rem;
        margin-bottom: 1.2rem;
        border: 1px solid #f0f4fa;
    }

    /* --- KPI Cards --- */
    .metrics-container {
        display: flex;
        flex-wrap: wrap;
        gap: 22px;
        margin: 1.3rem 0 2.3rem 0;
    }
    .metric-card {
        flex: 1;
        min-width: 190px;
        max-width: 265px;
        border-radius: 22px;
        padding: 1.6rem 1.2rem 1.2rem 1.2rem;
        text-align: center;
        background: linear-gradient(135deg, #ffffff 75%, #f6faff 100%);
        box-shadow: 0 4px 18px 0 rgba(110,168,254,0.10), 0 1.5px 5px 0 rgba(255,184,108,0.07);
        transition: transform 0.32s cubic-bezier(.38,.1,.36,.9), box-shadow 0.32s cubic-bezier(.38,.1,.36,.9);
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    .metric-card-wide {
        flex-basis: 60%; /* reduced from 70% */
        min-width: 280px;
        max-width: 85%;
        border-radius: 24px;
        padding: 2rem 2rem 1.5rem 2rem;
        text-align: left;
        font-size: 1.15rem;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: center;
        margin-bottom: 0.8rem;
        background: linear-gradient(90deg, #eaf1ff 50%, #f7f9fb 100%);
        box-shadow: 0 6px 24px 0 rgba(110,168,254,0.12), 0 2px 8px 0 rgba(255,184,108,0.08);
        transition: transform 0.32s cubic-bezier(.38,.1,.36,.9), box-shadow 0.32s cubic-bezier(.38,.1,.36,.9);
        cursor: pointer;
    }
    .metric-card-wide:hover {
        transform: translateY(-7px) scale(1.018);
        box-shadow: 0 14px 40px 0 rgba(110,168,254,0.19), 0 4px 16px 0 rgba(255,184,108,0.13);
    }
    .metric-card.cases, .metric-card-wide.cases {
        background: linear-gradient(90deg, #eaf1ff 70%, #b4d8fe 90%, #6ea8fe 100%);
        border-top: 7px solid #6ea8fe;
    }
    .metric-card.deaths, .metric-card-wide.deaths {
        background: linear-gradient(90deg, #fff0f0 70%, #ffc9c9 90%, #ff7b7b 100%);
        border-top: 7px solid #ff7b7b;
    }
    .metric-card.recovered, .metric-card-wide.recovered {
        background: linear-gradient(90deg, #f3fff2 70%, #b9f6c3 90%, #7ed96e 100%);
        border-top: 7px solid #7ed96e;
    }
    .metric-card.active, .metric-card-wide.active {
        background: linear-gradient(90deg, #fff6e8 70%, #ffe1b4 90%, #ffb86c 100%);
        border-top: 7px solid #ffb86c;
    }
    .metric-card.mortality, .metric-card-wide.mortality {
        background: linear-gradient(90deg, #f6eaff 70%, #e2d3fd 90%, #b39ddb 100%);
        border-top: 7px solid #b39ddb;
    }
    /* NEW: pastel purple-pink gradient for affected countries KPI */
    .metric-card.affected, .metric-card-wide.affected {
        background: linear-gradient(90deg, #f6eaff 60%, #ffd6f9 80%, #eabfff 100%);
        border-top: 7px solid #eabfff;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #2a3a5f;
        letter-spacing: -0.02em;
        margin-bottom: 0.05em;
    }
    .metric-label {
        font-size: 1.04rem;
        margin-top: 0.3rem;
        font-weight: 500;
        color: #7b859a;
        opacity: 0.82;
        letter-spacing: 0.01em;
    }
    .metric-change {
        display: inline-block;
        padding: 4px 13px;
        border-radius: 13px;
        font-size: 0.93rem;
        margin-top: 0.7rem;
        font-weight: 600;
        box-shadow: 0 1px 4px 0 rgba(110,168,254,0.08);
    }
    .kpi-positive {
        background: rgba(126,217,110,0.13);
        color: #50b46b;
        border: 1px solid #7ed96e;
    }
    .kpi-negative {
        background: rgba(255,123,123,0.13);
        color: #ff7b7b;
        border: 1px solid #ff7b7b;
    }

    /* --- Modern Card Container --- */
    .card {
        border-radius: 20px;
        padding: 1.8rem 1.2rem 1.2rem 1.2rem;
        margin-bottom: 1.7rem;
        background: linear-gradient(135deg, #ffffff 70%, #f4f7fa 100%);
        box-shadow: 0 3px 18px 0 rgba(110,168,254,0.10), 0 1px 4px 0 rgba(255,184,108,0.07);
        transition: box-shadow 0.28s;
    }
    .card:hover {
        box-shadow: 0 8px 28px 0 rgba(110,168,254,0.14), 0 2px 10px 0 rgba(255,184,108,0.10);
    }

    /* --- Modern Tabs --- */
    .stTabs {
        padding: 0px 7px 0px 7px !important;
        margin-bottom: 1.1rem !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        padding: 8px 14px;
        border-radius: 18px;
        background: #f4f7fa;
        box-shadow: 0 1px 4px 0 rgba(110,168,254,0.06);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 11px !important;
        padding: 11px 24px !important;
        font-size: 1.11rem !important;
        font-weight: 600 !important;
        background: #f7f9fb;
        color: #4f5a6d !important;
        margin-right: 1px;
        border: none !important;
        transition: background 0.23s, color 0.23s;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #eaf1ff 60%, #6ea8fe 100%);
        color: #2457a7 !important;
        box-shadow: 0 2px 8px 0 rgba(110,168,254,0.11);
    }

    /* --- Data Badge --- */
    .data-badge {
        display: inline-flex;
        align-items: center;
        padding: 7px 16px;
        border-radius: 22px;
        font-size: 1.04rem;
        font-weight: 500;
        margin-bottom: 20px;
        background: linear-gradient(90deg, #eaf1ff 60%, #6ea8fe 100%);
        color: #2457a7;
        box-shadow: 0 1px 6px 0 rgba(110,168,254,0.08);
    }

    /* --- Loading Animation --- */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(110,168,254,0.18);
        border-radius: 50%;
        border-top-color: #6ea8fe;
        animation: spin 1s ease-in-out infinite;
        margin-right: 13px;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* --- Modern Table Styling --- */
    .dataframe, .stDataFrame, .stTable, .ag-theme-streamlit {
        background: #fff !important;
        border-radius: 13px !important;
        border: 1.7px solid #eaf1ff !important;
        overflow: hidden !important;
        box-shadow: 0 1.5px 7px 0 rgba(110,168,254,0.07);
        font-size: 1.02rem !important;
    }
    .dataframe th, .stDataFrame th, .stTable th {
        background: #f7f9fb !important;
        color: #2a3a5f !important;
        font-weight: 700 !important;
        padding: 8px 7px !important;
        border-bottom: 1.5px solid #eaf1ff !important;
    }
    .dataframe td, .stDataFrame td, .stTable td {
        padding: 7px 7px !important;
        border-bottom: 1px solid #f0f4fa !important;
    }
    .dataframe tr:nth-child(even), .stDataFrame tr:nth-child(even), .stTable tr:nth-child(even) {
        background: #f4f7fa !important;
    }
    .dataframe tr:nth-child(odd), .stDataFrame tr:nth-child(odd), .stTable tr:nth-child(odd) {
        background: #fff !important;
    }
    /* AG-Grid overrides */
    .ag-theme-streamlit .ag-row-even { background: #f4f7fa !important; }
    .ag-theme-streamlit .ag-row-odd { background: #fff !important; }
    .ag-theme-streamlit .ag-header-cell-label { color: #2a3a5f !important; font-weight: bold; }
    .ag-theme-streamlit .ag-root-wrapper { border-radius: 13px !important; border: 1.7px solid #eaf1ff !important; }

    /* --- Enhanced Buttons --- */
    .stButton>button, .stDownloadButton>button {
        border-radius: 13px;
        font-weight: 700;
        font-size: 1.07rem;
        padding: 0.65rem 1.6rem;
        margin: 0.15rem 0.25rem;
        background: linear-gradient(90deg, #eaf1ff 60%, #6ea8fe 100%);
        color: #2457a7;
        border: 1.5px solid #eaf1ff;
        box-shadow: 0 1.5px 6px 0 rgba(110,168,254,0.10);
        transition: background 0.24s, color 0.21s, box-shadow 0.19s;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background: linear-gradient(90deg, #ffb86c 40%, #ff7b7b 100%);
        color: #fff;
        border: 1.5px solid #ffb86c;
        box-shadow: 0 4px 14px 0 rgba(255,184,108,0.18);
        transform: translateY(-2px) scale(1.03);
    }

    /* --- Download Section as Card in Sidebar --- */
    .sidebar-download-card {
        background: linear-gradient(135deg, #fff 60%, #eaf1ff 100%);
        border-radius: 16px;
        box-shadow: 0 2px 10px 0 rgba(110,168,254,0.07);
        padding: 1.2rem 1.1rem 1rem 1.1rem;
        margin-top: 2.2rem;
        border: 1px solid #f0f4fa;
    }
    .sidebar-download-header {
        font-size: 1.08rem;
        font-weight: 600;
        color: #2a3a5f;
        margin-bottom: 0.7rem;
        letter-spacing: 0.01em;
    }

    /* --- Footer --- */
    .footer {
        background: #f7f9fb;
        text-align: center;
        padding: 22px 0 8px 0;
        margin-top: 44px;
        font-size: 1.01rem;
        color: #a2aab7;
        opacity: 0.86;
        border-top: 1.5px solid #eaf1ff;
        border-radius: 0 0 22px 22px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- DATA LOADING WITH ERROR HANDLING ----------
@st.cache_data(ttl=3600, show_spinner=False)
def load_data(dataset_type="weekly"):
    """
    Optimized data loading function with robust error handling
    """
    try:
        start_time = time.time()
        if dataset_type == "daily":
            file_path = "WHO-COVID-19-global-daily-data.csv"
            df = pd.read_csv(file_path, parse_dates=['Date_reported'])
        else:  # weekly data
            file_path = "WHO-COVID-19-global-data.csv"
            df = pd.read_csv(file_path, parse_dates=['Date_reported'])
            
        # Basic data cleaning
        df['Year'] = df['Date_reported'].dt.year
        df['Month'] = df['Date_reported'].dt.strftime('%b %Y')
        df['Week'] = df['Date_reported'].dt.isocalendar().week
        
        # Handle NaN values in WHO_region to fix tree map errors
        df['WHO_region'] = df['WHO_region'].fillna('OTHER')
        
        # Make sure Country has no NaN values
        df['Country'] = df['Country'].fillna('Unknown')
        
        # Calculate metrics based on data type
        df = df.sort_values(['Country', 'Date_reported'])
        
        if dataset_type == "daily":
            # Daily metrics
            df['New_daily_cases'] = df.groupby('Country')['Cumulative_cases'].diff().fillna(0)
            df['New_daily_deaths'] = df.groupby('Country')['Cumulative_deaths'].diff().fillna(0)
            
            # Calculate weekly metrics from daily data
            df['week_id'] = df['Date_reported'].dt.strftime('%Y-%U')
            weekly_aggs = df.groupby(['Country', 'WHO_region', 'week_id']).agg({
                'Date_reported': 'last',
                'Cumulative_cases': 'last',
                'Cumulative_deaths': 'last',
                'New_daily_cases': 'sum',
                'New_daily_deaths': 'sum'
            }).reset_index()
            
            weekly_aggs = weekly_aggs.rename(columns={
                'New_daily_cases': 'New_weekly_cases',
                'New_daily_deaths': 'New_weekly_deaths'
            })
            
            # Merge weekly metrics back into daily data
            df = pd.merge(
                df, 
                weekly_aggs[['Country', 'Date_reported', 'New_weekly_cases', 'New_weekly_deaths']], 
                how='left', 
                on=['Country', 'Date_reported']
            )
        else:
            # Weekly metrics
            df['New_weekly_cases'] = df.groupby('Country')['Cumulative_cases'].diff().fillna(0)
            df['New_weekly_deaths'] = df.groupby('Country')['Cumulative_deaths'].diff().fillna(0)
            
            # Add placeholder columns for UI consistency
            df['New_daily_cases'] = np.nan
            df['New_daily_deaths'] = np.nan
        
        # Fix negative values
        for col in ['New_daily_cases', 'New_daily_deaths', 'New_weekly_cases', 'New_weekly_deaths']:
            if col in df.columns:
                df[col] = df[col].clip(lower=0)
        
        # Calculate mortality rate
        df['Mortality_rate'] = (df['Cumulative_deaths'] / df['Cumulative_cases'] * 100).round(2)
        df['Mortality_rate'] = df['Mortality_rate'].fillna(0).replace([np.inf, -np.inf], 0)
        
        # Calculate load time for performance monitoring
        load_time = time.time() - start_time
        return df, load_time
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), 0

#####################
# --- SIDEBAR ----
#####################
with st.sidebar:
    # ---- Modern Sidebar Header with Logo and Title (reverted to original icon and normal text) ----
    st.markdown(
        """
        <div class="sidebar-header">
            <div class="sidebar-logo">
                <img src="https://cdn-icons-png.flaticon.com/512/2913/2913465.png" width="50" height="50" style="object-fit:contain;"/>
            </div>
            <div class="sidebar-title">
                COVID-19 Analytics Hub<br>
                <span style="font-size:0.96rem; font-weight:400; color:#6ea8fe; letter-spacing:0.01em;">by Manjot Singh</span>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    # --- Dataset Selection in Card ---
    with st.container():
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("#### Dataset Selection")
        dataset_type = st.radio(
            "Select Dataset Type",
            ["Daily", "Weekly"],
            horizontal=True,
            help="Daily data provides more granular analysis, weekly data offers summarized trends."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Data Loading Spinner ---
    with st.spinner('Loading and processing data...'):
        covid_data, load_time = load_data(dataset_type.lower())
    st.caption(f"Data loaded in {load_time:.2f} seconds")

    # --- Filters in Card Panels ---
    if not covid_data.empty:
        # Date range
        min_date = covid_data['Date_reported'].min().date()
        max_date = covid_data['Date_reported'].max().date()
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("#### Date Range")
        date_range = st.date_input(
            "Select period:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range
        start_date_ts = pd.Timestamp(start_date)
        end_date_ts = pd.Timestamp(end_date)
        st.markdown('</div>', unsafe_allow_html=True)

        # Geographic filters
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("#### Geographic Filters")
        all_regions = sorted(covid_data['WHO_region'].unique())
        region_filter = st.multiselect(
            "WHO Region",
            options=all_regions,
            default=all_regions,
            help="Filter by WHO region(s)"
        )
        if region_filter:
            country_options = sorted(covid_data[covid_data['WHO_region'].isin(region_filter)]['Country'].unique())
        else:
            country_options = sorted(covid_data['Country'].unique())
        country_filter = st.multiselect(
            "Country",
            options=country_options,
            default=[],
            help="Filter by specific countries (optional)"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Data view options
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("#### Data View")
        if dataset_type == "Daily":
            view_options = st.radio(
                "Metric Type",
                options=["Cumulative", "Daily New", "Weekly New"],
                horizontal=True
            )
        else:
            view_options = st.radio(
                "Metric Type",
                options=["Cumulative", "Weekly New"],
                horizontal=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # Visualization options
        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        st.markdown("#### Visualization Options")
        log_scale = st.checkbox("Use Log Scale", value=True, help="Better for comparing values of different magnitudes")
        show_trends = st.checkbox("Show Trend Lines", value=True, help="Display moving averages")
        with st.expander("Advanced Options", expanded=False):
            animation_speed = st.slider("Animation Speed", 100, 1000, 300, step=100, 
                                       help="Speed of map animations in milliseconds")
            map_style = st.selectbox(
                "Map Style", 
                ["auto", "light", "dark", "satellite"], 
                index=0,
                help="Visual theme for map displays"
            )
            color_theme = st.selectbox(
                "Color Theme", 
                ["Viridis", "Plasma", "Inferno", "Turbo"], 
                index=1,
                help="Color scale for visualizations"
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # Reset filters button
        if st.button("🔄 Reset Filters", help="Reset all sidebar filters to default values."):
            st.experimental_rerun()

        # Apply filters
        with st.spinner('Applying filters...'):
            filtered = covid_data[
                (covid_data['Date_reported'] >= start_date_ts) &
                (covid_data['Date_reported'] <= end_date_ts)
            ]
            if region_filter:
                filtered = filtered[filtered['WHO_region'].isin(region_filter)]
            if country_filter:
                filtered = filtered[filtered['Country'].isin(country_filter)]

        # --- Download Section as Card Panel ---
        if not filtered.empty:
            st.markdown('<div class="sidebar-download-card">', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-download-header">📥 Download Full Analytics Report</div>', unsafe_allow_html=True)
            # CSV
            csv_data = filtered.to_csv(index=False)
            # Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                filtered.to_excel(writer, sheet_name="Filtered Data", index=False)
            excel_buffer.seek(0)
            # JSON
            json_data = filtered.to_json(orient='records')
            # PDF report (using reportlab and map snapshot if available)
            pdf_buffer = None
            if canvas is not None:
                pdf_buffer = io.BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=letter)
                width, height = letter
                c.setFont("Helvetica-Bold", 24)
                c.drawCentredString(width/2, height-100, "COVID-19 Analytics Report")
                c.setFont("Helvetica", 14)
                c.drawCentredString(width/2, height-130, f"Author: Manjot Singh")
                c.drawCentredString(width/2, height-150, f"Date Range: {start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}")
                c.showPage()
                c.setFont("Helvetica-Bold", 20)
                c.drawString(50, height-50, "Key Metrics")
                global_cases = int(filtered['Cumulative_cases'].sum())
                global_deaths = int(filtered['Cumulative_deaths'].sum())
                affected_countries = filtered['Country'].nunique()
                c.setFont("Helvetica", 12)
                c.drawString(50, height-80, f"Affected Countries: {affected_countries}")
                c.drawString(50, height-100, f"Total Cases: {global_cases:,}")
                c.drawString(50, height-120, f"Total Deaths: {global_deaths:,}")
                if 'fig_map' in locals() and kaleido is not None:
                    tmp_map_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                    fig_map.write_image(tmp_map_path, engine="kaleido")
                    c.drawImage(tmp_map_path, 50, height-400, width=500, preserveAspectRatio=True)
                c.showPage()
                c.save()
                pdf_buffer.seek(0)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.download_button("📥 CSV", data=csv_data, file_name="covid_full_analysis.csv", mime="text/csv")
            with col2:
                st.download_button("📊 Excel", data=excel_buffer, file_name="covid_full_analysis.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            with col3:
                st.download_button("🔄 JSON", data=json_data, file_name="covid_full_analysis.json", mime="application/json")
            with col4:
                if pdf_buffer is not None:
                    st.download_button("📄 PDF Report", data=pdf_buffer, file_name="covid_full_analysis_report.pdf", mime="application/pdf")
            st.markdown('</div>', unsafe_allow_html=True)


# ---------- MAIN CONTENT ----------
# Header section with dynamic title based on selected dataset
st.markdown(f"""
<h1>COVID-19 Global Dashboard</h1>
<div class='subtitle'>Analyzing <b>{dataset_type}</b> data from <b>{start_date.strftime('%b %d, %Y')}</b> to <b>{end_date.strftime('%b %d, %Y')}</b></div>
""", unsafe_allow_html=True)

# Progress indicator while page elements load
progress_bar = st.progress(0)
    
# Latest date for metrics
latest_date = filtered['Date_reported'].max()

# Check if we have data after filtering
if filtered.empty:
    st.warning("No data available with the current filter settings. Please adjust your filters.")
    st.stop()

# Update progress
progress_bar.progress(20)

# ---------- KEY PERFORMANCE INDICATORS ----------
# Extract latest metrics
latest = filtered[filtered['Date_reported'] == latest_date]
global_cases = int(latest['Cumulative_cases'].sum())
global_deaths = int(latest['Cumulative_deaths'].sum())
affected_countries = filtered['Country'].nunique()

# Calculate changes from previous period
previous_date = filtered[filtered['Date_reported'] < latest_date]['Date_reported'].max()
if pd.notna(previous_date):
    previous = filtered[filtered['Date_reported'] == previous_date]
    case_change = global_cases - int(previous['Cumulative_cases'].sum())
    death_change = global_deaths - int(previous['Cumulative_deaths'].sum())
    case_percent = (case_change / int(previous['Cumulative_cases'].sum()) * 100) if int(previous['Cumulative_cases'].sum()) > 0 else 0
    death_percent = (death_change / int(previous['Cumulative_deaths'].sum()) * 100) if int(previous['Cumulative_deaths'].sum()) > 0 else 0
else:
    case_change = death_change = case_percent = death_percent = 0

# Calculate new cases based on view option
if view_options == "Daily New" and dataset_type == "Daily":
    new_metric = 'New_daily_cases'
    new_deaths = 'New_daily_deaths'
    period = "Daily"
else:
    new_metric = 'New_weekly_cases'
    new_deaths = 'New_weekly_deaths'
    period = "Weekly"
    
new_cases = int(latest[new_metric].sum())
new_deaths = int(latest[new_deaths].sum())

# Calculate mortality rate
avg_mortality = (global_deaths / global_cases * 100) if global_cases > 0 else 0

# Update progress
progress_bar.progress(30)

# Display KPI cards with enhanced styling (modern, pastel, large)
st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
# Wide rectangular cards for all KPIs (including new weekly cases and mortality)
st.markdown(f'''
<div class="metric-card-wide affected" style="margin-right:0.5rem;">
    <div class="metric-value">{affected_countries:,}</div>
    <div class="metric-label">Affected Countries</div>
</div>
''', unsafe_allow_html=True)
case_class = "kpi-positive" if case_change >= 0 else "kpi-negative"
case_symbol = "+" if case_change >= 0 else ""
st.markdown(f'''
<div class="metric-card-wide cases" style="margin-right:0.5rem;">
    <div class="metric-value">{global_cases:,}</div>
    <div class="metric-label">Total Cases</div>
    <span class="metric-change {case_class}">{case_symbol}{case_change:,} ({case_percent:.1f}%)</span>
</div>
''', unsafe_allow_html=True)
death_class = "kpi-negative" if death_change >= 0 else "kpi-positive"
death_symbol = "+" if death_change >= 0 else ""
st.markdown(f'''
<div class="metric-card-wide deaths" style="margin-right:0.5rem;">
    <div class="metric-value">{global_deaths:,}</div>
    <div class="metric-label">Total Deaths</div>
    <span class="metric-change {death_class}">{death_symbol}{death_change:,} ({death_percent:.1f}%)</span>
</div>
''', unsafe_allow_html=True)
st.markdown(f'''
<div class="metric-card-wide active" style="margin-right:0.5rem;">
    <div class="metric-value">{new_cases:,}</div>
    <div class="metric-label">New {period} Cases</div>
</div>
''', unsafe_allow_html=True)
st.markdown(f'''
<div class="metric-card-wide mortality">
    <div class="metric-value">{avg_mortality:.2f}%</div>
    <div class="metric-label">Mortality Rate</div>
</div>
''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Display last updated badge (modern style)
st.markdown(f'''
<div class="data-badge">
    <div class="loading"></div> Last updated: {latest_date.strftime("%B %d, %Y")}
</div>
''', unsafe_allow_html=True)

# Update progress
progress_bar.progress(40)

# ---------- ENHANCED TAB NAVIGATION ----------
tab_icons = {
    "map": "🗺️",
    "countries": "📊",
    "trends": "📈",
    "regional": "🌐",
    "explorer": "🔍",
    "data": "📋"
}

# Create modern tab navigation
tabs = st.tabs([
    f"{tab_icons['map']} Animated Map",
    f"{tab_icons['countries']} Top Countries",
    f"{tab_icons['trends']} Trends",
    f"{tab_icons['regional']} Regional Analysis",
    f"{tab_icons['explorer']} Explorer",
    f"{tab_icons['data']} Data Table",
    "🧠 Forecasting (AI Predictions)",
    "📊 Statistical Insights",
    "💉 Vaccination vs Mortality",
    "📄 Report Export"
])

# ---------- ANIMATED MAP TAB ----------
with tabs[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Global COVID-19 Spread")
    
    # Create map data
    map_data = filtered.copy()
    map_data['date'] = map_data['Date_reported'].dt.strftime('%m/%d/%Y')
    
    # Determine metrics based on view option
    if view_options == "Cumulative":
        map_metric = "Cumulative_cases"
        map_deaths = "Cumulative_deaths"
        title_metric = "Cumulative Cases"
    elif view_options == "Daily New" and dataset_type == "Daily":
        map_metric = "New_daily_cases"
        map_deaths = "New_daily_deaths"
        title_metric = "New Daily Cases"
    else:  # Weekly New
        map_metric = "New_weekly_cases"
        map_deaths = "New_weekly_deaths"
        title_metric = "New Weekly Cases"
    
    # Make bubble sizes more visually appealing
    map_data['size'] = map_data[map_metric].clip(lower=1).pow(0.3)
    
    # Get ordered dates for animation
    ordered_dates = sorted(map_data['date'].unique(), key=lambda x: pd.to_datetime(x, format='%m/%d/%Y'))
    
    # Sample dates to reduce frame count for smoother animations
    if len(ordered_dates) > 30:
        sample_step = len(ordered_dates) // 30
        sampled_dates = ordered_dates[::sample_step]
        if ordered_dates[-1] not in sampled_dates:
            sampled_dates.append(ordered_dates[-1])
    else:
        sampled_dates = ordered_dates
    
    # Create map with selected color theme
    # --- Pastel color scales for map (unified pastel) ---
    pastel_map_scales = {
        "Cumulative Cases": ["#eaf1ff", "#b4d8fe", "#6ea8fe"],  # blue pastel
        "New Daily Cases": ["#fff6e8", "#ffe1b4", "#ffb86c"],    # orange pastel
        "New Weekly Cases": ["#fff6e8", "#ffe1b4", "#ffb86c"],   # orange pastel
    }
    if title_metric == "Cumulative Cases":
        map_color_scale = ["#eaf1ff", "#b4d8fe", "#6ea8fe"]
    elif "New Daily" in title_metric:
        map_color_scale = ["#ffe1fa", "#eabfff", "#b39ddb", "#ffd6f9", "#f6eaff"]
    else:
        map_color_scale = ["#fff6e8", "#ffe1b4", "#ffb86c", "#ffd6f9", "#eabfff"]
    fig_map = px.scatter_geo(
        map_data,
        locations="Country",
        locationmode='country names',
        color=map_metric,
        size='size',
        hover_name="Country",
        hover_data={
            map_metric: True,
            map_deaths: True,
            "Mortality_rate": True,
            "size": False
        },
        projection="natural earth",
        animation_frame="date",
        title=f'COVID-19: {title_metric} Over Time',
        color_continuous_scale=map_color_scale,
        range_color=[0, map_data[map_metric].quantile(0.95)]  # Use 95th percentile for better contrast
    )
    
    # Determine if we should use dark mode for map
    # Use Streamlit's config to determine if we're in dark mode
    is_dark_theme = st.get_option("theme.base") == "dark"
    
    # Set map styling based on user selection or theme
    if map_style == "dark" or (map_style == "auto" and is_dark_theme):
        bgcolor = "rgba(30,30,40,0.95)"
        landcolor = "#252c36"
        oceancolor = "#121418"
        textcolor = "white"
        template = "plotly_dark"
    elif map_style == "light" or (map_style == "auto" and not is_dark_theme):
        bgcolor = "rgba(240,242,246,0.95)"
        landcolor = "#ebedf0"
        oceancolor = "#f7f8fa"
        textcolor = "black"
        template = "plotly_white"
    else:  # satellite
        bgcolor = "rgba(30,30,40,0.95)"
        landcolor = "#3b3b3b"
        oceancolor = "#111111"
        textcolor = "white"
        template = "plotly_dark"
    
    # Enhance map appearance
    fig_map.update_layout(
        template=template,
        paper_bgcolor=bgcolor,
        geo=dict(
            showland=True,
            landcolor=landcolor,
            showocean=True,
            oceancolor=oceancolor,
            showcountries=True,
            countrycolor="#666666",
            showcoastlines=False,
            projection_type="natural earth",
            showframe=False
        ),
        height=620,
        updatemenus=[{
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": animation_speed, "redraw": True}, "fromcurrent": True}],
                    "label": "▶",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
                    "label": "■",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 10},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "y": 0,
            "bgcolor": "rgba(100,100,100,0.5)",
            "font": {"color": textcolor}
        }],
        sliders=[{
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {
                "font": {"size": 16, "color": textcolor},
                "prefix": "Date: ",
                "visible": True,
                "xanchor": "right"
            },
            "transition": {"duration": animation_speed},
            "pad": {"b": 10, "t": 50},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": [
                {
                    "args": [
                        [date],
                        {"frame": {"duration": animation_speed, "redraw": True}, "mode": "immediate"}
                    ],
                    "label": date,
                    "method": "animate"
                } for date in sampled_dates  # Use sampled dates for better performance
            ]
        }]
    )
    
    # Only create frames for sampled dates to improve performance
    map_data_sampled = map_data[map_data['date'].isin(sampled_dates)]
    fig_map.frames = [
        go.Frame(
            data=[go.Scattergeo(
                locations=map_data_sampled[map_data_sampled['date'] == date]['Country'],
                locationmode='country names',
                marker=dict(
                    size=map_data_sampled[map_data_sampled['date'] == date]['size'],
                    color=map_data_sampled[map_data_sampled['date'] == date][map_metric],
                    colorscale=map_color_scale,
                    colorbar=dict(title=map_metric),
                    cmin=0,
                    cmax=map_data[map_metric].quantile(0.95)
                )
            )],
            name=date
        )
        for date in sampled_dates
    ]
    
    # Render map with loading indicator
    with st.spinner("Rendering map..."):
        st.plotly_chart(fig_map, use_container_width=True)
    
    st.info("💡 **Pro Tip:** Use the play button to animate the map through time, or click on specific dates in the slider to jump to that point.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Update progress
progress_bar.progress(60)
    
# ---------- TOP COUNTRIES TAB ----------
with tabs[1]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Top Countries Analysis")
    
    # Get metrics based on selected view
    if view_options == "Cumulative":
        top_metrics = ['Cumulative_cases', 'Cumulative_deaths']
        title_prefix = "Cumulative"
    elif view_options == "Daily New" and dataset_type == "Daily":
        top_metrics = ['New_daily_cases', 'New_daily_deaths']
        title_prefix = "New Daily"
    else:  # Weekly New
        top_metrics = ['New_weekly_cases', 'New_weekly_deaths']
        title_prefix = "New Weekly"
        
    # Get data for the latest date for each country
    latest_by_country = filtered.sort_values('Date_reported').groupby('Country').last().reset_index()
    
    # Find top 10 countries by cases
    top_by_cases = latest_by_country.sort_values(top_metrics[0], ascending=False).head(10)
    top_by_cases['Mortality_rate'] = (top_by_cases['Cumulative_deaths'] / top_by_cases['Cumulative_cases'] * 100).round(2)
    
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
    # Enhanced bar chart for cases
    # Unified pastel blue for cases
        fig_topcases = px.bar(
        top_by_cases,
        x='Country',
        y=top_metrics[0],
        color=top_metrics[0],
        color_continuous_scale=["#eaf1ff", "#b4d8fe", "#6ea8fe"],
        title=f"Top 10 Countries by {title_prefix} Cases",
        log_y=log_scale,
        text=top_metrics[0],
        height=450
    )
        
        fig_topcases.update_layout(
            xaxis_title="",
            yaxis_title=f"{title_prefix} Case Count",
            coloraxis_showscale=False,
            margin=dict(l=40, r=20, t=40, b=40),
        )
        
        # Format the value labels
        fig_topcases.update_traces(
            texttemplate='%{y:,.0f}',
            textposition='outside',
            textfont_size=10,
            hovertemplate='<b>%{x}</b><br>Cases: %{y:,.0f}<extra></extra>'
        )
        
        st.plotly_chart(fig_topcases, use_container_width=True)
        
    with col_top2:
        # Enhanced bar chart for deaths
        # Unified pastel red for deaths
        fig_topdeaths = px.bar(
            top_by_cases,
            x='Country',
            y=top_metrics[1],
            color=top_metrics[1],
            color_continuous_scale=["#fff0f0", "#ffc9c9", "#ff7b7b"],
            title=f"{title_prefix} Deaths in Top 10 Case Countries",
            log_y=log_scale,
            text=top_metrics[1],
            height=450
        )
        
        fig_topdeaths.update_layout(
            xaxis_title="",
            yaxis_title=f"{title_prefix} Death Count",
            coloraxis_showscale=False,
            margin=dict(l=40, r=20, t=40, b=40),
        )
        
        # Format the value labels
        fig_topdeaths.update_traces(
            texttemplate='%{y:,.0f}',
            textposition='outside',
            textfont_size=10,
            hovertemplate='<b>%{x}</b><br>Deaths: %{y:,.0f}<extra></extra>'
        )
        
        st.plotly_chart(fig_topdeaths, use_container_width=True)
    
    # Create mortality rate visualization
    st.subheader("Mortality Rate Analysis")
    
    # Create scatter plot comparing cases, deaths and mortality rate
    # Unified pastel purple for mortality rate
    fig_scatter = px.scatter(
        top_by_cases,
        x='Cumulative_cases',
        y='Cumulative_deaths',
        color='Mortality_rate',
        size='Mortality_rate',
        hover_name='Country',
        text='Country',
        log_x=log_scale,
        log_y=log_scale,
        title="Case-Death Relationship & Mortality Rate",
        color_continuous_scale=["#f6eaff", "#e2d3fd", "#b39ddb", "#ffd6f9", "#eabfff"],
        height=500
    )
    
    fig_scatter.update_layout(
        xaxis_title="Total Cases",
        yaxis_title="Total Deaths",
        coloraxis_colorbar=dict(title="Mortality Rate (%)"),
        hovermode='closest'
    )
    
    fig_scatter.update_traces(
        textposition='top center',
        marker=dict(sizemin=5, sizeref=0.1),
        hovertemplate='<b>%{hovertext}</b><br>Cases: %{x:,.0f}<br>Deaths: %{y:,.0f}<br>Mortality: %{marker.color:.2f}%<extra></extra>'
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Mortality rate bar chart
    fig_mortality = px.bar(
        top_by_cases.sort_values('Mortality_rate', ascending=False),
        x='Country',
        y='Mortality_rate',
        color='Mortality_rate',
        color_continuous_scale=["#f6eaff", "#e2d3fd", "#b39ddb", "#ffd6f9", "#eabfff"],
        title="Mortality Rate (%) in Top 10 Countries",
        text='Mortality_rate',
        height=450
    )
    
    fig_mortality.update_layout(
        xaxis_title="",
        yaxis_title="Mortality Rate (%)",
        coloraxis_showscale=False
    )
    
    fig_mortality.update_traces(
        texttemplate='%{y:.2f}%',
        textposition='outside',
        textfont_size=10,
        hovertemplate='<b>%{x}</b><br>Mortality Rate: %{y:.2f}%<extra></extra>'
    )
    
    st.plotly_chart(fig_mortality, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Update progress
progress_bar.progress(70)

# ---------- TRENDS TAB ----------
with tabs[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Global Trends Over Time")
    
    # Create timeline data - optimize by grouping first
    timeline_metrics = {
        'Cumulative_cases': 'sum',
        'Cumulative_deaths': 'sum',
    }
    
    # Add appropriate metrics based on dataset type
    if dataset_type == "Daily":
        timeline_metrics.update({
            'New_daily_cases': 'sum',
            'New_daily_deaths': 'sum',
            'New_weekly_cases': 'sum',
            'New_weekly_deaths': 'sum'
        })
    else:
        timeline_metrics.update({
            'New_weekly_cases': 'sum',
            'New_weekly_deaths': 'sum'
        })
    
    # Calculate aggregates more efficiently
    with st.spinner("Calculating trends..."):
        timeline = filtered.groupby('Date_reported').agg(timeline_metrics).reset_index()
        timeline = timeline.sort_values('Date_reported')
    
    # Calculate moving averages for trend lines if enabled
    if show_trends:
        window_size = 7 if dataset_type == "Daily" else 4
        if len(timeline) >= window_size:
            if dataset_type == "Daily" and 'New_daily_cases' in timeline.columns:
                timeline['Cases_MA'] = timeline['New_daily_cases'].rolling(window=window_size, min_periods=1).mean()
                timeline['Deaths_MA'] = timeline['New_daily_deaths'].rolling(window=window_size, min_periods=1).mean()
            
            if 'New_weekly_cases' in timeline.columns:
                timeline['Weekly_Cases_MA'] = timeline['New_weekly_cases'].rolling(window=min(window_size, len(timeline)//2 or 1), min_periods=1).mean()
                timeline['Weekly_Deaths_MA'] = timeline['New_weekly_deaths'].rolling(window=min(window_size, len(timeline)//2 or 1), min_periods=1).mean()
    
    # Create interactive time series charts based on view options
    if view_options == "Cumulative":
        # Cumulative cases and deaths chart
        fig_cumulative = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add traces with attractive styling
        # Soft blue pastel for cases, soft red pastel for deaths
        fig_cumulative.add_trace(
            go.Scatter(
                x=timeline['Date_reported'], 
                y=timeline['Cumulative_cases'],
                name="Total Cases",
                line=dict(color="#6ea8fe", width=3, shape='spline'),
                fill='tozeroy',
                fillcolor='rgba(110,168,254,0.18)'
            )
        )
        fig_cumulative.add_trace(
            go.Scatter(
                x=timeline['Date_reported'], 
                y=timeline['Cumulative_deaths'],
                name="Total Deaths",
                line=dict(color="#ff7b7b", width=3, shape='spline'),
                fill='tozeroy',
                fillcolor='rgba(255,123,123,0.18)'
            ),
            secondary_y=True
        )
        
        # Update layout with modern styling
        fig_cumulative.update_layout(
            title=f"Cumulative Cases and Deaths ({dataset_type} Data)",
            height=500,
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        # Update axes
        fig_cumulative.update_yaxes(
            title_text="Cumulative Cases", 
            secondary_y=False,
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
            type='linear' if not log_scale else 'log'
        )
        fig_cumulative.update_yaxes(
            title_text="Cumulative Deaths", 
            secondary_y=True,
            showgrid=False,
            type='linear' if not log_scale else 'log'
        )
        fig_cumulative.update_xaxes(
            title_text="Date",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
        )
        
        # Add hover template for better interaction
        fig_cumulative.update_traces(
            hovertemplate='<b>%{x|%B %d, %Y}</b><br>%{y:,.0f}<extra>%{fullData.name}</extra>'
        )
        
        st.plotly_chart(fig_cumulative, use_container_width=True)
        
    elif view_options == "Daily New" and dataset_type == "Daily":
        # Daily new cases and deaths chart
        fig_daily = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add bar traces for new cases and deaths
        # Soft orange/green pastel for new cases/deaths
        fig_daily.add_trace(
            go.Bar(
                x=timeline['Date_reported'], 
                y=timeline['New_daily_cases'],
                name="New Daily Cases",
                marker_color='rgba(255,184,108,0.7)'
            )
        )
        fig_daily.add_trace(
            go.Bar(
                x=timeline['Date_reported'], 
                y=timeline['New_daily_deaths'],
                name="New Daily Deaths",
                marker_color='rgba(126,217,110,0.7)'
            ),
            secondary_y=True
        )
        
        # Add trend lines if enabled
        if show_trends and 'Cases_MA' in timeline.columns:
            fig_daily.add_trace(
                go.Scatter(
                    x=timeline['Date_reported'], 
                    y=timeline['Cases_MA'],
                    name="Cases Trend (7-day MA)",
                    line=dict(color="#6ea8fe", width=3, dash='solid')
                )
            )
            fig_daily.add_trace(
                go.Scatter(
                    x=timeline['Date_reported'], 
                    y=timeline['Deaths_MA'],
                    name="Deaths Trend (7-day MA)",
                    line=dict(color="#7ed96e", width=3, dash='solid')
                ),
                secondary_y=True
            )
        
        # Update layout
        fig_daily.update_layout(
            title="Daily New Cases and Deaths",
            height=500,
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        # Update axes
        fig_daily.update_yaxes(
            title_text="New Daily Cases", 
            secondary_y=False,
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
            type='linear' if not log_scale else 'log'
        )
        fig_daily.update_yaxes(
            title_text="New Daily Deaths", 
            secondary_y=True,
            showgrid=False,
            type='linear' if not log_scale else 'log'
        )
        fig_daily.update_xaxes(
            title_text="Date",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
        )
        
        # Add hover template
        fig_daily.update_traces(
            hovertemplate='<b>%{x|%B %d, %Y}</b><br>%{y:,.0f}<extra>%{fullData.name}</extra>'
        )
        
        st.plotly_chart(fig_daily, use_container_width=True)
    
    else:  # Weekly New (available in both dataset types)
        # Weekly new cases and deaths chart
        fig_weekly = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add bar traces for new cases and deaths
        fig_weekly.add_trace(
            go.Bar(
                x=timeline['Date_reported'], 
                y=timeline['New_weekly_cases'],
                name="New Weekly Cases",
                marker_color='rgba(255,184,108,0.7)'
            )
        )
        fig_weekly.add_trace(
            go.Bar(
                x=timeline['Date_reported'], 
                y=timeline['New_weekly_deaths'],
                name="New Weekly Deaths",
                marker_color='rgba(126,217,110,0.7)'
            ),
            secondary_y=True
        )
        
        # Add trend lines if enabled
        if show_trends and 'Weekly_Cases_MA' in timeline.columns:
            fig_weekly.add_trace(
                go.Scatter(
                    x=timeline['Date_reported'], 
                    y=timeline['Weekly_Cases_MA'],
                    name="Cases Trend (4-wk MA)",
                    line=dict(color="#6ea8fe", width=3, dash='solid')
                )
            )
            fig_weekly.add_trace(
                go.Scatter(
                    x=timeline['Date_reported'], 
                    y=timeline['Weekly_Deaths_MA'],
                    name="Deaths Trend (4-wk MA)",
                    line=dict(color="#7ed96e", width=3, dash='solid')
                ),
                secondary_y=True
            )
        
        # Update layout
        fig_weekly.update_layout(
            title=f"Weekly New Cases and Deaths ({dataset_type} Data)",
            height=500,
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        
        # Update axes
        fig_weekly.update_yaxes(
            title_text="New Weekly Cases", 
            secondary_y=False,
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
            type='linear' if not log_scale else 'log'
        )
        fig_weekly.update_yaxes(
            title_text="New Weekly Deaths", 
            secondary_y=True,
            showgrid=False,
            type='linear' if not log_scale else 'log'
        )
        fig_weekly.update_xaxes(
            title_text="Date",
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.2)',
        )
        
        # Add hover template
        fig_weekly.update_traces(
            hovertemplate='<b>%{x|%B %d, %Y}</b><br>%{y:,.0f}<extra>%{fullData.name}</extra>'
        )
        
        st.plotly_chart(fig_weekly, use_container_width=True)
    
    # Create a stacked area chart for cases by WHO region
    st.subheader("Regional Breakdown Over Time")
    
    # More efficient data aggregation for regions
    with st.spinner("Calculating regional breakdown..."):
        region_metrics = {
            'Cumulative_cases': 'sum',
            'Cumulative_deaths': 'sum',
            'New_weekly_cases': 'sum',
            'New_weekly_deaths': 'sum'
        }
        
        if dataset_type == "Daily":
            region_metrics.update({
                'New_daily_cases': 'sum',
                'New_daily_deaths': 'sum'
            })
            
        region_timeline = filtered.groupby(['Date_reported', 'WHO_region']).agg(region_metrics).reset_index()
    
    # Select metric based on view options
    if view_options == "Cumulative":
        region_metric = "Cumulative_cases"
        region_title = "Cumulative Cases by WHO Region"
    elif view_options == "Daily New" and dataset_type == "Daily":
        region_metric = "New_daily_cases"
        region_title = "New Daily Cases by WHO Region"
    else:  # Weekly New
        region_metric = "New_weekly_cases"
        region_title = "New Weekly Cases by WHO Region"
    
    # Create enhanced area chart
    # Pastel color palette for WHO regions (unified pastel)
    pastel_region_palette = ['#b4d8fe', '#ffc9c9', '#b9f6c3', '#ffe1b4', '#e2d3fd', '#ffd6f9', '#eabfff']
    fig_region_area = px.area(
        region_timeline,
        x='Date_reported',
        y=region_metric,
        color='WHO_region',
        title=region_title,
        color_discrete_sequence=pastel_region_palette,
        log_y=log_scale,
        height=500
    )
    
    fig_region_area.update_layout(
        xaxis_title="Date",
        yaxis_title=region_title.replace(" by WHO Region", ""),
        hovermode="x unified",
        legend_title="WHO Region",
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="left", x=0),
    )
    
    # Add hover template
    fig_region_area.update_traces(
        hovertemplate='<b>%{x|%B %d, %Y}</b><br>%{y:,.0f}<extra>%{fullData.name}</extra>'
    )
    
    st.plotly_chart(fig_region_area, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Update progress
progress_bar.progress(80)

# ---------- REGIONAL ANALYSIS TAB ----------
with tabs[3]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("WHO Regional Analysis")
    
    # Calculate region summary - more efficiently
    with st.spinner("Analyzing regional data..."):
        region_summary_metrics = {
            'Country': 'nunique',
            'Cumulative_cases': 'sum',
            'Cumulative_deaths': 'sum',
            'New_weekly_cases': 'sum',
            'New_weekly_deaths': 'sum'
        }
        
        if dataset_type == "Daily":
            region_summary_metrics.update({
                'New_daily_cases': 'sum',
                'New_daily_deaths': 'sum'
            })
            
        region_summary = filtered[filtered['Date_reported']==latest_date].groupby('WHO_region').agg(
            region_summary_metrics
        ).reset_index().rename(columns={'Country': 'Countries'})
        
        region_summary['Mortality_rate'] = (region_summary['Cumulative_deaths'] / region_summary['Cumulative_cases'] * 100).round(2)
        region_summary = region_summary.sort_values('Cumulative_cases', ascending=False)
    
    # Create continent mapping
    continent_mapping = {
        'AMRO': 'Americas',
        'EURO': 'Europe',
        'AFRO': 'Africa',
        'EMRO': 'Eastern Mediterranean',
        'WPRO': 'Western Pacific',
        'SEARO': 'South-East Asia',
        'OTHER': 'Other'
    }
    
    # Regional pie charts
    col_reg1, col_reg2 = st.columns(2)
    
    with col_reg1:
        # Determine metric for cases pie chart
        if view_options == "Cumulative":
            pie_metric = "Cumulative_cases"
            pie_title = "Distribution of Cases by WHO Region"
        elif view_options == "Daily New" and dataset_type == "Daily":
            pie_metric = "New_daily_cases"
            pie_title = "Distribution of New Daily Cases by WHO Region"
        else:  # Weekly New
            pie_metric = "New_weekly_cases"
            pie_title = "Distribution of New Weekly Cases by WHO Region"
        
        # Enhanced pie chart for cases
        # Pastel region palette for pie
        fig_reg_cases = px.pie(
            region_summary,
            values=pie_metric,
            names='WHO_region',
            title=pie_title,
            color='WHO_region',
            color_discrete_sequence=pastel_region_palette,
            hole=0.4
        )
        
        fig_reg_cases.update_layout(
            height=450,
            legend_title="WHO Region"
        )
        
        fig_reg_cases.update_traces(
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Cases: %{value:,.0f}<br>Share: %{percent}<extra></extra>'
        )
        
        st.plotly_chart(fig_reg_cases, use_container_width=True)
        
    with col_reg2:
        # Determine metric for deaths pie chart
        if view_options == "Cumulative":
            death_metric = "Cumulative_deaths"
            death_title = "Distribution of Deaths by WHO Region"
        elif view_options == "Daily New" and dataset_type == "Daily":
            death_metric = "New_daily_deaths"
            death_title = "Distribution of New Daily Deaths by WHO Region"
        else:  # Weekly New
            death_metric = "New_weekly_deaths"
            death_title = "Distribution of New Weekly Deaths by WHO Region"
        
        # Enhanced pie chart for deaths
        fig_reg_deaths = px.pie(
            region_summary,
            values=death_metric,
            names='WHO_region',
            title=death_title,
            color='WHO_region',
            color_discrete_sequence=pastel_region_palette,
            hole=0.4
        )
        
        fig_reg_deaths.update_layout(
            height=450,
            legend_title="WHO Region"
        )
        
        fig_reg_deaths.update_traces(
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Deaths: %{value:,.0f}<br>Share: %{percent}<extra></extra>'
        )
        
        st.plotly_chart(fig_reg_deaths, use_container_width=True)
    
    # Create treemap data with proper error handling
    st.subheader("Hierarchical View of COVID-19 Impact")
    
    # Prepare treemap data with careful handling of nulls
    with st.spinner("Preparing hierarchical visualization..."):
        try:
            # Get the latest data
            treemap_base = filtered[filtered['Date_reported'] == latest_date].copy()
            # Add continent information
            treemap_base['Continent'] = treemap_base['WHO_region'].map(continent_mapping)
            # Rename columns for visualization clarity
            treemap_data = treemap_base.rename(columns={
                'Country': 'Country_Name',
                'Cumulative_cases': 'Total_Cases',
                'Cumulative_deaths': 'Total_Deaths'
            })
            # Choose metrics based on view options
            if view_options == "Cumulative":
                treemap_metric = "Total_Cases"
                treemap_title = "Cumulative COVID-19 Cases"
            elif view_options == "Daily New" and dataset_type == "Daily":
                treemap_data['Daily_Cases'] = treemap_data['New_daily_cases']
                treemap_metric = "Daily_Cases"
                treemap_title = "New Daily COVID-19 Cases"
            else:  # Weekly New
                treemap_data['Weekly_Cases'] = treemap_data['New_weekly_cases']
                treemap_metric = "Weekly_Cases"
                treemap_title = "New Weekly COVID-19 Cases"

            # --- Null handling for treemap path columns and values ---
            treemap_data['Continent'] = treemap_data['Continent'].fillna('Other').astype(str)
            treemap_data['WHO_region'] = treemap_data['WHO_region'].fillna('Other').astype(str)
            treemap_data['Country_Name'] = treemap_data['Country_Name'].fillna('Unknown').astype(str)
            treemap_data[treemap_metric] = treemap_data[treemap_metric].fillna(0)
            # --------------------------------------------------------

            # Create treemap with error handling
            fig_treemap = px.treemap(
                treemap_data,
                path=['Continent', 'WHO_region', 'Country_Name'],
                values=treemap_metric,
                color='WHO_region',
                color_discrete_sequence=pastel_region_palette,
                title=f"{treemap_title} by Geographic Hierarchy ({dataset_type} Data)",
                height=600
            )
            fig_treemap.update_layout(
                margin=dict(l=0, r=0, t=30, b=0)
            )
            fig_treemap.update_traces(
                textinfo='label+value',
                hovertemplate='<b>%{label}</b><br>Cases: %{value:,.0f}<extra></extra>'
            )
            st.plotly_chart(fig_treemap, use_container_width=True)
        except Exception as e:
            st.error(f"Unable to create treemap visualization: {str(e)}")
            st.info("This is likely due to missing or inconsistent categorical data in your dataset.")
            # Fallback: Show a simpler visualization that doesn't rely on hierarchical paths
            st.subheader("Alternative Regional View")
            # Create a horizontal bar chart instead
            region_data = filtered[filtered['Date_reported'] == latest_date].groupby('WHO_region').agg({
                'Cumulative_cases': 'sum',
                'Cumulative_deaths': 'sum'
            }).reset_index().sort_values('Cumulative_cases')
            fig_bar = px.bar(
                region_data,
                y='WHO_region',
                x='Cumulative_cases',
                color='WHO_region',
                orientation='h',
                title="COVID-19 Cases by WHO Region",
                color_discrete_sequence=pastel_region_palette,
                height=500
            )
            fig_bar.update_layout(
                xaxis_title="Cumulative Cases",
                yaxis_title="WHO Region",
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Regional summary table with improved styling for both light and dark mode
    st.subheader("WHO Regional Summary")
    
    # Format the table
    formatted_summary = region_summary.copy()
    for col in formatted_summary.columns:
        if col in ['Cumulative_cases', 'Cumulative_deaths', 'New_weekly_cases', 'New_weekly_deaths']:
            formatted_summary[col] = formatted_summary[col].apply(lambda x: f"{int(x):,}")
        
        if dataset_type == "Daily" and col in ['New_daily_cases', 'New_daily_deaths']:
            formatted_summary[col] = formatted_summary[col].apply(lambda x: f"{int(x):,}")
            
    formatted_summary['Mortality_rate'] = formatted_summary['Mortality_rate'].apply(lambda x: f"{x:.2f}%")
    
    # Rename columns for better display
    rename_dict = {
        'Countries': 'Countries Affected',
        'Cumulative_cases': 'Total Cases',
        'Cumulative_deaths': 'Total Deaths',
        'New_weekly_cases': 'Weekly New Cases',
        'New_weekly_deaths': 'Weekly New Deaths',
        'Mortality_rate': 'Mortality Rate',
        'WHO_region': 'WHO Region'
    }
    
    if dataset_type == "Daily":
        rename_dict.update({
            'New_daily_cases': 'Daily New Cases',
            'New_daily_deaths': 'Daily New Deaths'
        })
    
    # Display the enhanced table
    st.dataframe(
        formatted_summary.rename(columns=rename_dict),
        use_container_width=True,
        height=300
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Update progress
progress_bar.progress(90)

# ---------- INTERACTIVE EXPLORER TAB ----------
with tabs[4]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Interactive Country Explorer")
    
    # Allow selecting specific countries to compare
    compare_countries = st.multiselect(
        "Select Countries to Compare",
        options=sorted(filtered['Country'].unique()),
        default=sorted(filtered['Country'].unique())[:5] if len(filtered['Country'].unique()) > 5 else sorted(filtered['Country'].unique()),
        help="Choose countries to compare (limit to 5-10 for better visualization)"
    )
    
    if not compare_countries:
        st.warning("Please select at least one country to explore.")
    else:
        # Get data for selected countries
        country_data = filtered[filtered['Country'].isin(compare_countries)].copy()
        
        # Determine metrics based on view options
        if view_options == "Cumulative":
            country_cases = 'Cumulative_cases'
            country_deaths = 'Cumulative_deaths'
            title_prefix = "Cumulative"
        elif view_options == "Daily New" and dataset_type == "Daily":
            country_cases = 'New_daily_cases'
            country_deaths = 'New_daily_deaths'
            title_prefix = "New Daily"
        else:  # Weekly New
            country_cases = 'New_weekly_cases'
            country_deaths = 'New_weekly_deaths'
            title_prefix = "New Weekly"
        
        # Line chart for selected countries with improved styling
        st.subheader(f"{title_prefix} Cases Comparison")
        
        # Pastel region palette for country lines
        fig_country_line = px.line(
            country_data,
            x='Date_reported',
            y=country_cases,
            color='Country',
            title=f"{title_prefix} Cases by Country",
            log_y=log_scale,
            color_discrete_sequence=pastel_region_palette,
            height=500
        )
        
        fig_country_line.update_layout(
            xaxis_title="Date",
            yaxis_title=f"{title_prefix} Cases",
            hovermode="x unified",
            legend_title="Country",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        # Add hover template
        fig_country_line.update_traces(
            hovertemplate='<b>%{x|%B %d, %Y}</b><br>%{y:,.0f}<extra>%{fullData.name}</extra>'
        )
        
        st.plotly_chart(fig_country_line, use_container_width=True)
        
        # Deaths comparison chart
        st.subheader(f"{title_prefix} Deaths Comparison")
        
        fig_country_deaths = px.line(
            country_data,
            x='Date_reported',
            y=country_deaths,
            color='Country',
            title=f"{title_prefix} Deaths by Country",
            log_y=log_scale,
            color_discrete_sequence=pastel_region_palette,
            height=500
        )
        
        fig_country_deaths.update_layout(
            xaxis_title="Date",
            yaxis_title=f"{title_prefix} Deaths",
            hovermode="x unified",
            legend_title="Country",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        # Add hover template
        fig_country_deaths.update_traces(
            hovertemplate='<b>%{x|%B %d, %Y}</b><br>%{y:,.0f}<extra>%{fullData.name}</extra>'
        )
        
        st.plotly_chart(fig_country_deaths, use_container_width=True)
        
        # Mortality rate over time
        st.subheader("Mortality Rate Over Time")
        
        # Calculate mortality rate over time
        mortality_data = country_data.copy()
        mortality_data['Mortality_rate'] = (mortality_data['Cumulative_deaths'] / mortality_data['Cumulative_cases'] * 100).round(2)
        mortality_data['Mortality_rate'] = mortality_data['Mortality_rate'].fillna(0).replace([np.inf, -np.inf], 0)
        
        fig_mortality_time = px.line(
            mortality_data,
            x='Date_reported',
            y='Mortality_rate',
            color='Country',
            title="Mortality Rate (%) Over Time",
            color_discrete_sequence=["#f6eaff", "#e2d3fd", "#b39ddb", "#ffd6f9", "#eabfff", "#d1c4e9", "#ede7f6", "#c3aed6"],
            height=500
        )
        
        fig_mortality_time.update_layout(
            xaxis_title="Date",
            yaxis_title="Mortality Rate (%)",
            hovermode="x unified",
            legend_title="Country",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        # Add hover template
        fig_mortality_time.update_traces(
            hovertemplate='<b>%{x|%B %d, %Y}</b><br>%{y:.2f}%<extra>%{fullData.name}</extra>'
        )
        
        st.plotly_chart(fig_mortality_time, use_container_width=True)
        
        # Create radar chart for multi-dimensional comparison
        st.subheader("Multi-dimensional Country Comparison")
        
        # Get the latest data for each selected country
        latest_country_data = country_data.groupby('Country').apply(lambda x: x[x['Date_reported'] == x['Date_reported'].max()]).reset_index(drop=True)
        
        # Normalize data for radar chart
        radar_data = latest_country_data.copy()
        normalized_cols = []
        
        # Choose columns to include based on dataset type
        if dataset_type == "Daily":
            radar_metrics = ['Cumulative_cases', 'Cumulative_deaths', 'New_daily_cases', 'New_daily_deaths', 'Mortality_rate']
            radar_labels = ['Total Cases', 'Total Deaths', 'New Daily Cases', 'New Daily Deaths', 'Mortality Rate']
        else:
            radar_metrics = ['Cumulative_cases', 'Cumulative_deaths', 'New_weekly_cases', 'New_weekly_deaths', 'Mortality_rate']
            radar_labels = ['Total Cases', 'Total Deaths', 'New Weekly Cases', 'New Weekly Deaths', 'Mortality Rate']
        
        # Perform normalization for each metric
        for col in radar_metrics:
            max_val = radar_data[col].max()
            if max_val > 0:  # Avoid division by zero
                radar_data[f'{col}_norm'] = (radar_data[col] / max_val) * 100
            else:
                radar_data[f'{col}_norm'] = 0
            normalized_cols.append(f'{col}_norm')
        
        # Create radar chart
        fig_radar = go.Figure()
        
        # Define colors for radar chart - unified pastel colors
        radar_colors = ['#6ea8fe', '#ffb86c', '#ff7b7b', '#7ed96e', '#b39ddb', '#b4d8fe', '#ffc9c9', '#ffd6f9', '#eabfff']
        for i, country in enumerate(radar_data['Country'].unique()):
            country_row = radar_data[radar_data['Country'] == country].iloc[0]
            fig_radar.add_trace(go.Scatterpolar(
                r=[country_row[f'{col}_norm'] for col in radar_metrics],
                theta=radar_labels,
                fill='toself',
                name=country,
                line_color=radar_colors[i % len(radar_colors)],
                fillcolor=hex_to_rgba(radar_colors[i % len(radar_colors)], 0.20)
            ))
        
        # Use neutral grid colors that work in both light and dark mode
        grid_color = "rgba(128, 128, 128, 0.2)"
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor=grid_color
                ),
                angularaxis=dict(
                    gridcolor=grid_color
                )
            ),
            showlegend=True,
            height=600,
            title=f"Multi-dimensional Country Comparison ({dataset_type} Data, Normalized to 100%)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        
        # Add subtle animation for radar chart
        st.plotly_chart(fig_radar, use_container_width=True, config={"staticPlot": False, "displayModeBar": False})
        st.caption("Note: All metrics are normalized relative to the maximum value across the selected countries.")
            
    st.markdown('</div>', unsafe_allow_html=True)

# Update progress
progress_bar.progress(95)

# ---------- DATA TABLE TAB ----------
with tabs[5]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Detailed Data Table & Export")
    # Add options for data display
    table_options = st.radio(
        "Choose data to display:",
        options=["All Data", "Latest Date Only", "Summary by Country", "Summary by WHO Region"],
        horizontal=True
    )
    # Prepare data based on selection
    with st.spinner("Preparing data table..."):
        if table_options == "All Data":
            display_data = filtered.sort_values(['Date_reported', 'Country'])
        elif table_options == "Latest Date Only":
            display_data = filtered[filtered['Date_reported'] == latest_date].sort_values('Country')
        elif table_options == "Summary by Country":
            agg_metrics = {
                'WHO_region': 'first',
                'Cumulative_cases': 'max',
                'Cumulative_deaths': 'max',
                'New_weekly_cases': 'sum',
                'New_weekly_deaths': 'sum',
                'Mortality_rate': 'max'
            }
            if dataset_type == "Daily":
                agg_metrics.update({
                    'New_daily_cases': 'sum',
                    'New_daily_deaths': 'sum'
                })
            display_data = filtered.groupby('Country').agg(agg_metrics).reset_index().sort_values('Cumulative_cases', ascending=False)
        else:
            region_agg_metrics = {
                'Country': 'nunique',
                'Cumulative_cases': 'sum',
                'Cumulative_deaths': 'sum',
                'New_weekly_cases': 'sum',
                'New_weekly_deaths': 'sum'
            }
            if dataset_type == "Daily":
                region_agg_metrics.update({
                    'New_daily_cases': 'sum',
                    'New_daily_deaths': 'sum'
                })
            display_data = filtered.groupby(['WHO_region', 'Date_reported']).agg(region_agg_metrics).reset_index()
            display_data['Mortality_rate'] = (display_data['Cumulative_deaths'] / display_data['Cumulative_cases'] * 100).round(2)
            display_data = display_data.rename(columns={'Country': 'Countries'}).sort_values(['WHO_region', 'Date_reported'])

    # --- Use st_aggrid for enhanced table if available ---
    table_height = 450
    if AgGrid is not None:
        gb = GridOptionsBuilder.from_dataframe(display_data)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
        gb.configure_default_column(editable=False, groupable=True, filter=True, sortable=True, resizable=True)
        gb.configure_side_bar()
        grid_options = gb.build()
        st.caption("🔎 Tip: Use the column headers to sort/filter. Pagination enabled for large datasets.")
        AgGrid(
            display_data,
            gridOptions=grid_options,
            height=table_height,
            width='100%',
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            update_mode=GridUpdateMode.NO_UPDATE,
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
            theme='streamlit'
        )
    else:
        st.dataframe(
            display_data,
            use_container_width=True,
            height=table_height
        )

    st.caption(f"Showing {len(display_data):,} records")

    # Export options
    # (Download Analytics now handled in sidebar after filters are applied)
    # Data dictionary
    with st.expander("Data Dictionary", expanded=False):
        st.markdown("""
        ### Column Descriptions
        * **Date_reported**: Date of the report
        * **Country**: Country, territory, or area name
        * **WHO_region**: WHO regional offices: AFRO (Africa), AMRO (Americas), EMRO (Eastern Mediterranean), EURO (Europe), SEARO (South-East Asia), WPRO (Western Pacific)
        * **Cumulative_cases**: Cumulative confirmed cases reported to WHO to date
        * **Cumulative_deaths**: Cumulative deaths reported to WHO to date
        * **New_daily_cases**: New confirmed cases reported in the last 24 hours (daily data only)
        * **New_daily_deaths**: New deaths reported in the last 24 hours (daily data only)
        * **New_weekly_cases**: New confirmed cases reported in the last 7 days
        * **New_weekly_deaths**: New deaths reported in the last 7 days
        * **Mortality_rate**: Deaths as a percentage of cases (Cumulative_deaths / Cumulative_cases * 100)
        """)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- FORECASTING (AI PREDICTIONS) TAB ----------
with tabs[6]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("🧠 Forecasting (AI Predictions)")
    st.markdown("Predict the next 14 days of COVID-19 metrics for selected countries using Prophet (if available) or ARIMA. Cumulative and new metrics are handled automatically.<br><span style='opacity:0.7;'>Hover over chart lines for more details.</span>", unsafe_allow_html=True)
    # --- Enforce max 3 countries ---
    forecast_countries = st.multiselect(
        "Select countries for forecasting (max 3):",
        options=sorted(filtered['Country'].unique()),
        default=sorted(filtered['Country'].unique())[:2],
        help="Choose up to 3 countries for best performance.",
        max_selections=3 if hasattr(st, "multiselect") and "max_selections" in st.multiselect.__code__.co_varnames else None
    )
    if len(forecast_countries) > 3:
        st.warning("⚠️ You can select up to 3 countries only.")
        forecast_countries = forecast_countries[:3]
    forecast_metric = st.selectbox(
        "Metric to forecast:",
        options=["Cumulative_cases", "Cumulative_deaths", "New_weekly_cases", "New_weekly_deaths"],
        index=0,
        help="Choose a metric to forecast."
    )
    st.caption("Forecasts include upper/lower confidence intervals. ARIMA fallback is robust for small datasets (≥10 rows).")
    if forecast_countries:
        for country in forecast_countries:
            with st.spinner(f"Generating forecast for {country}..."):
                st.subheader(f"Forecast for {country} ({forecast_metric})")
                country_df = filtered[filtered['Country'] == country][['Date_reported', forecast_metric]].copy()
                country_df = country_df.rename(columns={'Date_reported': 'ds', forecast_metric: 'y'})
                country_df['y'] = country_df['y'].fillna(0)
                # Adapt for cumulative: only positive, for new: allow zeros
                if "Cumulative" in forecast_metric:
                    country_df = country_df[country_df['y'] > 0]
                # For very small datasets, warn or fallback
                if len(country_df) < 10:
                    st.warning("Dataset is very small. Forecasts may be unreliable.")
                # Try Prophet, fallback to ARIMA if not available or fails
                forecast_success = False
                prophet_error = None
                if Prophet is not None and len(country_df) >= 2:
                    try:
                        m = Prophet()
                        m.fit(country_df)
                        future = m.make_future_dataframe(periods=14)
                        forecast = m.predict(future)
                        # Plotly visualization with confidence intervals
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=country_df['ds'], y=country_df['y'],
                            mode='lines+markers', name='Historical', line=dict(color="#3b82f6"),
                            hovertemplate='Date: %{x|%b %d, %Y}<br>Value: %{y:,.0f}<extra></extra>'
                        ))
                        fig.add_trace(go.Scatter(
                            x=forecast['ds'], y=forecast['yhat'],
                            mode='lines', name='Forecast', line=dict(color="#10b981", dash='dash'),
                            hovertemplate='Date: %{x|%b %d, %Y}<br>Forecast: %{y:,.0f}<extra></extra>'
                        ))
                        fig.add_trace(go.Scatter(
                            x=forecast['ds'], y=forecast['yhat_upper'],
                            mode='lines', name='Upper Bound', line=dict(color="#a7f3d0", width=0.5), showlegend=True,
                            hovertemplate='Upper Bound: %{y:,.0f}<extra></extra>'
                        ))
                        fig.add_trace(go.Scatter(
                            x=forecast['ds'], y=forecast['yhat_lower'],
                            mode='lines', name='Lower Bound', line=dict(color="#a7f3d0", width=0.5),
                            fill='tonexty', fillcolor='rgba(16,185,129,0.1)', showlegend=True,
                            hovertemplate='Lower Bound: %{y:,.0f}<extra></extra>'
                        ))
                        fig.update_layout(
                            title=f"{country} - {forecast_metric.replace('_',' ')} (14-Day Forecast, Prophet)",
                            xaxis_title="Date",
                            yaxis_title=forecast_metric.replace("_", " "),
                            height=400,
                            template="plotly_white"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        forecast_success = True
                    except Exception as e:
                        prophet_error = e
                else:
                    prophet_error = "Prophet not installed or insufficient data"
                if not forecast_success:
                    st.warning(f"Prophet not available or failed ({prophet_error}). Using ARIMA model as fallback.")
                    arima_df = country_df.copy().sort_values('ds')
                    y = arima_df['y'].values
                    if len(y) < 10 or np.all(y == y[0]):
                        st.error("Not enough data or no variation for ARIMA forecasting.")
                        continue
                    try:
                        order = (1, 1, 1) if "Cumulative" in forecast_metric else (2, 0, 2)
                        model = ARIMA(y, order=order)
                        model_fit = model.fit()
                        forecast_result = model_fit.get_forecast(steps=14)
                        forecast_values = forecast_result.predicted_mean
                        conf_int = forecast_result.conf_int()
                        if hasattr(conf_int, "to_numpy"):
                            conf_array = conf_int.to_numpy()
                        else:
                            conf_array = np.array(conf_int)
                        if conf_array.ndim == 1:
                            conf_array = np.column_stack((conf_array, conf_array))
                        upper_bound = conf_array[:, -1]
                        lower_bound = conf_array[:, 0]
                        last_date = pd.to_datetime(arima_df['ds'].iloc[-1])
                        freq = pd.infer_freq(arima_df['ds'])
                        if freq is None:
                            freq = "D"
                        forecast_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=14, freq=freq)
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=arima_df['ds'], y=arima_df['y'],
                            mode='lines+markers', name='Historical', line=dict(color="#3b82f6"),
                            hovertemplate='Date: %{x|%b %d, %Y}<br>Value: %{y:,.0f}<extra></extra>'
                        ))
                        fig.add_trace(go.Scatter(
                            x=forecast_dates, y=forecast_values,
                            mode='lines', name='Forecast (ARIMA)', line=dict(color="#10b981", dash='dash'),
                            hovertemplate='Date: %{x|%b %d, %Y}<br>Forecast: %{y:,.0f}<extra></extra>'
                        ))
                        fig.add_trace(go.Scatter(
                            x=forecast_dates, y=upper_bound,
                            mode='lines', name='Upper Bound', line=dict(color="#a7f3d0", width=0.5), showlegend=True,
                            hovertemplate='Upper Bound: %{y:,.0f}<extra></extra>'
                        ))
                        fig.add_trace(go.Scatter(
                            x=forecast_dates, y=lower_bound,
                            mode='lines', name='Lower Bound', line=dict(color="#a7f3d0", width=0.5),
                            fill='tonexty', fillcolor='rgba(16,185,129,0.1)', showlegend=True,
                            hovertemplate='Lower Bound: %{y:,.0f}<extra></extra>'
                        ))
                        fig.update_layout(
                            title=f"{country} - {forecast_metric.replace('_',' ')} (14-Day Forecast, ARIMA)",
                            xaxis_title="Date",
                            yaxis_title=forecast_metric.replace("_", " "),
                            height=400,
                            template="plotly_white"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"ARIMA forecasting failed for {country}: {e}")
    else:
        st.info("Select at least one country to view forecasts.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- STATISTICAL INSIGHTS TAB ----------
with tabs[7]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📊 Statistical Insights")
    st.markdown("Explore correlations and relationships between major metrics. <span style='opacity:0.7;'>Hover over heatmap for details.</span>", unsafe_allow_html=True)
    # Select columns to correlate
    corr_cols = [
        col for col in [
            'Cumulative_cases', 'Cumulative_deaths', 'New_weekly_cases', 'New_weekly_deaths',
            'Mortality_rate'
        ] if col in filtered.columns
    ]
    if dataset_type == "Daily":
        corr_cols += [col for col in ['New_daily_cases', 'New_daily_deaths'] if col in filtered.columns]
    corr_cols = list(dict.fromkeys(corr_cols))
    corr_data = filtered[corr_cols].dropna()
    if corr_data.empty or len(corr_data) < 2:
        st.info("Not enough data to compute correlations.")
    else:
        @st.cache_data(show_spinner=False)
        def cached_corr(df):
            return df.corr()
        corr = cached_corr(corr_data)
        if sns is None or plt is None:
            st.warning("Seaborn or matplotlib is not installed. Please install seaborn and matplotlib to view correlation heatmap.")
        else:
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax, cbar=True)
            ax.set_title("Correlation Heatmap of COVID-19 Metrics")
            st.pyplot(fig)
            # Optional: pairplot if data is small and seaborn available
            if len(corr_data) <= 200 and sns is not None:
                st.markdown("#### Pairwise Relationships (Pairplot, Sampled)")
                sample = corr_data.sample(min(len(corr_data), 100), random_state=42)
                pair_fig = sns.pairplot(sample)
                st.pyplot(pair_fig)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- VACCINATION VS MORTALITY TAB ----------
with tabs[8]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("💉 Vaccination vs Mortality")
    st.markdown("Compare vaccination rates with COVID-19 mortality. Upload your own vaccination dataset or use the default global data. <span style='opacity:0.7;'>Hover over points for details. Trendline shows overall relationship.</span>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload vaccination dataset (CSV with columns: Country, Date, Vaccination_rate, ...):",
        type=["csv"]
    )
    if uploaded_file is not None:
        try:
            vacc_df = pd.read_csv(uploaded_file)
            vacc_df['Date'] = pd.to_datetime(vacc_df['Date'], errors='coerce')
            merged = pd.merge(
                filtered,
                vacc_df,
                left_on=['Country', 'Date_reported'],
                right_on=['Country', 'Date'],
                how='inner'
            )
            show_vacc = True
        except Exception as e:
            st.error(f"Error processing vaccination dataset: {e}")
            show_vacc = False
    else:
        # Fetch default vaccination dataset from Our World in Data
        try:
            @st.cache_data(ttl=86400, show_spinner=False)
            def fetch_owid_vacc():
                url = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv"
                df = pd.read_csv(url, usecols=["location", "date", "people_fully_vaccinated_per_hundred"])
                df = df.rename(columns={"location": "Country", "date": "Date", "people_fully_vaccinated_per_hundred": "Vaccination_rate"})
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                return df
            vacc_df = fetch_owid_vacc()
            # Merge on closest date (within 2 days)
            filtered_copy = filtered.copy()
            filtered_copy['Date'] = filtered_copy['Date_reported']
            merged = pd.merge_asof(
                filtered_copy.sort_values('Date'),
                vacc_df.sort_values('Date'),
                by="Country",
                left_on="Date",
                right_on="Date",
                direction="nearest",
                tolerance=pd.Timedelta("2D")
            )
            show_vacc = True
            st.caption("Default vaccination data from Our World in Data (people fully vaccinated per hundred).")
        except Exception as e:
            st.warning(f"Could not fetch default vaccination data: {e}")
            show_vacc = False
    if show_vacc and not merged.empty:
        st.subheader("Vaccination Rate vs Mortality Rate")
        if 'Vaccination_rate' in merged.columns:
            plot_df = merged.dropna(subset=['Vaccination_rate', 'Mortality_rate'])
            if plot_df.empty:
                st.info("No overlapping data for vaccination and mortality rates.")
            else:
                # --- 7-day rolling average for vaccination rate ---
                plot_df = plot_df.sort_values(['Country', 'Date_reported'])
                plot_df['Vaccination_rate_rolling'] = plot_df.groupby('Country')['Vaccination_rate'].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
                fig = px.scatter(
                    plot_df,
                    x='Vaccination_rate_rolling',
                    y='Mortality_rate',
                    color='Country',
                    trendline='ols',
                    title="Vaccination Rate (7-day rolling avg) vs COVID-19 Mortality Rate",
                    labels={'Vaccination_rate_rolling': 'Vaccination Rate (7-day avg, %)', 'Mortality_rate': 'Mortality Rate (%)'},
                    height=500
                )
                fig.update_traces(
                    hovertemplate='Country: %{customdata[0]}<br>Vaccination Rate: %{x:.2f}%<br>Mortality Rate: %{y:.2f}%',
                    customdata=plot_df[['Country']]
                )
                fig.update_layout(
                    legend_title="Country"
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Trendline (dashed) shows linear fit between 7-day average vaccination and mortality rates.")
                # --- Multi-variate regression plot (optional) ---
                st.subheader("Multi-variate Regression: Mortality vs Vaccination Rate & Cumulative Cases")
                if len(plot_df) > 1:
                    try:
                        import statsmodels.api as sm
                        X = plot_df[['Vaccination_rate_rolling', 'Cumulative_cases']].copy()
                        X['Cumulative_cases'] = np.log1p(X['Cumulative_cases'])
                        X = sm.add_constant(X)
                        y = plot_df['Mortality_rate']
                        model = sm.OLS(y, X).fit()
                        st.write("Regression summary:")
                        st.text(model.summary())
                        # 3D plot
                        fig3d = go.Figure()
                        fig3d.add_trace(go.Scatter3d(
                            x=plot_df['Vaccination_rate_rolling'],
                            y=np.log1p(plot_df['Cumulative_cases']),
                            z=plot_df['Mortality_rate'],
                            mode='markers',
                            marker=dict(size=4, color=plot_df['Mortality_rate'], colorscale='Viridis', colorbar=dict(title="Mortality Rate")),
                            text=plot_df['Country'],
                            name="Data"
                        ))
                        # Regression plane
                        vacc_range = np.linspace(plot_df['Vaccination_rate_rolling'].min(), plot_df['Vaccination_rate_rolling'].max(), 10)
                        case_range = np.linspace(np.log1p(plot_df['Cumulative_cases']).min(), np.log1p(plot_df['Cumulative_cases']).max(), 10)
                        vacc_grid, case_grid = np.meshgrid(vacc_range, case_range)
                        Z = (model.params['const'] +
                             model.params['Vaccination_rate_rolling'] * vacc_grid +
                             model.params['Cumulative_cases'] * case_grid)
                        fig3d.add_trace(go.Surface(
                            x=vacc_grid, y=case_grid, z=Z,
                            colorscale='YlGnBu', showscale=False, opacity=0.5, name="Regression Plane"
                        ))
                        fig3d.update_layout(
                            scene=dict(
                                xaxis_title='Vaccination Rate (7-day avg, %)',
                                yaxis_title='log(Cumulative Cases)',
                                zaxis_title='Mortality Rate (%)'
                            ),
                            title="Mortality Rate as Function of Vaccination Rate & log(Cumulative Cases)",
                            height=600
                        )
                        st.plotly_chart(fig3d, use_container_width=True)
                    except Exception as e:
                        st.info(f"Multi-variate regression plot could not be generated: {e}")
        else:
            st.warning("Column 'Vaccination_rate' not found in the vaccination dataset.")
    elif not uploaded_file:
        st.info("Default global vaccination dataset loaded. Upload your own for custom analysis.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- REPORT EXPORT TAB ----------
with tabs[9]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📄 Report Export")
    st.markdown("Generate a branded PDF report with summary statistics and charts for your selected filters.<br><span style='opacity:0.7;'>Charts can be optionally included as images.</span>", unsafe_allow_html=True)
    if canvas is None:
        st.warning("ReportLab is not installed. Please install reportlab to enable PDF export.")
    else:
        # Prepare summary statistics
        summary = {
            "Date Range": f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}",
            "Affected Countries": affected_countries,
            "Total Cases": global_cases,
            "Total Deaths": global_deaths,
            "Mortality Rate (%)": f"{avg_mortality:.2f}",
            "New Cases (Current)": new_cases,
            "New Deaths (Current)": new_deaths,
        }
        # --- Add cover page info ---
        today_str = datetime.date.today().strftime("%B %d, %Y")
        # --- Table of Contents ---
        toc = [
            ("1. Cover Page", "cover"),
            ("2. Summary Statistics", "summary"),
            ("3. Key Charts", "charts"),
            ("4. Data Table", "datatable")
        ]
        # --- Prepare charts as images using kaleido ---
        chart_imgs = []
        chart_titles = []
        try:
            # 1. Global map (static snapshot)
            fig_map_snapshot = px.scatter_geo(
                filtered[filtered['Date_reported'] == latest_date],
                locations="Country",
                locationmode='country names',
                color="Cumulative_cases",
                size="Cumulative_cases",
                hover_name="Country",
                projection="natural earth",
                title='Global COVID-19 Cases Snapshot',
                color_continuous_scale="Viridis"
            )
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                fig_map_snapshot.write_image(tmpfile.name, format="png", width=900, height=500)
                chart_imgs.append(tmpfile.name)
                chart_titles.append("Global COVID-19 Cases Map")
            # 2. Top countries bar chart
            fig_top = px.bar(
                filtered[filtered['Date_reported'] == latest_date].sort_values("Cumulative_cases", ascending=False).head(10),
                x="Country", y="Cumulative_cases", color="Cumulative_cases",
                title="Top 10 Countries by Cases",
                color_continuous_scale="Blues"
            )
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                fig_top.write_image(tmpfile.name, format="png", width=900, height=500)
                chart_imgs.append(tmpfile.name)
                chart_titles.append("Top 10 Countries by Cases")
            # 3. Trends chart
            timeline = filtered.groupby('Date_reported').agg({'Cumulative_cases': 'sum', 'Cumulative_deaths': 'sum'}).reset_index()
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=timeline['Date_reported'], y=timeline['Cumulative_cases'], name="Cases", line=dict(color="#3b82f6")))
            fig_trend.add_trace(go.Scatter(x=timeline['Date_reported'], y=timeline['Cumulative_deaths'], name="Deaths", line=dict(color="#ef4444")))
            fig_trend.update_layout(title="Cumulative Cases & Deaths Over Time", xaxis_title="Date", yaxis_title="Count")
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                fig_trend.write_image(tmpfile.name, format="png", width=900, height=500)
                chart_imgs.append(tmpfile.name)
                chart_titles.append("Cumulative Cases & Deaths Over Time")
        except Exception as e:
            st.warning(f"Could not export all charts as images: {e}")
        # --- PDF Generation ---
        def generate_pdf(summary, chart_imgs, chart_titles, toc, datatable_df):
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter
            # --- Cover Page ---
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(width/2, height-100, "COVID-19 Global Impact Analysis")
            c.setFont("Helvetica", 16)
            c.drawCentredString(width/2, height-140, "Manjot Singh")
            c.setFont("Helvetica", 12)
            c.drawCentredString(width/2, height-180, f"Date: {today_str}")
            c.showPage()
            # --- Table of Contents ---
            c.setFont("Helvetica-Bold", 18)
            c.drawString(72, height-100, "Table of Contents")
            c.setFont("Helvetica", 12)
            y = height-130
            for idx, (title, _) in enumerate(toc):
                c.drawString(90, y, f"{title}")
                y -= 22
            c.showPage()
            # --- Summary Statistics ---
            c.setFont("Helvetica-Bold", 18)
            c.drawString(72, height-100, "Summary Statistics")
            c.setFont("Helvetica", 12)
            y = height-130
            for k, v in summary.items():
                c.drawString(90, y, f"{k}: {v}")
                y -= 20
            c.showPage()
            # --- Charts ---
            c.setFont("Helvetica-Bold", 18)
            c.drawString(72, height-100, "Key Charts")
            c.setFont("Helvetica", 12)
            y = height-120
            for img_path, title in zip(chart_imgs, chart_titles):
                try:
                    img = Image.open(img_path)
                    aspect = img.width / img.height
                    img_width = width - 120
                    img_height = img_width / aspect
                    if img_height > (height-220):
                        img_height = height-220
                        img_width = img_height * aspect
                    c.drawString(90, y, title)
                    y -= 20
                    c.drawImage(img_path, 60, y-img_height, width=img_width, height=img_height)
                    y -= img_height + 30
                    if y < 120:
                        c.showPage()
                        y = height-120
                except Exception:
                    continue
            c.showPage()
            # --- Data Table (first 20 rows) ---
            c.setFont("Helvetica-Bold", 18)
            c.drawString(72, height-100, "Data Table (First 20 Rows)")
            c.setFont("Helvetica", 8)
            y = height-120
            data_cols = datatable_df.columns.tolist()
            col_width = (width-100)//len(data_cols)
            # Header
            for i, col in enumerate(data_cols):
                c.drawString(72 + i*col_width, y, str(col)[:15])
            y -= 12
            # Rows
            for idx, row in datatable_df.head(20).iterrows():
                for i, col in enumerate(data_cols):
                    c.drawString(72 + i*col_width, y, str(row[col])[:15])
                y -= 12
                if y < 60:
                    c.showPage()
                    y = height-120
            c.save()
            pdf = buffer.getvalue()
            buffer.close()
            return pdf
        # --- PDF Download Button ---
        if st.button("Generate & Download PDF Report"):
            with st.spinner("Generating PDF report..."):
                datatable_df = filtered[filtered['Date_reported'] == latest_date].sort_values('Country').reset_index(drop=True)
                pdf_bytes = generate_pdf(summary, chart_imgs, chart_titles, toc, datatable_df)
                st.download_button(
                    "📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"COVID19_Report_{today_str.replace(' ','_').replace(',','')}.pdf",
                    mime="application/pdf"
                )
        st.info("Cover page with project title, your name, and date is included. Table of contents and charts are embedded as images.")
    st.markdown('</div>', unsafe_allow_html=True)
# ---------- Modern Footer ----------
st.markdown("""
<div class="footer">
    &copy; 2024 Manjot Singh &mdash; COVID-19 Analytics Hub. Data: WHO, Our World in Data. Design: Modern Light Theme.
</div>
""", unsafe_allow_html=True)