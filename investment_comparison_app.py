import streamlit as st
import pandas as pd
import numpy as np
import io
import requests
from datetime import datetime, timedelta
import os
from PIL import Image
import matplotlib.pyplot as plt
import locale

# Set page configuration with custom name and icon
st.set_page_config(
    page_title="🏦 Mevduat-Fon Karşılaştırma",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set the page name in the sidebar
st.sidebar.markdown("# 🏦 Mevduat-Fon Karşılaştırma")

# Updated color palette 
colors = {
    "chrysler_blue": "#3527DD",
    "dark_purple": "#2C1320",
    "sandy_brown": "#FA9F42",
    "dartmouth_green": "#0B6E4F",
    "platinum": "#E0E0E2"
}

# Custom CSS with the new color palette
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
    
    .product-b-card {{
        background-color: rgba(11, 110, 79, 0.1);
        border-left: 5px solid {colors["dartmouth_green"]};
    }}
    
    .product-a-card {{
        background-color: rgba(53, 39, 221, 0.1);
        border-left: 5px solid {colors["chrysler_blue"]};
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
    
    /* Change button colors to match the new theme */
    .stButton>button {{
        background-color: {colors["dartmouth_green"]};
        color: white;
    }}
    
    /* Style number inputs and selects to match the theme */
    .stNumberInput div[data-baseweb="input"] {{
        border-color: {colors["dartmouth_green"]};
    }}
    
    .stSelectbox div[data-baseweb="select"] {{
        border-color: {colors["dartmouth_green"]};
    }}
    
    /* Add some style to the sidebar */
    .css-1d391kg {{
        background-color: {colors["platinum"]};
    }}
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 class='main-header'>Mundi Getiri Hesaplama</h1>", unsafe_allow_html=True)

# Function to convert string percentage to float
def convert_to_float(value):
    if isinstance(value, str):
        # Replace comma with dot if needed
        value = value.replace(',', '.')
        # Remove any % sign if present
        value = value.replace('%', '')
    return float(value)

# Function to format numbers in Turkish locale (. as thousands separator, , as decimal)
def format_turkish(number, decimals=2):
    """Format number with Turkish locale (1.234,56)"""
    if number == 0:
        return "0"
    
    # Get integer and decimal parts
    if decimals > 0:
        integer_part = int(number)
        decimal_part = abs(number) - abs(int(number))
        
        # Format integer part with thousands separator
        formatted_int = ""
        int_str = str(abs(integer_part))
        for i, digit in enumerate(reversed(int_str)):
            if i > 0 and i % 3 == 0:
                formatted_int = "." + formatted_int
            formatted_int = digit + formatted_int
        
        if integer_part < 0:
            formatted_int = "-" + formatted_int
            
        # Format decimal part
        formatted_decimal = str(int(decimal_part * (10 ** decimals)))
        # Pad with leading zeros if needed
        formatted_decimal = formatted_decimal.zfill(decimals)
        
        return f"{formatted_int},{formatted_decimal}"
    else:
        # No decimals, just format integer
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
    """Format percentage with Turkish locale (12,34%)"""
    formatted = format_turkish(number, decimals)
    return f"%{formatted}"

# Load fund data from GitHub repository
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_fund_data():
    try:
        # GitHub raw content URL for the funds.csv file
        github_url = "https://raw.githubusercontent.com/srtczn/compBoard/main/funds.csv"
        
        response = requests.get(github_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Check if we got a valid response
        if response.status_code == 200:
            return pd.read_csv(io.StringIO(response.text))
        else:
            st.error(f"Failed to fetch data: HTTP {response.status_code}")
            # Try local file as fallback
            if os.path.exists("funds.csv"):
                st.warning("Using local funds.csv file as fallback")
                return pd.read_csv("funds.csv")
            else:
                # Use minimal fallback data if all else fails
                fallback_data = """Fon Kodu,Fon Adı,Tarih,Değişim
HVTAL,ALBATROSS PORTFÖY BİRİNCİ PARA PİYASASI (TL) FONU,08.05.2025,0.001542316975"""
                st.warning("Using minimal fallback data")
                return pd.read_csv(io.StringIO(fallback_data))
    except Exception as e:
        st.error(f"Error loading fund data: {e}")
        # Try local file as fallback
        if os.path.exists("funds.csv"):
            st.warning("Using local funds.csv file as fallback")
            return pd.read_csv("funds.csv")
        else:
            # Use minimal fallback data if all else fails
            fallback_data = """Fon Kodu,Fon Adı,Tarih,Değişim
HVTAL,ALBATROSS PORTFÖY BİRİNCİ PARA PİYASASI (TL) FONU,08.05.2025,0.001542316975"""
            st.warning("Using minimal fallback data")
            return pd.read_csv(io.StringIO(fallback_data))

# Load and process fund data
fund_data = load_fund_data()

# Ensure Değişim column is a float (convert from string if needed)
fund_data['Değişim'] = fund_data['Değişim'].apply(convert_to_float)

# Get list of fund codes and names
fund_options = dict(zip(fund_data['Fon Kodu'], fund_data['Fon Adı']))
ticker_list = sorted(fund_data['Fon Kodu'].unique())

# Create a dictionary for fund returns (using Fon Kodu as key)
latest_returns = dict(zip(fund_data['Fon Kodu'], fund_data['Değişim']))

# Create a description for each fund (using Fon Adı from data)
fund_descriptions = dict(zip(fund_data['Fon Kodu'], fund_data['Fon Adı']))

# Add logo to the sidebar
logo_path = "assets/logo.webp"
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.sidebar.image(logo, use_container_width=True)

# Create sidebar for inputs
st.sidebar.markdown("<h2 class='section-header'>Hesaplama Aracı:</h2>", unsafe_allow_html=True)

# Investment amount input
investment_amount = st.sidebar.number_input(
    "Yatırım Tutarı (₺)",
    min_value=1000,
    max_value=10000000,
    value=10000,
    step=1000,
    format="%d"
)

duration_days = st.sidebar.number_input(
    "Süre (Gün)",
    min_value=1,
    max_value=3650,
    value=1,
    step=1
)

# Divider
st.sidebar.markdown("---")

# Fixed Income Product A - Gecelik Mevduat
st.sidebar.markdown("<h3 style='color: {}'>Gecelik Mevduat</h3>".format(colors["chrysler_blue"]), unsafe_allow_html=True)

interest_rate_a = st.sidebar.number_input(
    "Faiz Oranı (%)",
    min_value=0.0,
    max_value=90.0,
    value=45.50,
    step=0.05,
    key="interest_a"
)

commission_rate_a = st.sidebar.number_input(
    "Mundi Komisyon Oranı (%)",
    min_value=0.0,
    max_value=5.0,
    value=1.5,
    step=0.05,
    key="commission_a"
)

tax_rate_a = st.sidebar.number_input(
    "Stopaj Oranı (%)",
    min_value=0.0,
    max_value=50.0,
    value=15.0,
    step=0.5,
    key="tax_a"
)

# Divider
st.sidebar.markdown("---")

# Fixed Income Product B - Gecelik Repo
st.sidebar.markdown("<h3 style='color: {}'>Gecelik Repo</h3>".format(colors["dartmouth_green"]), unsafe_allow_html=True)

interest_rate_b = st.sidebar.number_input(
    "Faiz Oranı (%)",
    min_value=0.0,
    max_value=90.0,
    value=45.0,
    step=0.05,
    key="interest_b"
)

commission_rate_b = st.sidebar.number_input(
    "Komisyon Oranı (%)",
    min_value=0.0,
    max_value=5.0,
    value=0.0,
    step=0.05,
    key="commission_b"
)

tax_rate_b = st.sidebar.number_input(
    "Stopaj Oranı (%)",
    min_value=0.0,
    max_value=50.0,
    value=15.0,
    step=0.5,
    key="tax_b"
)

# Divider
st.sidebar.markdown("---")

# Fund Product - Yatırım Fonları
st.sidebar.markdown("<h3 style='color: {}'>Yatırım Fonları</h3>".format(colors["sandy_brown"]), unsafe_allow_html=True)

# Create a display string for selectbox
fund_display_options = [f"{code} - {name}" for code, name in fund_options.items()]

# Map between display string and actual code
fund_code_map = {f"{code} - {name}": code for code, name in fund_options.items()}

# Display selectbox with combined code-name options
selected_display = st.sidebar.selectbox(
    "Fon Seçiniz",
    fund_display_options,
    index=0
)

# Extract the actual ticker/code
selected_ticker = fund_code_map[selected_display]

# Get the latest daily return for the selected fund
latest_return = latest_returns[selected_ticker]
# Format the percentage with 6 decimal places in Turkish format
formatted_return_percent = format_turkish_percent(latest_return * 100, 6)
fund_info = f"{fund_descriptions[selected_ticker]} (Son 1 Günlük Getiri: {formatted_return_percent})"
st.sidebar.info(fund_info)

# Process the "Tarih" column to ensure it's in datetime format
try:
    fund_data['Tarih'] = pd.to_datetime(fund_data['Tarih'], format='%d.%m.%Y')
except:
    try:
        # Try alternative format
        fund_data['Tarih'] = pd.to_datetime(fund_data['Tarih'])
    except Exception as e:
        st.warning(f"Date format conversion issue: {e}. Using original dates.")

# Show data source and update date at the end of the sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 class='section-header'>Veri Kaynağı</h3>", unsafe_allow_html=True)
st.sidebar.info("Data source: srtczn/compBoard GitHub repository")

# Show when the data was last updated (most recent date in the dataset)
try:
    latest_data_date = fund_data['Tarih'].max().strftime('%d.%m.%Y')
    st.sidebar.success(f"Son veri güncelleme: {latest_data_date}")
except:
    # If date conversion failed, don't display this
    pass

# BSMV tax rate (fixed at 5%)
bsmv_rate = 0.05

# Calculate returns for each product
# Fixed Income Product A - Gecelik Mevduat with daily compounding
interest_rate_a_decimal = interest_rate_a / 100
daily_rate_a = interest_rate_a_decimal / 365
commission_rate_a_decimal = commission_rate_a / 100
daily_commission_rate_a = commission_rate_a_decimal / 365
tax_rate_a_decimal = tax_rate_a / 100

# Calculate daily interest for the investment period
future_value_a = investment_amount * (1 + daily_rate_a) ** duration_days
gross_return_a = future_value_a - investment_amount

# Calculate commission using the daily rate model as requested
commission_a = investment_amount * daily_commission_rate_a * duration_days

# Calculate BSMV (5% of commission)
bsmv_a = commission_a * bsmv_rate

# Calculate income tax (stopaj) directly on the gross return
tax_a = gross_return_a * tax_rate_a_decimal

# Calculate final net return
net_return_a = gross_return_a - commission_a - bsmv_a - tax_a
final_balance_a = investment_amount + net_return_a

# Fixed Income Product B - Gecelik Repo with daily compounding
interest_rate_b_decimal = interest_rate_b / 100
daily_rate_b = interest_rate_b_decimal / 365
commission_rate_b_decimal = commission_rate_b / 100
daily_commission_rate_b = commission_rate_b_decimal / 365
tax_rate_b_decimal = tax_rate_b / 100

# Calculate daily interest for the investment period
future_value_b = investment_amount * (1 + daily_rate_b) ** duration_days
gross_return_b = future_value_b - investment_amount

# Calculate commission using the daily rate model
commission_b = investment_amount * daily_commission_rate_b * duration_days

# Calculate BSMV (5% of commission)
bsmv_b = commission_b * bsmv_rate

# Calculate income tax (stopaj) directly on the gross return
tax_b = gross_return_b * tax_rate_b_decimal

# Calculate final net return
net_return_b = gross_return_b - commission_b - bsmv_b - tax_b
final_balance_b = investment_amount + net_return_b

# Fund Product - Yatırım Fonu
fund_future_value = investment_amount * (1 + latest_return) ** duration_days
fund_return = fund_future_value - investment_amount
final_balance_fund = investment_amount + fund_return

# Find the best performing product
results = {
    "Gecelik Mevduat": net_return_a,
    "Gecelik Repo": net_return_b,
    "Yatırım Fonu": fund_return
}

best_return = max(results.values())
best_product = max(results, key=results.get)

# Calculate percentage comparisons
percentage_a = (net_return_a / best_return) * 100 if best_return > 0 else 100
percentage_b = (net_return_b / best_return) * 100 if best_return > 0 else 100
percentage_fund = (fund_return / best_return) * 100 if best_return > 0 else 100

# Display the results in columns
col1, col2, col3 = st.columns(3)

# Fixed Income Product A - Gecelik Mevduat
with col1:
    st.markdown(f"""
    <div class="card product-a-card">
        <h3 class="card-title">Gecelik Mevduat</h3>
        <div class="result-value">₺{format_turkish(net_return_a)}</div>
        <div class="result-label">Toplam Getiri</div>
        <div class="result-value">₺{format_turkish(final_balance_a)}</div>
        <div class="result-label">Net Dönüş Tutarı</div>
        <div class="divider"></div>
        <div class="result-label">Detaylar:</div>
        <div>Brüt Geri Dönüş Tutarı: ₺{format_turkish(gross_return_a)}</div>
        <div>Mundi Komisyonu: -₺{format_turkish(commission_a)}</div>
        <div>BSMV: -₺{format_turkish(bsmv_a)}</div>
        <div>Stopaj: -₺{format_turkish(tax_a)}</div>
        <div class="divider"></div>
        <div class="percent-compare">
            En iyi getiri ile karşılaştırma: {format_turkish_percent(percentage_a, 1)}
            <p>{" ★ EN İYİ GETİRİ" if best_product == "Gecelik Mevduat" else ""}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Fixed Income Product B - Gecelik Repo
with col2:
    st.markdown(f"""
    <div class="card product-b-card">
        <h3 class="card-title">Gecelik Repo</h3>
        <div class="result-value">₺{format_turkish(net_return_b)}</div>
        <div class="result-label">Toplam Getiri</div>
        <div class="result-value">₺{format_turkish(final_balance_b)}</div>
        <div class="result-label">Net Dönüş Tutarı</div>
        <div class="divider"></div>
        <div class="result-label">Detaylar:</div>
        <div>Brüt Geri Dönüş Tutarı: ₺{format_turkish(gross_return_b)}</div>
        <div>Komisyon: -₺{format_turkish(commission_b)}</div>
        <div>BSMV: -₺{format_turkish(bsmv_b)}</div>
        <div>Stopaj: -₺{format_turkish(tax_b)}</div>
        <div class="divider"></div>
        <div class="percent-compare">
            En iyi getiri ile karşılaştırma: {format_turkish_percent(percentage_b, 1)}
            <p>{" ★ EN İYİ GETİRİ" if best_product == "Gecelik Repo" else ""}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Fund Product - Yatırım Fonu
with col3:
    st.markdown(f"""
    <div class="card fund-card">
        <h3 class="card-title">Fon: {selected_ticker}</h3>
        <div class="result-value">₺{format_turkish(fund_return)}</div>
        <div class="result-label">Toplam Getiri</div>
        <div class="result-value">₺{format_turkish(final_balance_fund)}</div>
        <div class="result-label">Net Dönüş Tutarı</div>
        <div class="divider"></div>
        <div class="result-label">Detaylar:</div>
        <div>Günlük Getiri: {format_turkish_percent(latest_return * 100, 6)}</div>
        <div>Bileşik Getiri: {format_turkish_percent(((1 + latest_return) ** duration_days - 1) * 100, 2)}</div>
        <div class="divider"></div>
        <div class="percent-compare">
            En iyi getiri ile karşılaştırma: {format_turkish_percent(percentage_fund, 1)}
            <p>{" ★ EN İYİ GETİRİ" if best_product == "Yatırım Fonu" else ""}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Additional information and charts
st.markdown("<h2 class='section-header'>Getiri Analizi</h2>", unsafe_allow_html=True)

# Performance comparison chart - Updated for compound interest and new commission calculation
def calculate_growth(days):
    growth_a = []
    growth_b = []
    growth_fund = []
    
    for d in range(days+1):
        # For day 0, just use initial investment
        if d == 0:
            growth_a.append(investment_amount)
            growth_b.append(investment_amount)
            growth_fund.append(investment_amount)
            continue
        
        # Calculate daily growth for Product A - Gecelik Mevduat
        interest_earned_a = investment_amount * (1 + daily_rate_a) ** d - investment_amount
        commission_cost_a = investment_amount * daily_commission_rate_a * d
        bsmv_cost_a = commission_cost_a * bsmv_rate
        # Stopaj is calculated directly on gross interest
        tax_cost_a = interest_earned_a * tax_rate_a_decimal
        net_value_a = investment_amount + interest_earned_a - commission_cost_a - bsmv_cost_a - tax_cost_a
        growth_a.append(net_value_a)
        
        # Calculate daily growth for Product B - Gecelik Repo
        interest_earned_b = investment_amount * (1 + daily_rate_b) ** d - investment_amount
        commission_cost_b = investment_amount * daily_commission_rate_b * d
        bsmv_cost_b = commission_cost_b * bsmv_rate
        # Stopaj is calculated directly on gross interest
        tax_cost_b = interest_earned_b * tax_rate_b_decimal
        net_value_b = investment_amount + interest_earned_b - commission_cost_b - bsmv_cost_b - tax_cost_b
        growth_b.append(net_value_b)
        
        # Calculate daily growth for the Fund product
        fund_value = investment_amount * (1 + latest_return) ** d
        growth_fund.append(fund_value)
    
    return growth_a, growth_b, growth_fund

# Only show the chart if duration is reasonable for visualization
if duration_days <= 365:
    growth_a, growth_b, growth_fund = calculate_growth(duration_days)
    
    fig, ax = plt.figure(figsize=(10, 5)), plt.axes()
    
    # Plot with colors from our palette
    ax.plot(range(duration_days+1), growth_a, color=colors["chrysler_blue"], label="Gecelik Mevduat", linewidth=2)
    ax.plot(range(duration_days+1), growth_b, color=colors["dartmouth_green"], label="Gecelik Repo", linewidth=2)
    ax.plot(range(duration_days+1), growth_fund, color=colors["sandy_brown"], label=f"{selected_ticker}", linewidth=2)
    
    ax.set_xlabel('Gün')
    ax.set_ylabel('Tutar (₺)')
    ax.set_title('Yatırımın tahmini performansı')
    
    # Format y-axis with Turkish number format
    from matplotlib.ticker import FuncFormatter
    
    def turkish_currency_formatter(x, pos):
        return f'₺{format_turkish(x, 0)}'
    
    ax.yaxis.set_major_formatter(FuncFormatter(turkish_currency_formatter))
    
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Set background color for the chart
    ax.set_facecolor(colors["platinum"])
    fig.patch.set_facecolor('white')
    
    st.pyplot(fig)
else:
    st.info("Yatırım süresi 365 günden fazla olduğunda büyüme grafiği gösterilmez.")

# Summary and recommendation
st.markdown("<h2 class='section-header'>Sonuç</h2>", unsafe_allow_html=True)

best_choice_explanation = {
    "Gecelik Mevduat": f"Gecelik Mevduat günlük bileşik faiz ile daha uygun faiz oranı ve daha düşük ücret/vergi kombinasyonu sayesinde en iyi getiriyi sağlıyor.",
    "Gecelik Repo": f"Gecelik Repo, daha yüksek ücretlere rağmen günlük bileşik faiz ve üstün faiz oranı sayesinde daha iyi performans gösteriyor.",
    "Yatırım Fonu": f"Yatırım Fonu ({selected_ticker} - {fund_descriptions[selected_ticker]}) güçlü bileşik günlük büyüme sayesinde en yüksek getiriyi sunuyor, ancak daha fazla risk taşıyabilir."
}

st.markdown(f"""
<div style="background-color: rgba(44, 19, 32, 0.05); padding: 1.5rem; border-radius: 10px; margin-top: 1rem; border-left: 5px solid {colors["dark_purple"]};">
    <h3>Tavsiye</h3>
    <p><strong>{best_product}</strong>'nin {format_turkish(duration_days, 0)} gün içinde <strong>₺{format_turkish(results[best_product])}</strong> ile en yüksek getiriyi sağlaması öngörülüyor.</p>
    <p>{best_choice_explanation[best_product]}</p>
    <p>Geçmiş performansın gelecekteki sonuçları garanti etmediğini, özellikle piyasa volatilitesine tabi olabilecek yatırım fonu seçeneği için, unutmayın.</p>
</div>
""", unsafe_allow_html=True)

# Footer with version and GitHub link
st.markdown(f"""
<div style="font-size: 0.8rem; color: {colors["dark_purple"]}; text-align: center; margin-top: 2rem;">
    <p>Mundi Getiri Hesaplama v1.0 | <a href="https://github.com/srtczn/compBoard" target="_blank">GitHub</a></p>
</div>
""", unsafe_allow_html=True) 