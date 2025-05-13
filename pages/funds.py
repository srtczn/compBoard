import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from PIL import Image
import matplotlib.pyplot as plt
import locale
from matplotlib.ticker import FuncFormatter

# Set page configuration
st.set_page_config(
    page_title="Fon Karşılaştırma",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Hide the native navigation
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Reuse the same color palette
colors = {
    "chrysler_blue": "#3527DD",
    "dark_purple": "#2C1320",
    "sandy_brown": "#FA9F42",
    "dartmouth_green": "#0B6E4F",
    "platinum": "#E0E0E2"
}

# Reuse the same CSS
st.markdown(f"""
<style>
    .main-header {{
        color: {colors["dartmouth_green"]};
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-align: center;
    }}
    
    .section-header {{
        color: {colors["dark_purple"]};
        font-size: 1.5rem;
        font-weight: 500;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }}
    
    .card {{
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }}
    
    .fund-card {{
        background-color: rgba(250, 159, 66, 0.1);
        border-left: 5px solid {colors["sandy_brown"]};
    }}
    
    .best-performance {{
        color: {colors["dartmouth_green"]};
        font-weight: 700;
    }}
    
    .card-title {{
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: {colors["dark_purple"]};
    }}
    
    .result-value {{
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    
    .result-label {{
        font-size: 1rem;
        color: #666;
        margin-bottom: 0.25rem;
    }}
    
    .percent-compare {{
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }}
    
    .divider {{
        height: 1px;
        background-color: {colors["platinum"]};
        margin: 1rem 0;
    }}
    
    .sidebar-logo {{
        display: block;
        margin: 0 auto;
        max-width: 100%;
        padding-bottom: 1rem;
    }}
    
    .stButton>button {{
        background-color: {colors["dartmouth_green"]};
        color: white;
    }}
    
    .stNumberInput div[data-baseweb="input"] {{
        border-color: {colors["dartmouth_green"]};
    }}
    
    .stSelectbox div[data-baseweb="select"] {{
        border-color: {colors["dartmouth_green"]};
    }}
    
    .css-1d391kg {{
        background-color: {colors["platinum"]};
    }}
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 class='main-header'>Fon Karşılaştırma</h1>", unsafe_allow_html=True)

# Function to convert string percentage to float
def convert_to_float(value):
    if isinstance(value, str):
        value = value.replace(',', '.')
        value = value.replace('%', '')
    return float(value)

# Function to format numbers in Turkish locale
def format_turkish(number, decimals=2):
    if number == 0:
        return "0"
    
    if decimals > 0:
        integer_part = int(number)
        decimal_part = abs(number) - abs(int(number))
        
        formatted_int = ""
        int_str = str(abs(integer_part))
        for i, digit in enumerate(reversed(int_str)):
            if i > 0 and i % 3 == 0:
                formatted_int = "." + formatted_int
            formatted_int = digit + formatted_int
        
        if integer_part < 0:
            formatted_int = "-" + formatted_int
            
        formatted_decimal = str(int(decimal_part * (10 ** decimals)))
        formatted_decimal = formatted_decimal.zfill(decimals)
        
        return f"{formatted_int},{formatted_decimal}"
    else:
        integer_part = int(round(number, 0))
        formatted_int = ""
        int_str = str(abs(integer_part))
        for i, digit in enumerate(reversed(int_str)):
            if i > 0 and i % 3 == 0:
                formatted_int = "." + formatted_int
            formatted_int = digit + formatted_int
            
        if integer_part < 0:
            formatted_int = "-" + formatted_int
            
        return formatted_int

# Function to format percentage in Turkish locale
def format_turkish_percent(number, decimals=2):
    formatted = format_turkish(number, decimals)
    return f"%{formatted}"

# Load fund data
@st.cache_data(ttl=3600)
def load_fund_data():
    try:
        if os.path.exists("funds.csv"):
            return pd.read_csv("funds.csv")
        else:
            st.error("Funds data file not found")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading fund data: {e}")
        return pd.DataFrame()

# Load and process fund data
fund_data = load_fund_data()
if not fund_data.empty:
    fund_data['Değişim'] = fund_data['Değişim'].apply(convert_to_float)
    fund_options = dict(zip(fund_data['Fon Kodu'], fund_data['Fon Adı']))
    latest_returns = dict(zip(fund_data['Fon Kodu'], fund_data['Değişim']))
    
    # Get top 3 funds based on Değişim
    top_funds = fund_data.sort_values('Değişim', ascending=False).head(3)
    default_funds = top_funds['Fon Kodu'].tolist()
else:
    fund_options = {}
    latest_returns = {}
    default_funds = []

# Add logo to the sidebar
logo_path = "assets/logo.webp"
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.sidebar.image(logo, use_container_width=True)
else:
    st.sidebar.image("https://i.ibb.co/0jQ5YtL/logo.png", width=200)

# Custom navigation
st.sidebar.markdown("---")  # Add a separator
st.sidebar.markdown("### Navigation")
st.sidebar.page_link("main.py", label="🏦 Mevduat-Fon Karşılaştırma")
st.sidebar.page_link("pages/funds.py", label="📊 Fon Karşılaştırma")

# Sidebar inputs
st.sidebar.markdown("<h2 class='section-header'>Yatırım Bilgileri</h2>", unsafe_allow_html=True)

# Investment amount input
investment_amount = st.sidebar.number_input(
    "Yatırım Tutarı (₺)",
    min_value=1000,
    max_value=10000000,
    value=10000,
    step=1000,
    format="%d"
)

# Investment period input
investment_period = st.sidebar.number_input(
    "Süre (Gün)",
    min_value=1,
    max_value=365,
    value=30,
    step=1
)

# Main content area
st.markdown("<h2 class='section-header'>Fon Seçimi</h2>", unsafe_allow_html=True)

# Create three columns for fund selection
col1, col2, col3 = st.columns(3)

# Fund selection dropdowns
selected_funds = []
with col1:
    fund1 = st.selectbox(
        "1. Fon",
        options=list(fund_options.keys()),
        format_func=lambda x: f"{x} - {fund_options[x]}",
        key="fund1",
        index=list(fund_options.keys()).index(default_funds[0]) if default_funds else 0
    )
    selected_funds.append(fund1)

with col2:
    fund2 = st.selectbox(
        "2. Fon",
        options=list(fund_options.keys()),
        format_func=lambda x: f"{x} - {fund_options[x]}",
        key="fund2",
        index=list(fund_options.keys()).index(default_funds[1]) if len(default_funds) > 1 else 1
    )
    selected_funds.append(fund2)

with col3:
    fund3 = st.selectbox(
        "3. Fon",
        options=list(fund_options.keys()),
        format_func=lambda x: f"{x} - {fund_options[x]}",
        key="fund3",
        index=list(fund_options.keys()).index(default_funds[2]) if len(default_funds) > 2 else 2
    )
    selected_funds.append(fund3)

# Calculate results
st.markdown("<h2 class='section-header'>Karşılaştırma Sonuçları</h2>", unsafe_allow_html=True)

# Calculate daily returns and final amounts
results = []
for fund in selected_funds:
    daily_return = latest_returns.get(fund, 0)
    final_amount = investment_amount * (1 + daily_return) ** investment_period
    total_return = ((final_amount / investment_amount) - 1) * 100
    
    # Calculate additional metrics
    daily_return_amount = investment_amount * daily_return
    total_return_amount = final_amount - investment_amount
    
    results.append({
        'fund': fund,
        'name': fund_options[fund],
        'daily_return': daily_return,
        'final_amount': final_amount,
        'total_return': total_return,
        'daily_return_amount': daily_return_amount,
        'total_return_amount': total_return_amount
    })

# Find the best performing fund
best_fund = max(results, key=lambda x: x['total_return'])

# Display results
result_cols = st.columns(3)
for i, result in enumerate(results):
    with result_cols[i]:
        st.markdown(f"""
        <div class="card fund-card">
            <h3 class="card-title">{result['name']}</h3>
            <div class="result-value">₺{format_turkish(result['total_return_amount'])}</div>
            <div class="result-label">Toplam Getiri</div>
            <div class="result-value">₺{format_turkish(result['final_amount'])}</div>
            <div class="result-label">Net Dönüş Tutarı</div>
            <div class="divider"></div>
            <div class="result-label">Detaylar:</div>
            <div>Günlük Getiri: {format_turkish_percent(result['daily_return'] * 100)}</div>
            <div>Günlük Getiri Tutarı: ₺{format_turkish(result['daily_return_amount'])}</div>
            <div>Toplam Getiri Oranı: {format_turkish_percent(result['total_return'])}</div>
            <div class="divider"></div>
            <div class="percent-compare">
                En iyi getiri ile karşılaştırma: {format_turkish_percent((result['total_return'] / best_fund['total_return'] - 1) * 100, 1)}
                <p>{" ★ EN İYİ GETİRİ" if result['fund'] == best_fund['fund'] else ""}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Create comparison graph
st.markdown("<h2 class='section-header'>Getiri Karşılaştırma Grafiği</h2>", unsafe_allow_html=True)

# Create data for the bar chart
fund_names = [f"{fund} - {fund_options[fund]}" for fund in selected_funds]
fund_returns = [investment_amount * ((1 + latest_returns[fund]) ** investment_period - 1) for fund in selected_funds]

# Create the plot
plt.figure(figsize=(12, 6))
x = range(len(fund_names))
width = 0.35

# Plot bars
plt.bar(x, fund_returns, width, label='Fon Getirisi', color=colors["sandy_brown"])

# Customize the plot
plt.title('Fon Getiri Karşılaştırması', fontsize=14, pad=20)
plt.xlabel('Fonlar', fontsize=12)
plt.ylabel('Tutar (TL)', fontsize=12)
plt.xticks(x, fund_names, rotation=45, ha='right')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# Format y-axis with Turkish number format
def turkish_currency_formatter(x, pos):
    return f'₺{format_turkish(x, 0)}'
plt.gca().yaxis.set_major_formatter(FuncFormatter(turkish_currency_formatter))

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Display the plot
st.pyplot(plt) 