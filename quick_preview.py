#!/usr/bin/env python3
"""
Quick Data Preview and Summary
Generate a quick overview of the emergency incidents data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

def quick_data_preview():
    """Generate a quick preview of the data."""
    
    print("🚨 EMERGENCY INCIDENTS DATA PREVIEW")
    print("=" * 50)
    
    # Load data
    df = pd.read_csv('/Users/test/emergency-incidents-analysis/NERIS_COMPLETE_INCIDENTS.csv')
    
    print(f"📊 Dataset Info:")
    print(f"   Total Records: {len(df):,}")
    print(f"   Total Columns: {len(df.columns)}")
    print(f"   File Size: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    
    # Basic statistics
    print(f"\n📈 Quick Statistics:")
    print(f"   Date Range: {df['alarm_datetime'].min()} to {df['alarm_datetime'].max()}")
    print(f"   Cities: {df['city'].nunique()} unique cities")
    print(f"   Incident Types: {df['incident_type'].nunique()} unique types")
    
    # Top incident types
    print(f"\n🔥 Top 5 Incident Types:")
    # Split incident types and get main category
    incident_main_types = df['incident_type'].str.split('||').str[0]
    incident_main_types = incident_main_types[incident_main_types.notna() & (incident_main_types != '')]
    
    if len(incident_main_types) > 0:
        incident_counts = incident_main_types.value_counts()
        for i, (incident_type, count) in enumerate(incident_counts.head(5).items(), 1):
            percentage = (count / len(incident_main_types)) * 100
            print(f"   {i}. {incident_type}: {count:,} ({percentage:.1f}%)")
    else:
        # Fallback to full incident description
        incident_descriptions = df['incident_description'].value_counts()
        for i, (incident_desc, count) in enumerate(incident_descriptions.head(5).items(), 1):
            percentage = (count / len(df)) * 100
            print(f"   {i}. {incident_desc}: {count:,} ({percentage:.1f}%)")
    
    # Top cities
    print(f"\n🏙️ Top 5 Cities:")
    city_counts = df['city'].value_counts()
    for i, (city, count) in enumerate(city_counts.head(5).items(), 1):
        percentage = (count / len(df)) * 100
        print(f"   {i}. {city}: {count:,} ({percentage:.1f}%)")
    
    # Response time stats
    response_times = pd.to_numeric(df['response_time_minutes'], errors='coerce')
    print(f"\n⏱️ Response Time Analysis:")
    print(f"   Average: {response_times.mean():.1f} minutes")
    print(f"   Median: {response_times.median():.1f} minutes")
    print(f"   Fastest: {response_times.min():.1f} minutes")
    print(f"   Slowest: {response_times.max():.1f} minutes")
    
    # Casualties
    casualties = pd.to_numeric(df['total_casualties'], errors='coerce')
    print(f"\n🚑 Casualties Summary:")
    print(f"   Total Casualties: {casualties.sum():,}")
    print(f"   Incidents with Casualties: {(casualties > 0).sum():,}")
    print(f"   Max Casualties per Incident: {casualties.max()}")
    
    # Data quality
    print(f"\n🔍 Data Quality:")
    missing_percentages = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
    print(f"   Columns with Missing Data: {(missing_percentages > 0).sum()}")
    
    top_missing = missing_percentages[missing_percentages > 0].head(5)
    for col, pct in top_missing.items():
        print(f"   - {col}: {pct:.1f}% missing")
    
    print(f"\n✅ Data Preview Complete!")
    print(f"   Ready for analysis with data_analyzer.py")
    print(f"   Ready for dashboard with dashboard.py")
    
    return df

def create_quick_visualization(df):
    """Create a quick overview visualization."""
    
    # Set up the plot
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('Emergency Incidents Quick Overview', fontsize=16, fontweight='bold')
    
    # Convert datetime properly
    df_viz = df.copy()
    df_viz['alarm_datetime'] = pd.to_datetime(df_viz['alarm_datetime'], errors='coerce', utc=True)
    
    # 1. Incident types - fix empty values
    incident_types = df_viz['incident_type'].str.split('||').str[0]
    incident_types = incident_types[incident_types.notna() & (incident_types != '')]
    
    if len(incident_types) > 0:
        incident_counts = incident_types.value_counts().head(6)
        if len(incident_counts) > 0:
            axes[0, 0].pie(incident_counts.values, labels=incident_counts.index, autopct='%1.1f%%')
            axes[0, 0].set_title('Top Incident Types')
        else:
            axes[0, 0].text(0.5, 0.5, 'No incident type data', ha='center', va='center', transform=axes[0, 0].transAxes)
            axes[0, 0].set_title('Incident Types - No Data')
    else:
        axes[0, 0].text(0.5, 0.5, 'No incident type data', ha='center', va='center', transform=axes[0, 0].transAxes)
        axes[0, 0].set_title('Incident Types - No Data')
    
    # 2. Response times
    response_times = pd.to_numeric(df_viz['response_time_minutes'], errors='coerce')
    valid_response_times = response_times.dropna()
    if len(valid_response_times) > 0:
        axes[0, 1].hist(valid_response_times, bins=30, edgecolor='black', alpha=0.7)
        axes[0, 1].set_title('Response Time Distribution')
        axes[0, 1].set_xlabel('Minutes')
    else:
        axes[0, 1].text(0.5, 0.5, 'No response time data', ha='center', va='center', transform=axes[0, 1].transAxes)
        axes[0, 1].set_title('Response Times - No Data')
    
    # 3. Top cities
    city_counts = df_viz['city'].value_counts().head(8)
    if len(city_counts) > 0:
        axes[1, 0].barh(range(len(city_counts)), city_counts.values)
        axes[1, 0].set_yticks(range(len(city_counts)))
        axes[1, 0].set_yticklabels(city_counts.index)
        axes[1, 0].set_title('Top Cities by Incidents')
    else:
        axes[1, 0].text(0.5, 0.5, 'No city data', ha='center', va='center', transform=axes[1, 0].transAxes)
        axes[1, 0].set_title('Cities - No Data')
    
    # 4. Incidents over time (daily)
    valid_dates = df_viz['alarm_datetime'].dropna()
    if len(valid_dates) > 0:
        df_viz_clean = df_viz[df_viz['alarm_datetime'].notna()].copy()
        df_viz_clean['date'] = df_viz_clean['alarm_datetime'].dt.date
        daily_counts = df_viz_clean.groupby('date').size()
        
        if len(daily_counts) > 0:
            axes[1, 1].plot(daily_counts.index, daily_counts.values, marker='o', markersize=2)
            axes[1, 1].set_title('Incidents Over Time')
            axes[1, 1].tick_params(axis='x', rotation=45)
        else:
            axes[1, 1].text(0.5, 0.5, 'No timeline data', ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Timeline - No Data')
    else:
        axes[1, 1].text(0.5, 0.5, 'No datetime data', ha='center', va='center', transform=axes[1, 1].transAxes)
        axes[1, 1].set_title('Timeline - No Data')
    
    plt.tight_layout()
    plt.savefig('/Users/test/emergency-incidents-analysis/quick_overview.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("📊 Quick visualization saved as 'quick_overview.png'")

if __name__ == "__main__":
    df = quick_data_preview()
    
    # Ask if user wants to create visualization
    create_viz = input("\n📊 Create quick visualization? (y/n): ").lower().strip()
    if create_viz in ['y', 'yes']:
        create_quick_visualization(df)
    
    print("\n🚀 Next steps:")
    print("   1. Run 'python data_analyzer.py' for complete analysis")
    print("   2. Run 'streamlit run dashboard.py' for interactive dashboard")
    print("   3. Check README.md for detailed instructions")
