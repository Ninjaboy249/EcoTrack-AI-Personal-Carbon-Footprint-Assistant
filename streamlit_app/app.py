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
        .stApp {{
            background-image: url('data:image/png;base64,{get_bg_base64()}');
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        .card {{
            background: rgba(255,255,255,0.08);
            padding: 16px;
            border-radius: 12px;
            backdrop-filter: blur(6px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        }}
        .glow-text {{
            color: #fff;
            text-shadow: 0 0 8px rgba(255,255,255,0.8);
        }}
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
