import streamlit as st
import pandas as pd
from data_fetcher import fetch_sanjose_flights, get_real_weather
from llm_service import generate_eco_proposal

# App Configuration
st.set_page_config(
    page_title="Eco Flight Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI improvement
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6c757d;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🌱 Eco Flight Planner | エコ・フライトプランナー</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Optimize Altitude and Speed for CO2 Reduction | CO2削減のための高度・速度最適化</div>', unsafe_allow_html=True)

st.write("This dashboard fetches real-time flight data for the San Jose area and uses a local AI (Nemotron) to generate altitude change proposals (based on physics) to reduce CO2 emissions. | サンノゼ周辺のリアルタイムのフライトデータを取得し、ローカルAI (Nemotron) を活用してCO2排出を削減するための適切なフライトパラメータの変更提案を生成します。")

# Data fetch section
st.header("1. Fetch Real-Time Flight Data | リアルタイム・フライトデータの取得")
if st.button("✈️ Refresh Flight Data | フライトデータを最新化する", type="primary"):
    with st.spinner("Fetching data from OpenSky API... | OpenSky APIからサンノゼ周辺のデータを取得中..."):
        df_flights = fetch_sanjose_flights()
        # Save to session state to prevent reloading
        st.session_state['df_flights'] = df_flights

# Only show if we have data in session state
if 'df_flights' in st.session_state:
    df_flights = st.session_state['df_flights']
    
    if df_flights.empty:
        st.warning("⚠️ No flights found in this area right now. Please try again later. | 現在、サンノゼ周辺で条件に合致するフライトデータが見つかりませんでした。別の時間帯にお試しください。")
    else:
        st.success(f"✅ Successfully fetched {len(df_flights)} flights! | フライトデータを {len(df_flights)} 件取得しました！")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📍 Flight Location | フライトロケーション")
            # Create lat/lon DataFrame for st.map
            map_df = df_flights[['latitude', 'longitude']].rename(columns={'latitude': 'lat', 'longitude': 'lon'})
            st.map(map_df, zoom=9)
            
        with col2:
            st.subheader("📋 Flight List | 取得したフライト一覧")
            display_cols = ['callsign', 'origin_country', 'baro_altitude', 'velocity']
            st.dataframe(df_flights[display_cols], use_container_width=True)
            
        st.divider()
        
        # LLM Interaction Section
        st.header("2. AI Eco-Flight Proposal | Nemotron AIによるエコ・フライト提案")
        st.write("Select a specific flight from the list to request efficiency proposals from the LLM. | リストから特定のフライトを選択し、LLMに効率化の提案を求めます。")
        
        flight_options = df_flights['callsign'].tolist()
        selected_callsign = st.selectbox("Select Callsign for Analysis | 分析対象のコールサイン（Callsign）を選択:", flight_options)
        
        if st.button("🔍 Check Current Status (Fetch & Analyze) | データ取得＆推論", type="primary"):
            flight_data = df_flights[df_flights['callsign'] == selected_callsign].iloc[0]
            
            with st.spinner("Fetching weather data from Open-Meteo... | Open-Meteoから気象データを取得中..."):
                weather_data = get_real_weather()
                
            st.info(f"⛅ **Upper Wind Speed (850hPa proxy) | 上空風速:** {weather_data.get('upper_wind_kmh', 'N/A')} km/h | **Surface Wind Speed | 地表風速:** {weather_data.get('surface_wind_kmh', 'N/A')} km/h")
            
            with st.spinner(f"Generating aerodynamic eco-flight proposal with Nemotron (localhost:30000) for {selected_callsign}... | Nemotronで物理的なエコ・フライト提案を生成中..."):
                proposal = generate_eco_proposal(flight_data, weather_data)
                
            st.success("### 🌿 AI Proposal for CO2 Reduction (Aerodynamic Analysis)")
            st.write(proposal)
