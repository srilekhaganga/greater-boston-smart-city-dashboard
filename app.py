# Greater Boston Smart City Dashboard - Complete Implementation with Simulated Data

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import folium_static
import time
from datetime import datetime, timedelta
import logging
import random
from typing import Dict, List, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================
# 1. GREATER BOSTON CONFIGURATION
# ================================

class BostonConfig:
    """Configuration for Greater Boston Smart City Dashboard"""
    
    # Geographic boundaries for Greater Boston
    BOSTON_BOUNDS = {
        "center": [42.3601, -71.0589],  # Boston City Hall
        "north": 42.4820,   # Medford/Malden
        "south": 42.2279,   # Quincy/Braintree  
        "east": -70.9239,   # East Boston/Logan
        "west": -71.3683    # Newton/Waltham
    }
    
    # Major Boston Traffic Monitoring Locations
    TRAFFIC_LOCATIONS = [
        # Downtown Boston
        {"name": "Downtown Crossing", "lat": 42.3555, "lon": -71.0604, "neighborhood": "Downtown"},
        {"name": "Government Center", "lat": 42.3594, "lon": -71.0587, "neighborhood": "Downtown"},
        {"name": "Financial District", "lat": 42.3583, "lon": -71.0552, "neighborhood": "Downtown"},
        {"name": "Back Bay Station", "lat": 42.3477, "lon": -71.0752, "neighborhood": "Back Bay"},
        {"name": "Copley Square", "lat": 42.3495, "lon": -71.0773, "neighborhood": "Back Bay"},
        
        # Major Bridges & Highways
        {"name": "Tobin Bridge", "lat": 42.3823, "lon": -71.0370, "neighborhood": "North End"},
        {"name": "Zakim Bridge", "lat": 42.3679, "lon": -71.0611, "neighborhood": "North End"},
        {"name": "Mass Ave Bridge", "lat": 42.3530, "lon": -71.0919, "neighborhood": "Back Bay"},
        {"name": "Longfellow Bridge", "lat": 42.3611, "lon": -71.0758, "neighborhood": "Beacon Hill"},
        {"name": "I-93 South", "lat": 42.3301, "lon": -71.0589, "neighborhood": "South End"},
        {"name": "I-90 (Mass Pike)", "lat": 42.3467, "lon": -71.0972, "neighborhood": "Fenway"},
        {"name": "Route 1 North", "lat": 42.3756, "lon": -71.0342, "neighborhood": "Charlestown"},
        
        # Cambridge
        {"name": "Harvard Square", "lat": 42.3744, "lon": -71.1190, "neighborhood": "Cambridge"},
        {"name": "Kendall Square", "lat": 42.3625, "lon": -71.0861, "neighborhood": "Cambridge"},
        {"name": "Porter Square", "lat": 42.3884, "lon": -71.1192, "neighborhood": "Cambridge"},
        {"name": "Lechmere", "lat": 42.3701, "lon": -71.0761, "neighborhood": "Cambridge"},
        
        # Other Areas
        {"name": "Logan Airport", "lat": 42.3656, "lon": -71.0096, "neighborhood": "East Boston"},
        {"name": "Fenway Park", "lat": 42.3467, "lon": -71.0972, "neighborhood": "Fenway"},
        {"name": "TD Garden", "lat": 42.3662, "lon": -71.0621, "neighborhood": "North End"},
        {"name": "Brookline Village", "lat": 42.3326, "lon": -71.1205, "neighborhood": "Brookline"},
        {"name": "Newton Centre", "lat": 42.3292, "lon": -71.1925, "neighborhood": "Newton"},
        {"name": "Quincy Center", "lat": 42.2519, "lon": -71.0052, "neighborhood": "Quincy"}
    ]
    
    # MBTA Lines and Key Stations
    MBTA_LINES = {
        "Red": {
            "color": "#DA020E",
            "stations": ["Braintree", "Quincy Center", "South Station", "Park Street", 
                        "Harvard", "Porter", "Alewife"]
        },
        "Orange": {
            "color": "#ED8B00", 
            "stations": ["Forest Hills", "Back Bay", "Downtown Crossing", 
                        "State", "North Station", "Oak Grove"]
        },
        "Blue": {
            "color": "#003DA5",
            "stations": ["Wonderland", "Airport", "Maverick", "State", 
                        "Government Center", "Bowdoin"]
        },
        "Green-B": {
            "color": "#00843D",
            "stations": ["Boston College", "Cleveland Circle", "Kenmore", 
                        "Park Street", "Government Center"]
        },
        "Green-C": {
            "color": "#00843D",
            "stations": ["Cleveland Circle", "Coolidge Corner", "Kenmore", 
                        "Park Street", "North Station"]
        },
        "Green-D": {
            "color": "#00843D",
            "stations": ["Riverside", "Newton Highlands", "Brookline Hills", 
                        "Kenmore", "Park Street", "North Station"]
        },
        "Green-E": {
            "color": "#00843D",
            "stations": ["Heath Street", "Northeastern", "Back Bay", 
                        "Park Street", "North Station"]
        }
    }
    
    # Air Quality Monitoring Stations
    AQI_STATIONS = [
        {"name": "Boston Common", "lat": 42.3549, "lon": -71.0649, "type": "urban_park"},
        {"name": "Harvard University", "lat": 42.3770, "lon": -71.1167, "type": "institutional"},
        {"name": "Logan Airport", "lat": 42.3656, "lon": -71.0096, "type": "transportation"},
        {"name": "I-93 Corridor", "lat": 42.3301, "lon": -71.0589, "type": "highway"},
        {"name": "Financial District", "lat": 42.3583, "lon": -71.0552, "type": "business"},
        {"name": "Cambridge Riverside", "lat": 42.3601, "lon": -71.0942, "type": "residential"},
        {"name": "Brookline Hills", "lat": 42.3319, "lon": -71.1289, "type": "suburban"},
        {"name": "Quincy Adams", "lat": 42.2331, "lon": -71.0070, "type": "suburban"}
    ]

