import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
ENTRIES_PATH = os.path.join(DATA_DIR, 'entries.json')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
BG_PATH = os.path.join(ASSETS_DIR, 'ecotrack-bg.png')

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

# Emission factors (per unit) - same as Node app
EMISSION_FACTORS = {
    'transport': 0.21,    # kg CO2 per km (example)
    'electricity': 0.475, # kg CO2 per kWh
    'food': 0.3,          # kg CO2 per meal/unit
    'shopping': 0.2       # kg CO2 per arbitrary unit
}

# Helpers for reading/writing JSON
def load_entries():
    if not os.path.exists(ENTRIES_PATH):
        return []
    try:
        with open(ENTRIES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_entries(entries):
    with open(ENTRIES_PATH, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

# Styling - background image and transparent containers
def local_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        html, body, .stApp, .block-container, .main {{
            font-family: 'Inter', sans-serif !important;
            color: #e6eef3;
        }}
        /* background with darker overlay and blend for visibility */
        body {{
            background-image: linear-gradient(rgba(3,7,11,0.72), rgba(3,7,11,0.72)), url('data:image/png;base64,{get_bg_base64()}');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-blend-mode: overlay;
        }}
        /* make Streamlit page container transparent so background shows through */
        .block-container {{
            background: rgba(0,0,0,0.12) !important;
            backdrop-filter: blur(6px) saturate(120%);
            border-radius: 12px;
            padding: 1.25rem !important;
        }}
        /* card-like sections */
        .card {{
            background: rgba(255,255,255,0.06) !important;
            padding: 16px;
            border-radius: 12px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.45);
            color: #f8fafc;
            text-shadow: 0 2px 8px rgba(0,0,0,0.6);
        }}
        /* glow/lighting for headings */
        .stHeader, h1, h2, .stMarkdown {{
            color: #ffffff !important;
            text-shadow: 0 2px 16px rgba(60,200,120,0.09), 0 1px 6px rgba(0,0,0,0.6);
        }}
        /* slider handle color (works for modern browsers) */
        input[type="range"]::-webkit-slider-thumb {{ background: #ff4d4f; }}
        input[type="range"]::-moz-range-thumb {{ background: #ff4d4f; }}
        </style>
        """,
        unsafe_allow_html=True
    )

def get_bg_base64():
    import base64
    if os.path.exists(BG_PATH):
        with open(BG_PATH, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ''

# App layout
st.set_page_config(page_title='EcoTrack AI', layout='wide')
local_css()

st.title('EcoTrack — Personal CO2 Tracker')
st.markdown('Track and visualise your carbon footprint with simple sliders and charts.')

col1, col2 = st.columns([1, 1])

with col1:
    st.header('Add manual entry')
    transport = st.slider('Transport (km)', 0, 500, 10, help='Distance traveled in km')
    electricity = st.slider('Electricity (kWh)', 0, 500, 50)
    food = st.slider('Food (units)', 0, 30, 1)
    shopping = st.slider('Shopping (units)', 0, 50, 2)

    note = st.text_input('Notes (optional)')

    if st.button('Add entry'):
        total = (transport * EMISSION_FACTORS['transport'] +
                 electricity * EMISSION_FACTORS['electricity'] +
                 food * EMISSION_FACTORS['food'] +
                 shopping * EMISSION_FACTORS['shopping'])
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'transport': transport,
            'electricity': electricity,
            'food': food,
            'shopping': shopping,
            'total_co2': round(total, 3),
            'note': note
        }
        entries = load_entries()
        entries.insert(0, entry)
        save_entries(entries)
        st.success(f'Entry added — total CO2: {entry["total_co2"]} kg')

with col2:
    st.header('Recent entries')
    entries = load_entries()
    if not entries:
        st.info('No entries yet — add one on the left.')
    else:
        df = pd.DataFrame(entries)
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        st.dataframe(df[['timestamp','transport','electricity','food','shopping','total_co2','note']].head(10))

st.markdown('---')

# Charts
st.header('Trends')
entries = load_entries()
if entries:
    df = pd.DataFrame(entries)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df_sorted = df.sort_values('timestamp')

    col3, col4 = st.columns([2,1])
    with col3:
        fig = px.line(df_sorted, x='timestamp', y='total_co2', title='Total CO2 over time', markers=True)
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        latest = df_sorted.iloc[-1]
        breakdown = pd.DataFrame({
            'category': ['transport','electricity','food','shopping'],
            'value': [latest['transport']*EMISSION_FACTORS['transport'], latest['electricity']*EMISSION_FACTORS['electricity'], latest['food']*EMISSION_FACTORS['food'], latest['shopping']*EMISSION_FACTORS['shopping']]
        })
        fig2 = px.bar(breakdown, x='category', y='value', title='Latest entry breakdown')
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info('Add entries to see trends and breakdowns.')

st.markdown('---')

st.markdown('Built with ❤️ — deploy this app by connecting the repository to Streamlit Community Cloud (share -> Deploy).')
