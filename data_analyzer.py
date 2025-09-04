#!/usr/bin/env python3
"""
Emergency Incidents Data Analyzer
Comprehensive analysis and visualization of NERIS emergency incidents data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class EmergencyIncidentsAnalyzer:
    def __init__(self, csv_file_path):
        """Initialize the analyzer with the CSV data."""
        self.csv_file = csv_file_path
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Load and preprocess the emergency incidents data."""
        print("Loading emergency incidents data...")
        self.df = pd.read_csv(self.csv_file)
        
        # Convert datetime columns with proper UTC handling
        datetime_cols = ['alarm_datetime', 'arrival_datetime', 'controlled_datetime', 
                        'last_unit_cleared_datetime', 'incident_created_at']
        
        for col in datetime_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce', utc=True)
        
        # Convert boolean columns
        bool_cols = ['people_present', 'fire_suppression_present']
        for col in bool_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].map({'t': True, 'f': False})
        
        # Extract incident main type
        incident_types = self.df['incident_type'].str.split('||').str[0]
        self.df['incident_main_type'] = incident_types.fillna('Unknown')
        
        # Extract hour from alarm datetime (only if valid)
        valid_alarm_datetime = self.df['alarm_datetime'].dropna()
        if len(valid_alarm_datetime) > 0:
            self.df['alarm_hour'] = self.df['alarm_datetime'].dt.hour
            self.df['day_of_week'] = self.df['alarm_datetime'].dt.day_name()
        else:
            self.df['alarm_hour'] = None
            self.df['day_of_week'] = None
        
        print(f"Data loaded successfully! {len(self.df)} incidents found.")
        if len(valid_alarm_datetime) > 0:
            print(f"Date range: {self.df['alarm_datetime'].min()} to {self.df['alarm_datetime'].max()}")
        else:
            print("No valid datetime data found.")
        
    def get_summary_statistics(self):
        """Generate comprehensive summary statistics."""
        print("\n" + "="*60)
        print("EMERGENCY INCIDENTS DATA SUMMARY")
        print("="*60)
        
        # Basic statistics
        print(f"Total Incidents: {len(self.df):,}")
        
        # Check if we have valid datetime data
        valid_datetime = self.df['alarm_datetime'].dropna()
        if len(valid_datetime) > 0:
            print(f"Date Range: {self.df['alarm_datetime'].min().strftime('%Y-%m-%d')} to {self.df['alarm_datetime'].max().strftime('%Y-%m-%d')}")
        else:
            print("Date Range: No valid datetime data")
            
        print(f"Unique Cities: {self.df['city'].nunique()}")
        print(f"Unique Incident Types: {self.df['incident_main_type'].nunique()}")
        
        # Response time statistics
        print(f"\nResponse Time Statistics:")
        response_times = pd.to_numeric(self.df['response_time_minutes'], errors='coerce')
        valid_response_times = response_times.dropna()
        
        if len(valid_response_times) > 0:
            print(f"Average Response Time: {valid_response_times.mean():.2f} minutes")
            print(f"Median Response Time: {valid_response_times.median():.2f} minutes")
            print(f"Max Response Time: {valid_response_times.max():.2f} minutes")
        else:
            print("No valid response time data")
        
        # Incident type breakdown
        print(f"\nIncident Types Breakdown:")
        incident_counts = self.df['incident_main_type'].value_counts()
        for incident_type, count in incident_counts.head(10).items():
            percentage = (count / len(self.df)) * 100
            print(f"  {incident_type}: {count:,} ({percentage:.1f}%)")
        
        # City breakdown
        print(f"\nTop 10 Cities by Incident Count:")
        city_counts = self.df['city'].value_counts()
        for city, count in city_counts.head(10).items():
            percentage = (count / len(self.df)) * 100
            print(f"  {city}: {count:,} ({percentage:.1f}%)")
        
        # Casualties and transport
        print(f"\nCasualties and Transport:")
        casualties = pd.to_numeric(self.df['total_casualties'], errors='coerce')
        valid_casualties = casualties.dropna()
        
        if len(valid_casualties) > 0:
            print(f"Total Casualties: {valid_casualties.sum():,}")
            print(f"Incidents with Casualties: {(valid_casualties > 0).sum():,}")
        else:
            print("No valid casualty data")
        
        transport_counts = self.df['transport_disposition'].value_counts()
        print(f"\nTransport Disposition:")
        for disposition, count in transport_counts.items():
            if pd.notna(disposition):
                percentage = (count / len(self.df[self.df['transport_disposition'].notna()])) * 100
                print(f"  {disposition}: {count:,} ({percentage:.1f}%)")
        
        return {
            'total_incidents': len(self.df),
            'date_range': (self.df['alarm_datetime'].min(), self.df['alarm_datetime'].max()) if len(valid_datetime) > 0 else (None, None),
            'avg_response_time': valid_response_times.mean() if len(valid_response_times) > 0 else None,
            'incident_types': incident_counts,
            'city_counts': city_counts,
            'total_casualties': valid_casualties.sum() if len(valid_casualties) > 0 else 0
        }
    
    def create_incident_type_analysis(self):
        """Analyze incident types and their characteristics."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Emergency Incident Types Analysis', fontsize=16, fontweight='bold')
        
        # 1. Incident type distribution
        incident_counts = self.df['incident_main_type'].value_counts().head(8)
        if len(incident_counts) > 0:
            axes[0, 0].pie(incident_counts.values, labels=incident_counts.index, autopct='%1.1f%%')
            axes[0, 0].set_title('Incident Type Distribution')
        else:
            axes[0, 0].text(0.5, 0.5, 'No incident type data', ha='center', va='center', transform=axes[0, 0].transAxes)
            axes[0, 0].set_title('Incident Type Distribution - No Data')
        
        # 2. Response time by incident type
        response_data = self.df.dropna(subset=['incident_main_type', 'response_time_minutes'])
        if len(response_data) > 0:
            response_by_type = response_data.groupby('incident_main_type')['response_time_minutes'].mean().sort_values(ascending=False).head(8)
            axes[0, 1].bar(range(len(response_by_type)), response_by_type.values)
            axes[0, 1].set_xticks(range(len(response_by_type)))
            axes[0, 1].set_xticklabels(response_by_type.index, rotation=45, ha='right')
            axes[0, 1].set_title('Average Response Time by Incident Type')
            axes[0, 1].set_ylabel('Minutes')
        else:
            axes[0, 1].text(0.5, 0.5, 'No response time data', ha='center', va='center', transform=axes[0, 1].transAxes)
            axes[0, 1].set_title('Response Time by Type - No Data')
        
        # 3. Incidents by hour of day
        if self.df['alarm_hour'].notna().any():
            hourly_incidents = self.df.groupby('alarm_hour').size()
            axes[1, 0].plot(hourly_incidents.index, hourly_incidents.values, marker='o')
            axes[1, 0].set_title('Incidents by Hour of Day')
            axes[1, 0].set_xlabel('Hour')
            axes[1, 0].set_ylabel('Number of Incidents')
            axes[1, 0].grid(True, alpha=0.3)
        else:
            axes[1, 0].text(0.5, 0.5, 'No hourly data', ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Incidents by Hour - No Data')
        
        # 4. Incidents by day of week
        if self.df['day_of_week'].notna().any():
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_incidents = self.df['day_of_week'].value_counts().reindex(day_order)
            daily_incidents = daily_incidents.dropna()
            if len(daily_incidents) > 0:
                axes[1, 1].bar(daily_incidents.index, daily_incidents.values)
                axes[1, 1].set_title('Incidents by Day of Week')
                axes[1, 1].set_xticklabels(daily_incidents.index, rotation=45, ha='right')
                axes[1, 1].set_ylabel('Number of Incidents')
            else:
                axes[1, 1].text(0.5, 0.5, 'No daily data', ha='center', va='center', transform=axes[1, 1].transAxes)
                axes[1, 1].set_title('Incidents by Day - No Data')
        else:
            axes[1, 1].text(0.5, 0.5, 'No daily data', ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Incidents by Day - No Data')
        
        plt.tight_layout()
        plt.savefig('/Users/test/emergency-incidents-analysis/incident_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_geographic_analysis(self):
        """Analyze geographic distribution of incidents."""
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Geographic Distribution of Emergency Incidents', fontsize=16, fontweight='bold')
        
        # 1. Incidents by city
        city_counts = self.df['city'].value_counts().head(10)
        axes[0].barh(range(len(city_counts)), city_counts.values)
        axes[0].set_yticks(range(len(city_counts)))
        axes[0].set_yticklabels(city_counts.index)
        axes[0].set_title('Top 10 Cities by Incident Count')
        axes[0].set_xlabel('Number of Incidents')
        
        # 2. Incidents by place type
        place_counts = self.df['place_type'].value_counts().head(8)
        axes[1].pie(place_counts.values, labels=place_counts.index, autopct='%1.1f%%')
        axes[1].set_title('Incidents by Place Type')
        
        plt.tight_layout()
        plt.savefig('/Users/test/emergency-incidents-analysis/geographic_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_response_time_analysis(self):
        """Analyze response times and operational efficiency."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Response Time and Operational Analysis', fontsize=16, fontweight='bold')
        
        # 1. Response time distribution
        axes[0, 0].hist(self.df['response_time_minutes'].dropna(), bins=30, edgecolor='black', alpha=0.7)
        axes[0, 0].set_title('Response Time Distribution')
        axes[0, 0].set_xlabel('Response Time (minutes)')
        axes[0, 0].set_ylabel('Frequency')
        
        # 2. Response time vs control time
        valid_data = self.df.dropna(subset=['response_time_minutes', 'control_time_minutes'])
        axes[0, 1].scatter(valid_data['response_time_minutes'], valid_data['control_time_minutes'], 
                          alpha=0.6, s=20)
        axes[0, 1].set_title('Response Time vs Control Time')
        axes[0, 1].set_xlabel('Response Time (minutes)')
        axes[0, 1].set_ylabel('Control Time (minutes)')
        
        # 3. Units responded distribution
        units_dist = self.df['units_responded'].value_counts().sort_index()
        axes[1, 0].bar(units_dist.index, units_dist.values)
        axes[1, 0].set_title('Distribution of Units Responded')
        axes[1, 0].set_xlabel('Number of Units')
        axes[1, 0].set_ylabel('Number of Incidents')
        
        # 4. Total time by incident category
        time_by_category = self.df.groupby('incident_category')['total_time_minutes'].mean().sort_values(ascending=False)
        axes[1, 1].barh(range(len(time_by_category)), time_by_category.values)
        axes[1, 1].set_yticks(range(len(time_by_category)))
        axes[1, 1].set_yticklabels(time_by_category.index)
        axes[1, 1].set_title('Average Total Time by Incident Category')
        axes[1, 1].set_xlabel('Total Time (minutes)')
        
        plt.tight_layout()
        plt.savefig('/Users/test/emergency-incidents-analysis/response_time_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_interactive_dashboard(self):
        """Create an interactive Plotly dashboard."""
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Incidents Over Time', 'Response Time by City', 
                          'Incident Types Distribution', 'Geographic Distribution'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Time series of incidents
        valid_datetime = self.df['alarm_datetime'].dropna()
        if len(valid_datetime) > 0:
            daily_incidents = self.df[self.df['alarm_datetime'].notna()].groupby(self.df['alarm_datetime'].dt.date).size()
            fig.add_trace(
                go.Scatter(x=daily_incidents.index, y=daily_incidents.values, 
                          mode='lines+markers', name='Daily Incidents'),
                row=1, col=1
            )
        else:
            # Add placeholder
            fig.add_trace(
                go.Scatter(x=[1], y=[1], mode='markers', name='No Date Data'),
                row=1, col=1
            )
        
        # 2. Response time by city (top 10)
        top_cities = self.df['city'].value_counts().head(10).index
        response_data = self.df[self.df['city'].isin(top_cities)].dropna(subset=['response_time_minutes'])
        
        if len(response_data) > 0:
            city_response_times = response_data.groupby('city')['response_time_minutes'].mean()
            fig.add_trace(
                go.Bar(x=city_response_times.index, y=city_response_times.values, 
                       name='Avg Response Time'),
                row=1, col=2
            )
        else:
            # Add placeholder
            fig.add_trace(
                go.Bar(x=['No Data'], y=[0], name='No Response Data'),
                row=1, col=2
            )
        
        # 3. Incident types pie chart
        incident_counts = self.df['incident_main_type'].value_counts().head(6)
        if len(incident_counts) > 0:
            fig.add_trace(
                go.Pie(labels=incident_counts.index, values=incident_counts.values, 
                       name="Incident Types"),
                row=2, col=1
            )
        else:
            # Add placeholder
            fig.add_trace(
                go.Pie(labels=['No Data'], values=[1], name="No Incident Data"),
                row=2, col=1
            )
        
        # 4. Geographic scatter
        geo_data = self.df.dropna(subset=['latitude', 'longitude'])
        if len(geo_data) > 0:
            # Sample for performance
            if len(geo_data) > 1000:
                geo_data = geo_data.sample(n=1000)
            
            fig.add_trace(
                go.Scatter(x=geo_data['longitude'], y=geo_data['latitude'], 
                          mode='markers', name='Incident Locations',
                          marker=dict(size=4, opacity=0.6)),
                row=2, col=2
            )
        else:
            # Add placeholder
            fig.add_trace(
                go.Scatter(x=[0], y=[0], mode='markers', name='No Location Data'),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title_text="Emergency Incidents Interactive Dashboard",
            title_x=0.5,
            height=800,
            showlegend=False
        )
        
        # Save interactive dashboard
        fig.write_html('/Users/test/emergency-incidents-analysis/interactive_dashboard.html')
        print("Interactive dashboard saved as 'interactive_dashboard.html'")
        
        return fig
    
    def create_detailed_report(self):
        """Generate a detailed analysis report."""
        # Get basic statistics
        valid_datetime = self.df['alarm_datetime'].dropna()
        response_times = pd.to_numeric(self.df['response_time_minutes'], errors='coerce').dropna()
        casualties = pd.to_numeric(self.df['total_casualties'], errors='coerce').dropna()
        
        # Handle datetime range
        if len(valid_datetime) > 0:
            date_range_str = f"{self.df['alarm_datetime'].min().strftime('%Y-%m-%d')} to {self.df['alarm_datetime'].max().strftime('%Y-%m-%d')}"
        else:
            date_range_str = "No valid date data available"
        
        # Handle peak hour/day calculations
        if self.df['alarm_hour'].notna().any():
            peak_hour = self.df.groupby('alarm_hour').size().idxmax()
            peak_hour_count = self.df.groupby('alarm_hour').size().max()
            peak_hour_str = f"{peak_hour}:00 ({peak_hour_count} incidents)"
        else:
            peak_hour_str = "No hourly data available"
        
        if self.df['day_of_week'].notna().any():
            busiest_day = self.df['day_of_week'].value_counts().index[0]
            busiest_day_count = self.df['day_of_week'].value_counts().iloc[0]
            busiest_day_str = f"{busiest_day} ({busiest_day_count} incidents)"
        else:
            busiest_day_str = "No daily data available"
        
        report_content = f"""
# Emergency Incidents Analysis Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
This report analyzes {len(self.df):,} emergency incidents from the NERIS database spanning from {date_range_str}.

## Key Findings

### Response Performance
- **Average Response Time**: {response_times.mean():.2f} minutes
- **Median Response Time**: {response_times.median():.2f} minutes
- **90th Percentile Response Time**: {response_times.quantile(0.9):.2f} minutes

### Incident Patterns
- **Most Common Incident Type**: {self.df['incident_main_type'].value_counts().index[0]} ({self.df['incident_main_type'].value_counts().iloc[0]:,} incidents)
- **Peak Hour**: {peak_hour_str}
- **Busiest Day**: {busiest_day_str}

### Geographic Distribution
- **Most Active City**: {self.df['city'].value_counts().index[0]} ({self.df['city'].value_counts().iloc[0]:,} incidents)
- **Most Common Location Type**: {self.df['place_type'].value_counts().index[0]} ({self.df['place_type'].value_counts().iloc[0]:,} incidents)

### Medical Outcomes
- **Total Casualties**: {casualties.sum():,}
- **Incidents with Transport**: {(self.df['transport_disposition'] == 'TRANSPORT_BY_EMS_UNIT').sum():,}
- **Patient Refusal Rate**: {((self.df['transport_disposition'] == 'PATIENT_REFUSED_TRANSPORT').sum() / self.df['transport_disposition'].notna().sum() * 100):.1f}%

## Detailed Analysis

### Incident Type Breakdown
"""
        
        # Add incident type breakdown
        incident_counts = self.df['incident_main_type'].value_counts()
        for incident_type, count in incident_counts.items():
            percentage = (count / len(self.df)) * 100
            report_content += f"- **{incident_type}**: {count:,} incidents ({percentage:.1f}%)\n"
        
        report_content += f"""

### Geographic Analysis
The incidents are distributed across {self.df['city'].nunique()} cities in Maryland. The top 5 cities are:

"""
        
        # Add city breakdown
        city_counts = self.df['city'].value_counts().head(5)
        for city, count in city_counts.items():
            percentage = (count / len(self.df)) * 100
            city_response_data = self.df[self.df['city'] == city]['response_time_minutes']
            city_response_data = pd.to_numeric(city_response_data, errors='coerce').dropna()
            
            if len(city_response_data) > 0:
                avg_response = city_response_data.mean()
                report_content += f"- **{city}**: {count:,} incidents ({percentage:.1f}%) - Avg Response: {avg_response:.1f} min\n"
            else:
                report_content += f"- **{city}**: {count:,} incidents ({percentage:.1f}%) - No response data\n"
        
        report_content += """

### Recommendations
1. **Peak Hour Staffing**: Consider increasing staffing during peak hours to reduce response times
2. **Geographic Optimization**: Review unit placement in high-incident areas
3. **Training Focus**: Prioritize training for the most common incident types
4. **Equipment Allocation**: Ensure adequate equipment availability during peak periods

## Data Quality Notes
- All timestamps are in Eastern Time (UTC-4)
- Response times calculated from alarm to arrival
- Geographic coordinates provided for mapping analysis
"""
        
        # Save report
        with open('/Users/test/emergency-incidents-analysis/analysis_report.md', 'w') as f:
            f.write(report_content)
        
        print("Detailed analysis report saved as 'analysis_report.md'")
    
    def run_complete_analysis(self):
        """Run the complete analysis suite."""
        print("Starting complete emergency incidents analysis...")
        
        # Generate summary statistics
        summary = self.get_summary_statistics()
        
        # Create visualizations
        print("\nGenerating visualizations...")
        self.create_incident_type_analysis()
        self.create_geographic_analysis()
        self.create_response_time_analysis()
        
        # Create interactive dashboard
        print("\nCreating interactive dashboard...")
        self.create_interactive_dashboard()
        
        # Generate detailed report
        print("\nGenerating detailed report...")
        self.create_detailed_report()
        
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE!")
        print("="*60)
        print("Generated files:")
        print("- incident_analysis.png")
        print("- geographic_analysis.png")
        print("- response_time_analysis.png")
        print("- interactive_dashboard.html")
        print("- analysis_report.md")
        print("\nAll analysis files have been saved to the current directory.")

if __name__ == "__main__":
    # Initialize analyzer
    analyzer = EmergencyIncidentsAnalyzer('/Users/test/emergency-incidents-analysis/NERIS_COMPLETE_INCIDENTS.csv')
    
    # Run complete analysis
    analyzer.run_complete_analysis()