config = BostonConfig()

# ================================
# 2. DATA SIMULATION CLASSES
# ================================

class BostonDataSimulator:
    """Simulates realistic Boston-area data based on actual patterns"""
    
    def __init__(self):
        self.current_time = datetime.now()
        np.random.seed(int(self.current_time.timestamp()) % 1000)
    
    def simulate_mbta_data(self) -> pd.DataFrame:
        """Simulate MBTA real-time vehicle data"""
        vehicles = []
        
        for line_name, line_data in config.MBTA_LINES.items():
            # Number of vehicles per line (Red/Orange have more)
            if line_name in ["Red", "Orange"]:
                num_vehicles = random.randint(15, 25)
            elif line_name == "Blue":
                num_vehicles = random.randint(8, 12)
            else:  # Green line branches
                num_vehicles = random.randint(6, 10)
            
            for i in range(num_vehicles):
                # Current location (random station on the line)
                current_station = random.choice(line_data["stations"])
                
                # Realistic delay patterns
                base_delay = 0
                hour = self.current_time.hour
                
                # Rush hour delays (7-9 AM, 5-7 PM)
                if 7 <= hour <= 9 or 17 <= hour <= 19:
                    base_delay = np.random.normal(3, 2)  # Average 3 min delay
                elif 10 <= hour <= 16:
                    base_delay = np.random.normal(1, 1)  # Light delays
                else:
                    base_delay = np.random.normal(0.5, 0.5)  # Minimal delays
                
                delay = max(0, base_delay)
                
                # Crowding levels
                if 7 <= hour <= 9 or 17 <= hour <= 19:
                    crowding = random.choice(["MANY_SEATS_AVAILABLE", "FEW_SEATS_AVAILABLE", 
                                            "STANDING_ROOM_ONLY", "CRUSHED_STANDING_ROOM_ONLY"], 
                                           weights=[0.1, 0.3, 0.4, 0.2])
                else:
                    crowding = random.choice(["MANY_SEATS_AVAILABLE", "FEW_SEATS_AVAILABLE", 
                                            "STANDING_ROOM_ONLY"], weights=[0.5, 0.4, 0.1])
                
                vehicles.append({
                    "vehicle_id": f"{line_name.replace('-', '_')}_train_{i+1}",
                    "line": line_name,
                    "direction": random.choice(["Inbound", "Outbound"]),
                    "current_station": current_station,
                    "delay_minutes": round(delay, 1),
                    "crowding_level": crowding,
                    "speed_mph": random.uniform(15, 35),
                    "timestamp": self.current_time,
                    "status": random.choice(["On Time", "Delayed", "Approaching"], weights=[0.6, 0.3, 0.1])
                })
        
        return pd.DataFrame(vehicles)
    
    def simulate_traffic_data(self) -> pd.DataFrame:
        """Simulate realistic Boston traffic data"""
        traffic_data = []
        hour = self.current_time.hour
        is_weekday = self.current_time.weekday() < 5
        
        for location in config.TRAFFIC_LOCATIONS:
            # Base congestion varies by location type and time
            base_congestion = 0.2
            
            # Time-based patterns
            if is_weekday:
                if 7 <= hour <= 9:  # Morning rush
                    base_congestion += 0.5
                elif 17 <= hour <= 19:  # Evening rush
                    base_congestion += 0.6
                elif 10 <= hour <= 16:  # Business hours
                    base_congestion += 0.3
                elif 20 <= hour <= 22:  # Evening activity
                    base_congestion += 0.2
            else:  # Weekend
                if 11 <= hour <= 15:  # Weekend activity
                    base_congestion += 0.3
                elif 19 <= hour <= 23:  # Weekend nightlife
                    base_congestion += 0.4
            
            # Location-specific adjustments
            location_multiplier = 1.0
            if "Bridge" in location["name"]:
                location_multiplier = 1.3  # Bridges are bottlenecks
            elif location["name"] in ["Harvard Square", "Kendall Square", "Downtown Crossing"]:
                location_multiplier = 1.2  # High activity areas
            elif "Airport" in location["name"]:
                location_multiplier = 1.1  # Airport traffic
            elif location["neighborhood"] in ["Newton", "Brookline", "Quincy"]:
                location_multiplier = 0.8  # Suburban areas
            
            congestion = min(1.0, (base_congestion * location_multiplier + np.random.normal(0, 0.1)))
            congestion = max(0.0, congestion)
            
            # Derived metrics
            avg_speed = 35 * (1 - congestion)  # Speed inversely related to congestion
            incident_count = np.random.poisson(congestion * 2)
            delay_minutes = congestion * 15
            
            # Special events (Red Sox, Bruins, etc.)
            special_event = None
            if location["name"] == "Fenway Park" and random.random() < 0.1:
                special_event = "Red Sox Game"
                congestion = min(1.0, congestion + 0.3)
            elif location["name"] == "TD Garden" and random.random() < 0.1:
                special_event = "Bruins/Celtics Game"
                congestion = min(1.0, congestion + 0.3)
            
            traffic_data.append({
                "location": location["name"],
                "neighborhood": location["neighborhood"],
                "latitude": location["lat"],
                "longitude": location["lon"],
                "congestion_index": round(congestion, 3),
                "average_speed_mph": round(avg_speed, 1),
                "incident_count": incident_count,
                "delay_minutes": round(delay_minutes, 1),
                "timestamp": self.current_time,
                "special_event": special_event,
                "traffic_volume": random.randint(500, 3000)  # Vehicles per hour
            })
        
        return pd.DataFrame(traffic_data)
    
    def simulate_air_quality_data(self) -> pd.DataFrame:
        """Simulate Boston air quality data"""
        aqi_data = []
        
        for station in config.AQI_STATIONS:
            # Base AQI varies by location type
            base_aqi = {
                "urban_park": 40,
                "suburban": 35,
                "residential": 45,
                "business": 55,
                "highway": 65,
                "transportation": 70,
                "institutional": 40
            }.get(station["type"], 50)
            
            # Time and weather adjustments
            hour = self.current_time.hour
            if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hour pollution
                base_aqi += random.randint(10, 25)
            
            # Weather impact simulation
            weather_impact = random.choice([
                {"condition": "Clear", "modifier": 0},
                {"condition": "Partly Cloudy", "modifier": 5},
                {"condition": "Overcast", "modifier": 10},
                {"condition": "Light Rain", "modifier": -15},  # Rain cleans air
                {"condition": "Windy", "modifier": -10}  # Wind disperses pollution
            ])
            
            aqi = max(0, min(300, base_aqi + weather_impact["modifier"] + random.randint(-10, 15)))
            
            # AQI Category
            if aqi <= 50:
                category, color = "Good", "green"
            elif aqi <= 100:
                category, color = "Moderate", "yellow" 
            elif aqi <= 150:
                category, color = "Unhealthy for Sensitive Groups", "orange"
            elif aqi <= 200:
                category, color = "Unhealthy", "red"
            else:
                category, color = "Very Unhealthy", "purple"
            
            # Individual pollutants
            pm25 = round(aqi * 0.4 + random.uniform(-5, 5), 1)
            pm10 = round(aqi * 0.7 + random.uniform(-8, 8), 1)
            no2 = round(random.uniform(10, 50), 1)
            o3 = round(random.uniform(15, 80), 1)
            
            aqi_data.append({
                "station": station["name"],
                "station_type": station["type"],
                "latitude": station["lat"],
                "longitude": station["lon"],
                "aqi": round(aqi),
                "category": category,
                "color": color,
                "pm25": pm25,
                "pm10": pm10,
                "no2": no2,
                "o3": o3,
                "weather_condition": weather_impact["condition"],
                "timestamp": self.current_time
            })
        
        return pd.DataFrame(aqi_data)
    
    def simulate_energy_data(self) -> Dict:
        """Simulate Boston-area energy consumption data"""
        hour = self.current_time.hour
        is_weekday = self.current_time.weekday() < 5
        
        # Base load (MW)
        base_load = 2500
        
        # Demand patterns
        if is_weekday:
            if 8 <= hour <= 18:  # Business hours
                demand_multiplier = 1.3
            elif 6 <= hour <= 8 or 18 <= hour <= 22:  # Peak residential
                demand_multiplier = 1.4
            else:  # Off-peak
                demand_multiplier = 0.8
        else:  # Weekend
            if 10 <= hour <= 16:  # Weekend day
                demand_multiplier = 1.1
            elif 18 <= hour <= 23:  # Weekend evening
                demand_multiplier = 1.2
            else:
                demand_multiplier = 0.9
        
        # Weather impact (heating/cooling)
        temp = random.uniform(15, 30)  # Celsius
        if temp > 27:  # Hot day, more AC
            demand_multiplier += 0.2
        elif temp < 5:  # Cold day, more heating
            demand_multiplier += 0.15
        
        total_demand = base_load * demand_multiplier + random.uniform(-100, 100)
        
        # Energy mix for New England
        renewable_pct = random.uniform(0.25, 0.40)  # 25-40% renewable
        nuclear_pct = random.uniform(0.20, 0.30)
        gas_pct = random.uniform(0.35, 0.45)
        other_pct = 1 - (renewable_pct + nuclear_pct + gas_pct)
        
        return {
            "total_demand_mw": round(total_demand, 1),
            "renewable_percentage": round(renewable_pct, 3),
            "nuclear_percentage": round(nuclear_pct, 3),
            "natural_gas_percentage": round(gas_pct, 3),
            "other_percentage": round(other_pct, 3),
            "grid_frequency": round(60.0 + random.uniform(-0.05, 0.05), 3),
            "peak_load_ratio": round(total_demand / (base_load * 1.5), 3),
            "outage_count": random.randint(0, 5),
            "temperature_f": round(temp * 9/5 + 32, 1)
        }

