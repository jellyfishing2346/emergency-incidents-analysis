#!/usr/bin/env python3
"""
Emergency Incidents Database Showcase
Interactive web dashboard for emergency incidents data
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import altair as alt

# Page configuration
st.set_page_config(
    page_title="Emergency Incidents Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #d63384;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the emergency incidents data."""
    # Try multiple possible file locations
    possible_paths = [
        'NERIS_COMPLETE_INCIDENTS.csv',  # Same directory
        '/Users/test/emergency-incidents-analysis/NERIS_COMPLETE_INCIDENTS.csv',  # Original path
        './NERIS_COMPLETE_INCIDENTS.csv',  # Current directory
        '../NERIS_COMPLETE_INCIDENTS.csv'  # Parent directory
    ]
    
    df = None
    for file_path in possible_paths:
        try:
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                st.success(f"✅ Data loaded successfully from: {file_path}")
                break
        except Exception as e:
            continue
    
    if df is None:
        st.error("""
        🚨 **Data File Not Found**
        
        The NERIS_COMPLETE_INCIDENTS.csv file is required to run this dashboard.
        
        **To fix this:**
        1. Download the NERIS emergency incidents dataset
        2. Save it as `NERIS_COMPLETE_INCIDENTS.csv` in the project directory
        3. Restart the dashboard
        
        **Alternative:** Use the static analysis files (`incident_analysis.png`, `database_summary.md`) 
        that are included in this repository.
        """)
        st.stop()
    
    # Convert datetime columns
    datetime_cols = ['alarm_datetime', 'arrival_datetime', 'controlled_datetime', 
                    'last_unit_cleared_datetime', 'incident_created_at']
    
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
    
    # Convert boolean columns
    bool_cols = ['people_present', 'fire_suppression_present']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].map({'t': True, 'f': False})
    
    # Extract features - with error handling for datetime operations
    df['incident_main_type'] = df['incident_type'].str.split('||').str[0]
    
    # Only extract datetime features if alarm_datetime is properly converted
    if 'alarm_datetime' in df.columns and not df['alarm_datetime'].empty:
        try:
            df['alarm_hour'] = df['alarm_datetime'].dt.hour
            df['day_of_week'] = df['alarm_datetime'].dt.day_name()
            df['date'] = df['alarm_datetime'].dt.date
        except AttributeError:
            # Fallback if datetime conversion fails
            df['alarm_hour'] = 12  # Default hour
            df['day_of_week'] = 'Unknown'
            df['date'] = pd.NaT
    else:
        # Fallback values if datetime column doesn't exist or is empty
        df['alarm_hour'] = 12  # Default hour
        df['day_of_week'] = 'Unknown' 
        df['date'] = pd.NaT
    
    return df

