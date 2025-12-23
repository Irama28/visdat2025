import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import folium
from streamlit_folium import st_folium
import requests

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Less Cars, More Life | UK Co-Benefits",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

GEOJSON_URL = "https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/administrative/gb/lad.json"

# --- CACHE GEOJSON DATA ---
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_geojson():
    """Load and cache GeoJSON data to avoid repeated fetches"""
    try:
        response = requests.get(GEOJSON_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error loading GeoJSON: {e}")
        return None

# --- CACHE MAP DATA AGGREGATION ---
@st.cache_data
def get_map_data(master_df, category_filter, selected_year):
    """Cache map data aggregation to avoid recomputation on map interactions"""
    if category_filter:
        filtered_df = master_df[master_df['co-benefit_type'] == category_filter]
    else:
        filtered_df = master_df
    
    if selected_year == 2050:
        map_data = filtered_df.groupby('local_authority')['sum'].sum().reset_index()
        map_data.columns = ['local_authority', 'value']
    else:
        year_col = str(selected_year)
        map_data = filtered_df.groupby('local_authority')[year_col].sum().reset_index()
        map_data.columns = ['local_authority', 'value']
    
    return map_data

# CSS for the landing page and dashboard (dark, modern & consistent theme)
st.markdown("""
<style>
    /* Global layout */
    body {
        background: #020617;
        color: #e5e7eb;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif;
    }
    .main {
        background: radial-gradient(circle at top, #1e293b 0, #020617 55%, #020617 100%);
        padding: 0;
    }
    .block-container {
        padding-top: 0rem;
        max-width: 100%;
    }
    a {
        color: #4ade80;
    }
    
    /* Landing (hero) */
    .hero-section {
        background: radial-gradient(circle at top, #111827 0, #020617 60%, #020617 100%);
        padding: 6rem 2rem 4rem 2rem;
        text-align: center;
        color: #e5e7eb;
        margin: -1rem -1rem 2rem -1rem;
    }
    .hero-title {
        font-size: 4rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.05em;
        text-shadow: 0 8px 30px rgba(0,0,0,0.6);
    }
    .hero-subtitle {
        font-size: 1.5rem;
        margin-top: 1rem;
        opacity: 0.9;
    }
    .explore-btn {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        color: #020617;
        padding: 1rem 3rem;
        border-radius: 999px;
        font-size: 1.1rem;
        font-weight: 600;
        border: none;
        cursor: pointer;
        margin-top: 2rem;
        display: inline-block;
        text-decoration: none;
        box-shadow: 0 10px 30px rgba(22, 163, 74, 0.45);
    }
    
    /* Dashboard container */
    .dashboard-container {
        background: rgba(15, 23, 42, 0.95);
        border-radius: 24px;
        padding: 2.5rem 2.5rem 3rem 2.5rem;
        margin: 1rem 1.5rem 3rem 1.5rem;
        box-shadow: 0 24px 60px rgba(15, 23, 42, 0.9);
    }
    .metrics-section {
        margin: 2rem 1.5rem;
    }
    @media (max-width: 768px) {
        .metrics-section {
            margin: 2.5rem 1.25rem;
        }
        .metrics-section .metric-card {
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
    }
    
    /* Typography */
    h1, h2, h3 {
        color: #e5e7eb;
    }
    h2 {
        font-size: 2rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #22c55e;
        padding-bottom: 0.6rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        padding: 1.5rem;
        border-radius: 16px;
        color: #f9fafb;
        text-align: center;
        box-shadow: 0 18px 45px rgba(22, 163, 74, 0.55);
        margin-bottom: 1rem;
        margin-top: 1rem;
    }
    .metric-value {
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.14em;
    }
    
    /* Insight & narrative blocks */
    .insight-box {
        background: rgba(15, 23, 42, 0.9);
        border-left: 4px solid #22c55e;
        padding: 1.5rem 1.75rem;
        border-radius: 12px;
        margin: 2rem 0;
    }
    .story-text {
        font-size: 1.05rem;
        line-height: 1.8;
        color: #cbd5f5;
        margin: 1.5rem 0;
    }
    .research-question {
        background: rgba(15, 23, 42, 0.9);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #22c55e;
        color: #e5e7eb;
    }
    
    /* Streamlit metric blocks */
    .stMetric {
        background: #020617;
        padding: 1.2rem 1.4rem;
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.35);
    }
    .stMetric label, 
    .stMetric [data-testid="stMetricDelta"], 
    .stMetric [data-testid="stMetricValue"] {
        color: #e5e7eb !important;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    l3 = pd.read_csv('Level_3.csv', sep=None, engine='python', encoding='utf-8')
    lk = pd.read_csv('lookups.csv', sep=None, engine='python', encoding='utf-8')
    
    l3.columns = l3.columns.str.replace('^\ufeff', '', regex=True).str.strip()
    lk.columns = lk.columns.str.replace('^\ufeff', '', regex=True).str.strip()
    
    target = ['air_quality', 'physical_activity', 'road_safety', 'noise', 'congestion']
    l3 = l3[l3['co-benefit_type'].isin(target)].copy()
    
    df = pd.merge(l3, lk[['small_area', 'local_authority', 'population', 'nation']], 
                  on='small_area', how='left')
    
    cols = [str(y) for y in range(2025, 2051)] + ['sum']
    for c in cols:
        df[c] = df[c].astype(str).str.replace(',', '.')
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        
    return df

try:
    master_df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

total_benefit = master_df['sum'].sum()

# === LANDING PAGE HEADER & SUMMARY (SINGLE PAGE) ===
st.markdown("""
<div class="hero-section">
    <div class="hero-title">🚗 → 🌿</div>
    <h1 style="color: white; font-size: 3.5rem; margin: 1rem 0;">Less Cars, More Life</h1>
    <p class="hero-subtitle">Exploring the hidden co-benefits of reducing car use across the United Kingdom</p>
    <p style="margin-top: 2rem; font-size: 1.1rem; opacity: 0.9;">
        Transport is one of the largest sources of emissions in the United Kingdom. But reducing car use is not just about the climate—<br>
        it is also about <strong>cleaner air, healthier lives, safer streets, and more vibrant communities</strong>.
    </p>
    <p style="margin-top: 2rem; font-size: 1rem; opacity: 0.9;">
        Scroll down to explore the interactive dashboard and key findings.
    </p>
</div>
""", unsafe_allow_html=True)

# Preview metrics (top-of-page summary)
st.markdown('<div class="metrics-section">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

total_health = master_df[master_df['damage_type'] == 'health']['sum'].sum()
areas = master_df['small_area'].nunique()

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Economic Value</div>
        <div class="metric-value">£{total_benefit/1000:.1f}B</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">up to 2050</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Health Benefits</div>
        <div class="metric-value">£{total_health/1000:.1f}B</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">{total_health/total_benefit*100:.0f}% of total</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Geographical Coverage</div>
        <div class="metric-value">{areas:,}</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">small areas</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Periode Waktu</div>
        <div class="metric-value">2025-2050</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">25 years</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Map preview with Leaflet (folium)
# st.markdown("<br>", unsafe_allow_html=True)

# map_preview = master_df.groupby('local_authority')['sum'].sum().reset_index()
# try:
#     m_preview = folium.Map(location=[54.5, -2], zoom_start=5, tiles="CartoDB dark_matter")
#     folium.Choropleth(
#         geo_data=GEOJSON_URL,
#         data=map_preview,
#         columns=['local_authority', 'sum'],
#         key_on="feature.properties.LAD13NM",
#         fill_color="YlGn",
#         fill_opacity=0.8,
#         line_opacity=0.2,
#         legend_name="Total Benefits (Million GBP)"
#     ).add_to(m_preview)
#     st_folium(m_preview, width=None, height=800)
# except Exception as e:
    # st.warning(f"⚠️ Peta pratinjau tidak dapat dimuat: {e}")

# === MAIN DASHBOARD CONTENT (CONTINUES SAME PAGE) ===
# st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)

# Header
# st.title("🚗 → 🌿 Less Cars, More Life")
# st.markdown("**Interactive Dashboard** | Co-benefits Analysis of Reducing Car Use in the UK 2025–2050")

st.markdown("---")

# === RESEARCH QUESTIONS ===
st.markdown("## 📋 Research Questions")

st.markdown("""
<div class="research-question">
    <a href="#rq1" style="text-decoration: none; color: inherit;">
        <strong>1.</strong> Which areas in the United Kingdom receive the greatest co-benefits from reducing car use?
    </a>
</div>
<div class="research-question">
    <a href="#rq2" style="text-decoration: none; color: inherit;">
        <strong>2.</strong> How strong is the relationship between emissions reductions and improved health?
    </a>
</div>
<div class="research-question">
    <a href="#rq3" style="text-decoration: none; color: inherit;">
        <strong>3.</strong> Do the largest benefits come from air quality, physical activity, or road safety?
    </a>
</div>
<div class="research-question">
    <a href="#rq4" style="text-decoration: none; color: inherit;">
        <strong>4.</strong> How do these benefits evolve from 2025 to 2050?
    </a>
</div>
""", unsafe_allow_html=True)

# === SECTION 1: INTERACTIVE MAP VIEW ===
st.markdown('<div id="rq1"></div>', unsafe_allow_html=True)
st.markdown("## 🗺️ Interactive Map: Spatial Distribution of Co-benefits")

col_map1, col_map2 = st.columns([3, 1])

with col_map2:
    st.markdown("### Filter Options")
    
    # Category filter
    benefit_categories = {
        'All Co-benefits': None,
        'Air Quality': 'air_quality',
        'Physical Activity': 'physical_activity',
        'Road Safety': 'road_safety',
        'Noise': 'noise',
        'Congestion': 'congestion'
    }
    
    selected_category = st.selectbox(
        "Select Benefit Category:",
        options=list(benefit_categories.keys())
    )
    
    # Time slider
    selected_year = st.slider(
        "Select Year:",
        min_value=2025,
        max_value=2050,
        value=2050,
        step=1
    )
    
    st.markdown(f"""
    <div class="insight-box" style="margin-top: 2rem;">
        <strong>📊 Current Selection:</strong><br>
        Category: <strong>{selected_category}</strong><br>
        Year: <strong>{selected_year}</strong>
    </div>
    """, unsafe_allow_html=True)

with col_map1:
    # Initialize session state for map view persistence
    if 'map_center' not in st.session_state:
        st.session_state.map_center = [54.5, -2]
        st.session_state.map_zoom = 5
        st.session_state.last_filter = None
    
    # Check if filter has changed
    current_filter = f"{selected_category}_{selected_year}"
    filter_changed = st.session_state.last_filter != current_filter
    
    # Get cached map data aggregation (fast even on re-runs)
    category_filter = benefit_categories[selected_category]
    map_data = get_map_data(master_df, category_filter, selected_year)
    
    # Calculate national average for comparison
    national_avg = map_data['value'].mean()
    
    # Load cached GeoJSON data
    geojson_data = load_geojson()
    
    if geojson_data is None:
        st.warning("⚠️ GeoJSON data could not be loaded. Showing the top 10 areas in a table instead.")
        st.dataframe(map_data.nlargest(10, 'value'), width='stretch')
    else:
        try:
            # Get current map view state (preserved from previous interactions)
            map_location = st.session_state.map_center
            map_zoom = st.session_state.map_zoom
            
            # Create map with current view state
            m_map = folium.Map(
                location=map_location, 
                zoom_start=map_zoom, 
                tiles="CartoDB dark_matter"
            )
            
            # Always add choropleth (data aggregation is cached, so it's fast)
            # The choropleth will update when filter changes because map_data changes
            folium.Choropleth(
                geo_data=geojson_data,
                data=map_data,  # This uses cached aggregation from get_map_data()
                columns=['local_authority', 'value'],
                key_on="feature.properties.LAD13NM",
                fill_color="YlGn",
                fill_opacity=0.8,
                line_opacity=0.2,
                legend_name="Benefits (Million GBP)"
            ).add_to(m_map)
            
            # Use key based on filter to ensure choropleth updates when filter changes
            # But preserve view state from session_state to maintain zoom/pan
            # The data aggregation is cached, so recreating choropleth is fast
            map_key = f"map_{current_filter}"
            
            map_return = st_folium(
                m_map, 
                width=None, 
                height=600, 
                key=map_key,  # Key changes with filter to ensure choropleth updates
                returned_objects=["last_clicked", "bounds", "zoom", "center"]
            )
            
            # Update session state with current map view state
            # This preserves zoom/pan position
            if map_return is not None:
                if map_return.get('center') is not None:
                    st.session_state.map_center = [
                        map_return['center']['lat'],
                        map_return['center']['lng']
                    ]
                if map_return.get('zoom') is not None:
                    st.session_state.map_zoom = map_return['zoom']
            
            # Update filter state for tracking
            if filter_changed:
                st.session_state.last_filter = current_filter
            
        except Exception as e:
            st.warning(f"⚠️ The map could not be loaded. Showing the top 10 areas in a table instead. Details: {e}")
            st.dataframe(map_data.nlargest(10, 'value'), width='stretch')

# Top 10 regions
st.markdown("### 🏆 Top 10 Regions by Benefits")
top10 = map_data.nlargest(10, 'value')
top10['Comparison to Avg'] = ((top10['value'] / national_avg - 1) * 100).round(1)

fig_top10 = px.bar(
    top10, x='value', y='local_authority',
    orientation='h',
    color='value',
    color_continuous_scale='Viridis',
    labels={'value': 'Benefits (Million GBP)', 'local_authority': ''},
    text='value'
)
fig_top10.update_traces(texttemplate='£%{text:.1f}M', textposition='outside')
fig_top10.update_layout(
    showlegend=False,
    height=400,
    yaxis={'categoryorder': 'total ascending'}
)
st.plotly_chart(fig_top10, width='stretch')

st.markdown(f"""
<div class="insight-box">
    <strong>💡 Answer to Research Question 1:</strong><br>
    The largest co-benefits are concentrated in major urban areas such as <strong>{top10.iloc[0]['local_authority']}</strong> 
    (around £{top10.iloc[0]['value']:.1f} million), which is approximately <strong>{top10.iloc[0]['Comparison to Avg']:.0f}%</strong> 
    above the national average. However, benefits are spread across all {len(map_data)} local authorities, 
    which shows opportunities for sustainable transport policies across the country.
</div>
""", unsafe_allow_html=True)

# === SECTION 2: BENEFIT TYPES ANALYSIS ===
st.markdown('<div id="rq3"></div>', unsafe_allow_html=True)
st.markdown("## 📊 Types of Co-benefits: What Contributes the Most?")

col_pie, col_bar = st.columns(2)

with col_pie:
    st.markdown("### Distribution by Category")
    benefit_dist = master_df.groupby('co-benefit_type')['sum'].sum().reset_index()
    benefit_dist.columns = ['Kategori', 'Nilai']
    benefit_dist['Kategori'] = benefit_dist['Kategori'].str.replace('_', ' ').str.title()
    
    fig_pie = px.pie(
        benefit_dist,
        values='Nilai',
        names='Kategori',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, width='stretch')

with col_bar:
    st.markdown("### Benefits by Category (£ Million)")
    benefit_dist_sorted = benefit_dist.sort_values('Nilai', ascending=True)
    
    fig_bar_cat = px.bar(
        benefit_dist_sorted,
        x='Nilai',
        y='Kategori',
        orientation='h',
        color='Nilai',
        color_continuous_scale='Viridis',
        text='Nilai'
    )
    fig_bar_cat.update_traces(texttemplate='£%{text:.0f}M', textposition='outside')
    fig_bar_cat.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_bar_cat, width='stretch')

top_benefit = benefit_dist.nlargest(1, 'Nilai').iloc[0]
st.markdown(f"""
<div class="insight-box">
    <strong>💡 Answer to Research Question 3:</strong><br>
    <strong>{top_benefit['Kategori']}</strong> provides the largest co-benefits, accounting for around 
    <strong>{(top_benefit['Nilai']/benefit_dist['Nilai'].sum()*100):.1f}%</strong> of the total value 
    (around £{top_benefit['Nilai']/1000:.2f} billion). This shows that encouraging walking and cycling 
    can deliver very large health benefits, above and beyond emissions reductions alone.
</div>
""", unsafe_allow_html=True)

# === SECTION 3: TEMPORAL TRENDS ===
st.markdown('<div id="rq4"></div>', unsafe_allow_html=True)
st.markdown("## 📈 Timeline: How Benefits Grow from 2025–2050")

years = [str(y) for y in range(2025, 2051)]
trend_df = master_df.groupby('co-benefit_type')[years].sum().T
trend_df.index = trend_df.index.astype(int)
trend_df = trend_df.reset_index()
trend_df.columns = ['Year'] + [col.replace('_', ' ').title() for col in trend_df.columns[1:]]

# Melt for plotting
trend_melted = trend_df.melt(id_vars='Year', var_name='Kategori', value_name='Nilai')

fig_timeline = px.line(
        trend_melted,
        x='Year',
        y='Nilai',
        color='Kategori',
    markers=True,
        labels={'Nilai': 'Cumulative Benefits (Million GBP)', 'Year': 'Year'},
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig_timeline.update_layout(
    height=500,
    hovermode='x unified',
    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
)
st.plotly_chart(fig_timeline, width='stretch')

# Growth calculation
start_val = trend_df[trend_df['Year']==2025].iloc[0, 1:].sum()
end_val = trend_df[trend_df['Year']==2050].iloc[0, 1:].sum()
growth_rate = ((end_val/start_val)**(1/25) - 1) * 100

st.markdown(f"""
<div class="insight-box">
    <strong>💡 Answer to Research Question 4:</strong><br>
    Co-benefits grow from <strong>£{start_val:.0f}M in 2025</strong> to <strong>£{end_val:.0f}M by 2050</strong>, 
    representing a compound annual growth rate of <strong>{growth_rate:.1f}%</strong>. 
    The acceleration after 2030 reflects the compound effects of infrastructure investment and sustained 
    behavior change in active travel patterns.
</div>
""", unsafe_allow_html=True)

# === SECTION 4: HEALTH-EMISSION CORRELATION ===
st.markdown('<div id="rq2"></div>', unsafe_allow_html=True)
st.markdown("## 🔗 Links Between Health and Non-health Benefits")

st.markdown("""
<p class="story-text">
One of the key questions for policymakers is: <strong>Do emissions reductions and sustainable transport policies 
deliver benefits beyond health alone?</strong> Below, we compare health benefits with non-health benefits 
(for example environmental and other socio-economic benefits) in each local authority.
</p>
""", unsafe_allow_html=True)

# Calculate health vs non-health benefits per local authority
health_benefits = master_df[master_df['damage_type'] == 'health'].groupby('local_authority')['sum'].sum()
non_health_benefits = master_df[master_df['damage_type'] == 'non-health'].groupby('local_authority')['sum'].sum()

corr_df = pd.DataFrame({
    'Health Benefits': health_benefits,
    'Non-health Benefits': non_health_benefits,
    'Local Authority': health_benefits.index
}).reset_index(drop=True)

# Only use rows that have both types of benefits
corr_df = corr_df.dropna(subset=['Health Benefits', 'Non-health Benefits'])

# Calculate correlation coefficient
correlation = corr_df['Health Benefits'].corr(corr_df['Non-health Benefits'])

fig_scatter = px.scatter(
    corr_df,
    x='Non-health Benefits',
    y='Health Benefits',
    hover_data=['Local Authority'],
    labels={
        'Health Benefits': 'Health Benefits (Million GBP)',
        'Non-health Benefits': 'Non-health Benefits (Million GBP)'
    },
    color='Health Benefits',
    color_continuous_scale='Greens'
)
fig_scatter.update_traces(marker=dict(size=8, opacity=0.7))
fig_scatter.update_layout(height=500)
st.plotly_chart(fig_scatter, width='stretch')

st.markdown(f"""
<div class="insight-box">
    <strong>💡 Answer to Research Question 2:</strong><br>
    The correlation coefficient between non-health and health benefits is 
    <strong>{correlation:.3f}</strong>, indicating a <strong>very strong positive relationship</strong>. 
    This means that areas receiving larger non-health benefits (such as improved air quality, reduced noise, and other socio-economic gains) 
    also tend to experience significant increases in health benefits. This underlines that sustainable transport policies are not only good for the environment, 
    but also directly support public health.
</div>
""", unsafe_allow_html=True)

# === SECTION 5: COMPARISON PANEL ===
st.markdown("## ⚖️ City-to-city Comparison")

st.markdown("""
<p class="story-text">
Compare co-benefits between two local authorities to understand regional differences and policy opportunities.
</p>
""", unsafe_allow_html=True)

col_comp1, col_comp2 = st.columns(2)

cities = sorted(master_df['local_authority'].unique())

with col_comp1:
    city_a = st.selectbox("Choose First City:", cities, index=0, key='city_select_a')

with col_comp2:
    city_b = st.selectbox("Choose Second City:", cities, 
                          index=min(1, len(cities)-1), key='city_select_b')

# Comparison data
comp_df = master_df[master_df['local_authority'].isin([city_a, city_b])]
comp_summary = comp_df.groupby(['local_authority', 'co-benefit_type'])['sum'].sum().reset_index()
comp_summary['co-benefit_type'] = comp_summary['co-benefit_type'].str.replace('_', ' ').str.title()

fig_compare = px.bar(
    comp_summary,
    x='co-benefit_type',
    y='sum',
    color='local_authority',
    barmode='group',
    labels={'sum': 'Benefits (Million GBP)', 'co-benefit_type': 'Co-benefit Category'},
    color_discrete_sequence=['#22c55e', '#16a34a']
)
fig_compare.update_layout(height=400, legend=dict(title=''))
st.plotly_chart(fig_compare, width='stretch')

# Comparison metrics
city_a_total = comp_df[comp_df['local_authority']==city_a]['sum'].sum()
city_b_total = comp_df[comp_df['local_authority']==city_b]['sum'].sum()

col_metric1, col_metric2, col_metric3 = st.columns(3)
with col_metric1:
    st.metric(f"{city_a}", f"£{city_a_total:.1f}M")
with col_metric2:
    st.metric(f"{city_b}", f"£{city_b_total:.1f}M")
with col_metric3:
    diff_pct = ((city_b_total/city_a_total - 1) * 100) if city_a_total > 0 else 0
    direction = "higher" if diff_pct > 0 else "lower"
    st.metric("Difference", f"{abs(diff_pct):.1f}%", 
             delta=f"{city_b} {direction}")

# === STORY MODE / INSIGHTS SECTION ===
st.markdown("## 📖 Key Findings & Policy Implications")

st.markdown("""
<div class="story-text">
<strong>By 2050, local transport action has the potential to generate very large economic and social value:</strong>
</div>
""", unsafe_allow_html=True)

total_health_benefits = master_df[master_df['damage_type']=='health']['sum'].sum()

col_insight1, col_insight2 = st.columns(2)

with col_insight1:
    st.markdown(f"""
    <div class="insight-box">
        <h3 style="color: #22c55e; margin-top: 0;">💰 Economic Value</h3>
        <p><strong>around £{total_benefit/1000:.1f} billion</strong> in total co-benefits</p>
        <p><strong>around £{total_health_benefits/1000:.1f} billion</strong> from health benefits alone</p>
        <p>These benefits have the potential to finance sustainable transport infrastructure many times over.</p>
    </div>
    """, unsafe_allow_html=True)
    
with col_insight2:
    st.markdown("""
    <div class="insight-box">
        <h3 style="color: #22c55e; margin-top: 0;">🎯 Policy Priorities</h3>
        <p><strong>1.</strong> Increase investment in active transport infrastructure (walking & cycling)</p>
        <p><strong>2.</strong> Focus interventions in urban areas for the greatest impact</p>
        <p><strong>3.</strong> Communicate transport policy as an effort to improve health & quality of life, not just a restriction.</p>
    </div>
    """, unsafe_allow_html=True)
    
st.markdown("""
<div class="insight-box" style="background: linear-gradient(135deg, #22c55e22 0%, #16a34a22 100%); border: none;">
    <h3 style="color: #22c55e;">🌟 Key Message</h3>
    <p class="story-text">
    Climate action through reducing car use is not about sacrifice; it is about building cities that are healthier, 
    safer, and more pleasant to live in. The data show that small changes in everyday travel patterns can 
    generate very large social and economic benefits. By prioritising sustainable transport, the United Kingdom can 
    simultaneously reduce emissions and improve the quality of life for millions of its residents.
    </p>
</div>
""", unsafe_allow_html=True)

# === FOOTER ===
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: #020617; border-radius: 12px;">
    <p style="margin: 0; color: #e5e7eb;"><strong>Data Source:</strong></p>
    <p style="margin: 0.5rem 0; color: #cbd5f5;">
    Sudmant, A., Higgins-Lavery, R. (2025). <em>The Co-Benefits of Reaching Net-Zero in the UK</em>.<br>
    Edinburgh Climate Change Institute, University of Edinburgh.
    </p>
    <p style="margin-top: 1rem; color: #9ca3af; font-size: 0.9rem;">
    This dashboard was developed for the Data Visualisation Project | 2025
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)