# ================================
# 3. MAIN STREAMLIT APPLICATION
# ================================

def main():
    # Page configuration
    st.set_page_config(
        page_title="Greater Boston Smart City Analytics",
        page_icon="🏙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 1rem;
        }
        .boston-subtitle {
            font-size: 1.2rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
            margin-bottom: 1rem;
        }
        .alert-high { border-left-color: #dc3545; }
        .alert-medium { border-left-color: #fd7e14; }
        .alert-low { border-left-color: #28a745; }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🏙️ Greater Boston Smart City Dashboard</h1>', 
                unsafe_allow_html=True)
    st.markdown('<p class="boston-subtitle">Real-time Analytics for Cambridge • Boston • Brookline • Newton • Quincy</p>', 
                unsafe_allow_html=True)
    
    # Initialize data simulator
    simulator = BostonDataSimulator()
    
    # Sidebar
    with st.sidebar:
        st.title("🗺️ Navigation")
        
        module = st.selectbox(
            "Select Module",
            ["🏠 Overview", "🚦 Traffic Analysis", "🚇 MBTA Transit", 
             "🌱 Air Quality", "⚡ Energy Grid", "📊 Analytics"]
        )
        
        time_range = st.selectbox(
            "Time Range",
            ["Real-time", "Last Hour", "Last 24 Hours", "Last Week"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### 🎯 Quick Stats")
        
        # Quick metrics in sidebar
        traffic_data = simulator.simulate_traffic_data()
        mbta_data = simulator.simulate_mbta_data()
        avg_congestion = traffic_data['congestion_index'].mean()
        avg_delay = mbta_data['delay_minutes'].mean()
        
        st.metric("Avg Traffic Congestion", f"{avg_congestion:.1%}")
        st.metric("Avg MBTA Delay", f"{avg_delay:.1f} min")
        
        # Auto-refresh option
        auto_refresh = st.checkbox("Auto Refresh (30s)", value=False)
        if st.button("🔄 Refresh Now"):
            st.experimental_rerun()
    
    # Display selected module
    if module == "🏠 Overview":
        display_overview(simulator)
    elif module == "🚦 Traffic Analysis":
        display_traffic_analysis(simulator)
    elif module == "🚇 MBTA Transit":
        display_mbta_analysis(simulator)
    elif module == "🌱 Air Quality":
        display_air_quality_analysis(simulator)
    elif module == "⚡ Energy Grid":
        display_energy_analysis(simulator)
    elif module == "📊 Analytics":
        display_advanced_analytics(simulator)
    
    # Footer
    st.markdown("---")
    st.markdown("### 📋 Data Sources")
    st.markdown("""
    **Simulated data based on:**
    - MBTA V3 API patterns
    - MassDOT traffic data
    - EPA AirNow structure  
    - ISO New England grid data
    - Boston Open Data formats
    """)

# ================================
# 4. MODULE IMPLEMENTATIONS
# ================================

def display_overview(simulator):
    """Main overview dashboard"""
    st.header("🏠 Greater Boston Overview")
    
    # Get current data
    traffic_data = simulator.simulate_traffic_data()
    mbta_data = simulator.simulate_mbta_data()
    aqi_data = simulator.simulate_air_quality_data()
    energy_data = simulator.simulate_energy_data()
    
    # KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_congestion = traffic_data['congestion_index'].mean()
        st.metric(
            "Traffic Flow", 
            f"{(1-avg_congestion):.1%}",
            f"{random.uniform(-0.05, 0.03):.1%}"
        )
        st.caption("🟢 Good" if avg_congestion < 0.5 else "🟡 Fair" if avg_congestion < 0.7 else "🔴 Heavy")
    
    with col2:
        on_time_pct = len(mbta_data[mbta_data['delay_minutes'] <= 2]) / len(mbta_data)
        st.metric(
            "MBTA On-Time", 
            f"{on_time_pct:.1%}",
            f"{random.uniform(-0.03, 0.05):.1%}"
        )
        st.caption("🟢 Excellent" if on_time_pct > 0.9 else "🟡 Good" if on_time_pct > 0.8 else "🔴 Poor")
    
    with col3:
        avg_aqi = aqi_data['aqi'].mean()
        st.metric(
            "Air Quality", 
            f"{avg_aqi:.0f} AQI",
            f"{random.randint(-5, 3)}"
        )
        st.caption("🟢 Good" if avg_aqi <= 50 else "🟡 Moderate" if avg_aqi <= 100 else "🔴 Unhealthy")
    
    with col4:
        st.metric(
            "Energy Demand", 
            f"{energy_data['total_demand_mw']:.0f} MW",
            f"{random.uniform(-50, 50):.0f} MW"
        )
        st.caption(f"🔋 {energy_data['renewable_percentage']:.1%} Renewable")
    
    with col5:
        satisfaction = random.uniform(3.8, 4.6)
        st.metric(
            "Citizen Score", 
            f"{satisfaction:.1f}/5.0",
            f"{random.uniform(-0.1, 0.2):.1f}"
        )
        st.caption("🟢 High" if satisfaction > 4.2 else "🟡 Good")
    
    st.markdown("---")
    
    # Interactive Map
    st.subheader("🗺️ Live Greater Boston Conditions")
    boston_map = create_boston_overview_map(traffic_data, aqi_data)
    folium_static(boston_map, width=1200, height=500)
    
    # Trends and Alerts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Traffic Patterns Today")
        display_traffic_trends()
    
    with col2:
        st.subheader("🚇 MBTA Performance")
        display_mbta_performance_chart(mbta_data)

def display_traffic_analysis(simulator):
    """Detailed traffic analysis for Greater Boston"""
    st.header("🚦 Greater Boston Traffic Analysis")
    
    traffic_data = simulator.simulate_traffic_data()
    
    # Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        neighborhood_filter = st.selectbox(
            "Neighborhood", 
            ["All"] + sorted(traffic_data['neighborhood'].unique())
        )
    with col2:
        congestion_threshold = st.slider("Alert Threshold", 0.0, 1.0, 0.6, 0.1)
    with col3:
        show_events = st.checkbox("Show Special Events", True)
    
    # Filter data
    if neighborhood_filter != "All":
        traffic_data = traffic_data[traffic_data['neighborhood'] == neighborhood_filter]
    
    # Traffic map
    st.subheader("🗺️ Real-time Traffic Conditions")
    traffic_map = create_traffic_map(traffic_data, show_events)
    folium_static(traffic_map, width=1200, height=500)
    
    # Metrics and Analysis
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Congestion by neighborhood
        st.subheader("📊 Congestion by Area")
        neighborhood_stats = traffic_data.groupby('neighborhood').agg({
            'congestion_index': 'mean',
            'average_speed_mph': 'mean',
            'incident_count': 'sum'
        }).round(3)
        
        fig_neighborhoods = px.bar(
            x=neighborhood_stats.index,
            y=neighborhood_stats['congestion_index'],
            title="Average Congestion by Neighborhood",
            labels={'x': 'Neighborhood', 'y': 'Congestion Index'}
        )
        fig_neighborhoods.add_hline(y=congestion_threshold, line_dash="dash", line_color="red")
        st.plotly_chart(fig_neighborhoods, use_container_width=True)
    
    with col2:
        # Hotspots
        st.subheader("🔥 Current Hotspots")
        hotspots = traffic_data[traffic_data['congestion_index'] >= congestion_threshold].sort_values(
            'congestion_index', ascending=False
        )
        
        if len(hotspots) > 0:
            for _, spot in hotspots.head(5).iterrows():
                severity = "🔴" if spot['congestion_index'] > 0.8 else "🟡"
                st.markdown(f"""
                **{severity} {spot['location']}**  
                📍 {spot['neighborhood']}  
                🚗 {spot['congestion_index']:.1%} congestion  
                ⚡ {spot['average_speed_mph']:.0f} mph avg speed  
                """)
                if spot['special_event']:
                    st.caption(f"🎉 {spot['special_event']}")
                st.markdown("---")
        else:
            st.success("✅ No major congestion hotspots!")

def display_mbta_analysis(simulator):
    """MBTA transit analysis"""
    st.header("🚇 MBTA Real-time Analysis")
    
    mbta_data = simulator.simulate_mbta_data()
    
    # MBTA Performance Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_vehicles = len(mbta_data)
        st.metric("Active Vehicles", total_vehicles)
    
    with col2:
        on_time = len(mbta_data[mbta_data['delay_minutes'] <= 2])
        st.metric("On-Time Performance", f"{on_time/total_vehicles:.1%}")
    
    with col3:
        avg_delay = mbta_data['delay_minutes'].mean()
        st.metric("Average Delay", f"{avg_delay:.1f} min")
    
    with col4:
        delayed_trains = len(mbta_data[mbta_data['delay_minutes'] > 5])
        st.metric("Major Delays (>5min)", delayed_trains)
    
    # Line Performance
    st.subheader("🚇 Performance by MBTA Line")
    
    line_stats = mbta_data.groupby('line').agg({
        'delay_minutes': ['mean', 'count'],
        'speed_mph': 'mean'
    }).round(2)
    
    line_stats.columns = ['Avg Delay (min)', 'Vehicle Count', 'Avg Speed (mph)']
    
    # Color code by line
    line_colors = {line: data['color'] for line, data in config.MBTA_LINES.items()}
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_delay = px.bar(
            x=line_stats.index,
            y=line_stats['Avg Delay (min)'],
            title="Average Delay by MBTA Line",
            color=line_stats.index,
            color_discrete_map=line_colors
        )
        st.plotly_chart(fig_delay, use_container_width=True)
    
    with col2:
        fig_crowding = px.pie(
            mbta_data.groupby('crowding_level').size().reset_index(name='count'),
            values='count',
            names='crowding_level',
            title="Current Crowding Levels"
        )
        st.plotly_chart(fig_crowding, use_container_width=True)
    
    # Line Details
    st.subheader("📋 Line Status Details")
    for line in mbta_data['line'].unique():
        line_data = mbta_data[mbta_data['line'] == line]
        avg_delay = line_data['delay_minutes'].mean()
        
        status = "🟢" if avg_delay <= 2 else "🟡" if avg_delay <= 5 else "🔴"
        
        with st.expander(f"{status} {line} Line - {len(line_data)} vehicles"):
            st.dataframe(line_data[['vehicle_id', 'current_station', 'direction', 
                                  'delay_minutes', 'crowding_level', 'status']])

def display_air_quality_analysis(simulator):
    """Air quality analysis for Greater Boston"""
    st.header("🌱 Greater Boston Air Quality")
    
    aqi_data = simulator.simulate_air_quality_data()
    
    # AQI Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_aqi = aqi_data['aqi'].mean()
        st.metric("Average AQI", f"{avg_aqi:.0f}")
    
    with col2:
        good_stations = len(aqi_data[aqi_data['aqi'] <= 50])
        st.metric("Good Quality Stations", f"{good_stations}/{len(aqi_data)}")
    
    with col3:
        max_aqi = aqi_data['aqi'].max()
        worst_station = aqi_data[aqi_data['aqi'] == max_aqi]['station'].iloc[0]
        st.metric("Highest AQI", f"{max_aqi:.0f}")
        st.caption(f"📍 {worst_station}")
    
    with col4:
        avg_pm25 = aqi_data['pm25'].mean()
        st.metric("Avg PM2.5", f"{avg_pm25:.1f} μg/m³")
    
    # Air Quality Map
    st.subheader("🗺️ Air Quality Monitoring Stations")
    aqi_map = create_aqi_map(aqi_data)
    folium_static(aqi_map, width=1200, height=500)
    
    # Detailed Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 AQI Distribution")
        fig_aqi = px.bar(
            aqi_data.groupby('category').size().reset_index(name='count'),
            x='category', y='count',
            title="Stations by AQI Category",
            color='category',
            color_discrete_map={
                'Good': 'green', 'Moderate': 'yellow', 
                'Unhealthy for Sensitive Groups': 'orange',
                'Unhealthy': 'red', 'Very Unhealthy': 'purple'
            }
        )
        st.plotly_chart(fig_aqi, use_container_width=True)
    
    with col2:
        st.subheader("🌡️ Pollutant Levels")
        pollutant_data = aqi_data[['station', 'pm25', 'pm10', 'no2', 'o3']].set_index('station')
        fig_pollutants = px.line(
            pollutant_data.T,
            title="Pollutant Levels by Station"
        )
        st.plotly_chart(fig_pollutants, use_container_width=True)

def display_energy_analysis(simulator):
    """Energy grid analysis"""
    st.header("⚡ Greater Boston Energy Grid")
    
    energy_data = simulator.simulate_energy_data()
    
    # Energy Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Demand", f"{energy_data['total_demand_mw']:.0f} MW")
    
    with col2:
        st.metric("Renewable %", f"{energy_data['renewable_percentage']:.1%}")
    
    with col3:
        st.metric("Grid Frequency", f"{energy_data['grid_frequency']:.2f} Hz")
    
    with col4:
        st.metric("Active Outages", energy_data['outage_count'])
    
    # Energy Mix
    st.subheader("🔋 Current Energy Generation Mix")
    
    energy_mix = pd.DataFrame({
        'Source': ['Renewable', 'Nuclear', 'Natural Gas', 'Other'],
        'Percentage': [
            energy_data['renewable_percentage'],
            energy_data['nuclear_percentage'], 
            energy_data['natural_gas_percentage'],
            energy_data['other_percentage']
        ]
    })
    
    fig_energy = px.pie(
        energy_mix,
        values='Percentage',
        names='Source',
        title="Energy Generation by Source"
    )
    st.plotly_chart(fig_energy, use_container_width=True)
    
    # Demand Pattern (simulated 24-hour)
    st.subheader("📈 Daily Demand Pattern")
    hours = list(range(24))
    demand_pattern = []
    
    for hour in hours:
        base_demand = 2500
        if 8 <= hour <= 18:  # Business hours
            multiplier = 1.3
        elif 6 <= hour <= 8 or 18 <= hour <= 22:  # Peak
            multiplier = 1.4
        else:
            multiplier = 0.8
        demand_pattern.append(base_demand * multiplier + random.uniform(-100, 100))
    
    fig_demand = px.line(
        x=hours, y=demand_pattern,
        title="24-Hour Demand Forecast (MW)",
        labels={'x': 'Hour', 'y': 'Demand (MW)'}
    )
    st.plotly_chart(fig_demand, use_container_width=True)

def display_advanced_analytics(simulator):
    """Advanced analytics and predictions"""
    st.header("📊 Advanced Analytics & Insights")
    
    # Generate all data
    traffic_data = simulator.simulate_traffic_data()
    mbta_data = simulator.simulate_mbta_data()
    aqi_data = simulator.simulate_air_quality_data()
    
    st.subheader("🎯 Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚦 Traffic Insights")
        
        # Correlations
        bridge_congestion = traffic_data[traffic_data['location'].str.contains('Bridge')]['congestion_index'].mean()
        other_congestion = traffic_data[~traffic_data['location'].str.contains('Bridge')]['congestion_index'].mean()
        
        st.write(f"• Bridges have {(bridge_congestion/other_congestion - 1):.1%} higher congestion")
        
        # Event impact
        event_locations = traffic_data[traffic_data['special_event'].notna()]
        if len(event_locations) > 0:
            st.write(f"• {len(event_locations)} locations affected by special events")
        
        # Neighborhood analysis
        worst_neighborhood = traffic_data.groupby('neighborhood')['congestion_index'].mean().idxmax()
        st.write(f"• Highest congestion: {worst_neighborhood}")
    
    with col2:
        st.markdown("#### 🚇 Transit Insights")
        
        # Line performance
        best_line = mbta_data.groupby('line')['delay_minutes'].mean().idxmin()
        worst_line = mbta_data.groupby('line')['delay_minutes'].mean().idxmax()
        
        st.write(f"• Best performing line: {best_line}")
        st.write(f"• Most delayed line: {worst_line}")
        
        # Crowding analysis
        crowded_pct = len(mbta_data[mbta_data['crowding_level'].str.contains('STANDING')]) / len(mbta_data)
        st.write(f"• {crowded_pct:.1%} of vehicles have standing room only")
    
    # Correlation Analysis
    st.subheader("🔗 Cross-System Correlations")
    
    # Simulate correlations
    correlations = pd.DataFrame({
        'Metric Pair': [
            'Traffic Congestion vs Air Quality',
            'MBTA Delays vs Traffic Congestion', 
            'Air Quality vs Weather Conditions',
            'Energy Demand vs Time of Day'
        ],
        'Correlation': [0.72, 0.58, -0.43, 0.89],
        'Significance': ['Strong', 'Moderate', 'Moderate', 'Very Strong']
    })
    
    st.dataframe(correlations, use_container_width=True)
    
    # Recommendations
    st.subheader("💡 Recommendations")
    
    recommendations = [
        "🚦 **Traffic**: Implement dynamic signal timing on Mass Ave Bridge during peak hours",
        "🚇 **Transit**: Increase Red Line frequency during morning rush (7-9 AM)",
        "🌱 **Environment**: Monitor I-93 corridor air quality during high traffic periods",
        "⚡ **Energy**: Prepare for peak demand during extreme weather events",
        "📱 **Citizens**: Promote real-time transit apps to reduce wait times"
    ]
    
    for rec in recommendations:
        st.markdown(rec)

# ================================
# 5. MAP CREATION FUNCTIONS
# ================================

def create_boston_overview_map(traffic_data, aqi_data):
    """Create comprehensive Boston overview map"""
    m = folium.Map(location=config.BOSTON_BOUNDS["center"], zoom_start=11)
    
    # Add traffic markers
    for _, row in traffic_data.iterrows():
        color = 'red' if row['congestion_index'] > 0.7 else 'orange' if row['congestion_index'] > 0.4 else 'green'
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"""
            <b>🚦 {row['location']}</b><br>
            📍 {row['neighborhood']}<br>
            🚗 {row['congestion_index']:.1%} congestion<br>
            ⚡ {row['average_speed_mph']:.0f} mph<br>
            {f"🎉 {row['special_event']}" if row['special_event'] else ""}
            """,
            icon=folium.Icon(color=color, icon='road')
        ).add_to(m)
    
    # Add AQI markers
    for _, row in aqi_data.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=8,
            popup=f"""
            <b>🌱 {row['station']}</b><br>
            AQI: {row['aqi']} ({row['category']})<br>
            PM2.5: {row['pm25']} μg/m³<br>
            Weather: {row['weather_condition']}
            """,
            color='black',
            fillColor=row['color'],
            fillOpacity=0.7
        ).add_to(m)
    
    return m

def create_traffic_map(traffic_data, show_events):
    """Create detailed traffic map"""
    m = folium.Map(location=config.BOSTON_BOUNDS["center"], zoom_start=12)
    
    for _, row in traffic_data.iterrows():
        color = 'red' if row['congestion_index'] > 0.7 else 'orange' if row['congestion_index'] > 0.4 else 'green'
        
        # Marker size based on traffic volume
        radius = min(20, max(8, row['traffic_volume'] / 200))
        
        popup_text = f"""
        <b>{row['location']}</b><br>
        📍 {row['neighborhood']}<br>
        🚗 {row['congestion_index']:.1%} congestion<br>
        ⚡ {row['average_speed_mph']:.0f} mph<br>
        🚙 {row['traffic_volume']} vehicles/hr<br>
        ⏱️ +{row['delay_minutes']:.0f} min delay
        """
        
        if show_events and row['special_event']:
            popup_text += f"<br>🎉 {row['special_event']}"
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=radius,
            popup=popup_text,
            color='black',
            fillColor=color,
            fillOpacity=0.7
        ).add_to(m)
    
    return m