def create_metrics_cards(df, filtered_df):
    """Create metrics cards for key statistics."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Incidents",
            value=f"{len(filtered_df):,}",
            delta=f"{len(filtered_df) - len(df):,} vs All Data"
        )
    
    with col2:
        avg_response = filtered_df['response_time_minutes'].mean()
        st.metric(
            label="Avg Response Time",
            value=f"{avg_response:.1f} min",
            delta=f"{avg_response - df['response_time_minutes'].mean():.1f} min vs All"
        )
    
    with col3:
        total_casualties = filtered_df['total_casualties'].sum()
        st.metric(
            label="Total Casualties",
            value=f"{total_casualties:,}",
            delta=f"{total_casualties - df['total_casualties'].sum():,} vs All Data"
        )
    
    with col4:
        unique_cities = filtered_df['city'].nunique()
        st.metric(
            label="Cities Affected",
            value=f"{unique_cities}",
            delta=f"{unique_cities - df['city'].nunique():,} vs All Data"
        )

def create_incident_timeline(df):
    """Create timeline visualization of incidents."""
    daily_counts = df.groupby('date').size().reset_index(name='count')
    daily_counts['date'] = pd.to_datetime(daily_counts['date'])
    
    fig = px.line(
        daily_counts, 
        x='date', 
        y='count',
        title='Emergency Incidents Over Time',
        labels={'count': 'Number of Incidents', 'date': 'Date'}
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        title_x=0.5
    )
    
    return fig

def create_incident_type_chart(df):
    """Create incident type distribution chart."""
    incident_counts = df['incident_main_type'].value_counts().head(8)
    
    fig = px.bar(
        x=incident_counts.values,
        y=incident_counts.index,
        orientation='h',
        title='Most Common Incident Types',
        labels={'x': 'Number of Incidents', 'y': 'Incident Type'},
        color=incident_counts.values,
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        height=400,
        title_x=0.5,
        showlegend=False
    )
    
    return fig

def create_response_time_distribution(df):
    """Create response time distribution chart."""
    fig = px.histogram(
        df,
        x='response_time_minutes',
        nbins=30,
        title='Response Time Distribution',
        labels={'response_time_minutes': 'Response Time (minutes)', 'count': 'Frequency'}
    )
    
    # Add average line
    avg_response = df['response_time_minutes'].mean()
    fig.add_vline(
        x=avg_response,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Average: {avg_response:.1f} min"
    )
    
    fig.update_layout(
        height=400,
        title_x=0.5,
        showlegend=False
    )
    
    return fig

def create_hourly_pattern_chart(df):
    """Create hourly incident pattern chart."""
    hourly_counts = df.groupby('alarm_hour').size()
    
    fig = px.bar(
        x=hourly_counts.index,
        y=hourly_counts.values,
        title='Incidents by Hour of Day',
        labels={'x': 'Hour of Day', 'y': 'Number of Incidents'},
        color=hourly_counts.values,
        color_continuous_scale='plasma'
    )
    
    fig.update_layout(
        height=400,
        title_x=0.5,
        showlegend=False,
        xaxis=dict(tickmode='linear', tick0=0, dtick=2)
    )
    
    return fig

def create_geographic_map(df):
    """Create geographic map of incidents."""
    # Sample data for performance if too many points
    if len(df) > 1000:
        df_sample = df.sample(n=1000)
    else:
        df_sample = df
    
    # Create base map centered on Maryland
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=10,
        tiles='OpenStreetMap'
    )
    
    # Add incident markers with color coding by type
    incident_colors = {
        'MEDICAL': 'red',
        'FIRE': 'orange',
        'PUBSERV': 'blue',
        'OTHER': 'green'
    }
    
    for _, row in df_sample.iterrows():
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            color = incident_colors.get(row['incident_main_type'], 'gray')
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=5,
                popup=f"""
                <b>Incident:</b> {row['incident_description']}<br>
                <b>Date:</b> {row['alarm_datetime'].strftime('%Y-%m-%d %H:%M')}<br>
                <b>City:</b> {row['city']}<br>
                <b>Response Time:</b> {row['response_time_minutes']:.1f} min
                """,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6
            ).add_to(m)
    
    return m

def create_city_comparison(df):
    """Create city comparison chart."""
    city_stats = df.groupby('city').agg({
        'incident_number': 'count',
        'response_time_minutes': 'mean',
        'total_casualties': 'sum'
    }).round(2)
    
    city_stats = city_stats.sort_values('incident_number', ascending=False).head(10)
    city_stats.columns = ['Total Incidents', 'Avg Response Time', 'Total Casualties']
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=['Total Incidents', 'Avg Response Time (min)', 'Total Casualties'],
        specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Total incidents
    fig.add_trace(
        go.Bar(
            x=city_stats.index,
            y=city_stats['Total Incidents'],
            name='Total Incidents',
            marker_color='lightblue'
        ),
        row=1, col=1
    )
    
    # Average response time
    fig.add_trace(
        go.Bar(
            x=city_stats.index,
            y=city_stats['Avg Response Time'],
            name='Avg Response Time',
            marker_color='lightgreen'
        ),
        row=1, col=2
    )
    
    # Total casualties
    fig.add_trace(
        go.Bar(
            x=city_stats.index,
            y=city_stats['Total Casualties'],
            name='Total Casualties',
            marker_color='lightcoral'
        ),
        row=1, col=3
    )
    
    fig.update_layout(
        height=400,
        title_text="Top 10 Cities Comparison",
        title_x=0.5,
        showlegend=False
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig

def main():
    """Main Streamlit application."""
    # Header
    st.markdown('<h1 class="main-header">🚨 Emergency Incidents Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    with st.spinner('Loading emergency incidents data...'):
        df = load_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Date range filter
    min_date = df['alarm_datetime'].dt.date.min()
    max_date = df['alarm_datetime'].dt.date.max()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Incident type filter
    incident_types = ['All'] + list(df['incident_main_type'].unique())
    selected_incident_type = st.sidebar.selectbox("Incident Type", incident_types)
    
    # City filter
    cities = ['All'] + list(df['city'].unique())
    selected_city = st.sidebar.selectbox("City", cities)
    
    # Response time filter
    max_response_time = st.sidebar.slider(
        "Max Response Time (minutes)",
        min_value=0,
        max_value=int(df['response_time_minutes'].max()),
        value=int(df['response_time_minutes'].max())
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['alarm_datetime'].dt.date >= date_range[0]) &
            (filtered_df['alarm_datetime'].dt.date <= date_range[1])
        ]
    
    if selected_incident_type != 'All':
        filtered_df = filtered_df[filtered_df['incident_main_type'] == selected_incident_type]
    
    if selected_city != 'All':
        filtered_df = filtered_df[filtered_df['city'] == selected_city]
    
    filtered_df = filtered_df[filtered_df['response_time_minutes'] <= max_response_time]
    
    # Display metrics
    st.subheader("📊 Key Metrics")
    create_metrics_cards(df, filtered_df)
    
    st.markdown("---")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🗺️ Geographic Analysis", "⏱️ Response Analysis", "📋 Data Table"])
    
    with tab1:
        st.subheader("📈 Incident Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            timeline_fig = create_incident_timeline(filtered_df)
            st.plotly_chart(timeline_fig, use_container_width=True)
            
            hourly_fig = create_hourly_pattern_chart(filtered_df)
            st.plotly_chart(hourly_fig, use_container_width=True)
        
        with col2:
            incident_type_fig = create_incident_type_chart(filtered_df)
            st.plotly_chart(incident_type_fig, use_container_width=True)
            
            response_dist_fig = create_response_time_distribution(filtered_df)
            st.plotly_chart(response_dist_fig, use_container_width=True)
    
    with tab2:
        st.subheader("🗺️ Geographic Distribution")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Incident Locations Map")
            incident_map = create_geographic_map(filtered_df)
            st_folium(incident_map, width=700, height=500)
        
        with col2:
            st.subheader("Legend")
            st.markdown("""
            **Map Legend:**
            - 🔴 **Red**: Medical Incidents
            - 🟠 **Orange**: Fire Incidents  
            - 🔵 **Blue**: Public Service
            - 🟢 **Green**: Other Incidents
            """)
            
            # City breakdown
            st.subheader("Cities Overview")
            city_counts = filtered_df['city'].value_counts().head(5)
            for city, count in city_counts.items():
                st.write(f"**{city}**: {count} incidents")
        
        # City comparison chart
        city_comparison_fig = create_city_comparison(filtered_df)
        st.plotly_chart(city_comparison_fig, use_container_width=True)
    
    with tab3:
        st.subheader("⏱️ Response Time Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Response time by incident type
            response_by_type = filtered_df.groupby('incident_main_type')['response_time_minutes'].mean().sort_values(ascending=False)
            
            fig = px.bar(
                x=response_by_type.values,
                y=response_by_type.index,
                orientation='h',
                title='Average Response Time by Incident Type',
                labels={'x': 'Average Response Time (minutes)', 'y': 'Incident Type'},
                color=response_by_type.values,
                color_continuous_scale='reds'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Response time by day of week
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            response_by_day = filtered_df.groupby('day_of_week')['response_time_minutes'].mean().reindex(day_order)
            
            fig = px.bar(
                x=response_by_day.index,
                y=response_by_day.values,
                title='Average Response Time by Day of Week',
                labels={'x': 'Day of Week', 'y': 'Average Response Time (minutes)'},
                color=response_by_day.values,
                color_continuous_scale='blues'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Response time statistics
        st.subheader("📊 Response Time Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mean", f"{filtered_df['response_time_minutes'].mean():.1f} min")
        with col2:
            st.metric("Median", f"{filtered_df['response_time_minutes'].median():.1f} min")
        with col3:
            st.metric("90th Percentile", f"{filtered_df['response_time_minutes'].quantile(0.9):.1f} min")
        with col4:
            st.metric("Max", f"{filtered_df['response_time_minutes'].max():.1f} min")
    
    with tab4:
        st.subheader("📋 Filtered Data Table")
        
        # Display options
        col1, col2 = st.columns(2)
        with col1:
            show_columns = st.multiselect(
                "Select columns to display:",
                options=filtered_df.columns.tolist(),
                default=['incident_number', 'alarm_datetime', 'incident_description', 'city', 'response_time_minutes']
            )
        
        with col2:
            rows_to_show = st.selectbox("Rows to display:", [10, 25, 50, 100], index=1)
        
        if show_columns:
            display_df = filtered_df[show_columns].head(rows_to_show)
            st.dataframe(display_df, use_container_width=True)
            
            # Download button
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="Download filtered data as CSV",
                data=csv,
                file_name=f"emergency_incidents_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            Emergency Incidents Analysis Dashboard | Data from NERIS Database<br>
            📊 Built with Streamlit | 🚨 Emergency Response Analytics
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