def create_aqi_map(aqi_data):
    """Create air quality monitoring map"""
    m = folium.Map(location=config.BOSTON_BOUNDS["center"], zoom_start=11)
    
    for _, row in aqi_data.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=12,
            popup=f"""
            <b>🌱 {row['station']}</b><br>
            Type: {row['station_type'].replace('_', ' ').title()}<br>
            AQI: {row['aqi']} ({row['category']})<br>
            PM2.5: {row['pm25']} μg/m³<br>
            PM10: {row['pm10']} μg/m³<br>
            NO₂: {row['no2']} ppb<br>
            O₃: {row['o3']} ppb<br>
            Weather: {row['weather_condition']}
            """,
            color='black',
            fillColor=row['color'],
            fillOpacity=0.8
        ).add_to(m)
    
    return m

def display_traffic_trends():
    """Display traffic trend chart"""
    hours = list(range(24))
    congestion_pattern = []
    
    for hour in hours:
        base = 0.3
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            base += 0.4
        elif 10 <= hour <= 16:  # Business hours
            base += 0.2
        congestion_pattern.append(base + random.uniform(-0.1, 0.1))
    
    fig = px.line(x=hours, y=congestion_pattern, title="24-Hour Congestion Pattern")
    fig.add_hline(y=0.7, line_dash="dash", line_color="red", annotation_text="High Congestion")
    st.plotly_chart(fig, use_container_width=True)

def display_mbta_performance_chart(mbta_data):
    """Display MBTA performance chart"""
    performance_by_hour = []
    current_hour = datetime.now().hour
    
    for i in range(24):
        hour = (current_hour - 23 + i) % 24
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            on_time_pct = random.uniform(0.7, 0.85)
        else:
            on_time_pct = random.uniform(0.85, 0.95)
        performance_by_hour.append(on_time_pct)
    
    hours = [(current_hour - 23 + i) % 24 for i in range(24)]
    
    fig = px.line(x=hours, y=performance_by_hour, title="MBTA On-Time Performance (24H)")
    fig.add_hline(y=0.9, line_dash="dash", line_color="green", annotation_text="Target 90%")
    st.plotly_chart(fig, use_container_width=True)

# ================================
# 6. RUN APPLICATION

if __name__ == "__main__":
    main()
