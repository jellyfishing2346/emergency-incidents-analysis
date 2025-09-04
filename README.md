# Emergency Incidents Analysis

## 🚨 Overview
This project provides comprehensive analysis and visualization of emergency incidents data from the NERIS (National Emergency Response Information System) database. The analysis includes response times, incident patterns, geographic distribution, and operational efficiency metrics.

## 🎉 **Ready to Run**
**Great news!** The complete dataset (`NERIS_COMPLETE_INCIDENTS.csv`) is included in this repository. You can clone and run immediately - no separate data download required!

**Dataset:** 50,000 emergency incident records (21MB) covering 5 years of Maryland emergency responses across 5 cities.

## 📊 Features

### Data Analysis (`data_analyzer.py`)
- **Comprehensive Statistics**: Summary statistics for all incident types and response metrics
- **Response Time Analysis**: Distribution and patterns of emergency response times
- **Geographic Analysis**: Incident distribution across cities and location types
- **Temporal Patterns**: Analysis of incidents by time of day, day of week, and seasonal trends
- **Interactive Visualizations**: Charts and graphs showing key insights
- **Detailed Reporting**: Automated generation of analysis reports

### Interactive Dashboard (`dashboard.py`)
- **Real-time Filtering**: Filter data by date range, incident type, city, and response time
- **Key Metrics Dashboard**: Live updating statistics and KPIs
- **Geographic Mapping**: Interactive maps showing incident locations with color-coded markers
- **Trend Analysis**: Timeline visualizations and pattern recognition
- **Comparative Analysis**: City-by-city and type-by-type comparisons
- **Data Export**: Download filtered datasets for further analysis

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start
1. Clone this repository:
   ```bash
   git clone https://github.com/jellyfishing2346/emergency-incidents-analysis.git
   cd emergency-incidents-analysis
   ```
2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. Launch the dashboard:
   ```bash
   streamlit run dashboard.py
   ```

### Manual Installation
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Running the Data Analyzer
Generate comprehensive analysis and visualizations:
```bash
python data_analyzer.py
```

This will create:
- `incident_analysis.png` - Incident type and temporal analysis
- `geographic_analysis.png` - Geographic distribution charts
- `response_time_analysis.png` - Response time and operational metrics
- `interactive_dashboard.html` - Interactive Plotly dashboard
- `analysis_report.md` - Detailed written analysis report

### Running the Interactive Dashboard
Launch the Streamlit web dashboard:
```bash
streamlit run dashboard.py
```

The dashboard will open in your web browser and provide:
- Real-time data filtering and exploration
- Interactive maps and charts
- Key performance indicators
- Data export capabilities

## 📈 Data Structure

The NERIS dataset includes the following key fields:
- **Incident Information**: ID, type, description, category
- **Location Data**: Address, city, state, coordinates, place type
- **Timing Data**: Alarm, arrival, control, and clearance timestamps
- **Response Metrics**: Response time, control time, total time, units responded
- **Medical Data**: Patient care details, transport information, casualties
- **Fire Safety**: Suppression operations, alarm systems, sprinkler activation

## 📊 Key Insights

### Response Performance
- Average response time across all incidents
- 90th percentile response time benchmarks
- Response time variations by incident type and location

### Incident Patterns
- Most common incident types and their characteristics
- Peak hours and days for emergency responses
- Seasonal and temporal trends

### Geographic Distribution
- High-incident areas and response optimization opportunities
- City-by-city performance comparisons
- Location type analysis (residential, commercial, etc.)

### Operational Efficiency
- Unit allocation and resource utilization
- Control time analysis
- Total incident duration patterns

## 🔧 Customization

### Adding New Visualizations
Edit `data_analyzer.py` to add custom analysis functions:
```python
def create_custom_analysis(self):
    # Your custom analysis code here
    pass
```

### Modifying Dashboard Layout
Edit `dashboard.py` to customize the Streamlit interface:
```python
# Add new tabs, charts, or filters
tab5 = st.tabs(["Custom Analysis"])
```

### Adjusting Filters
Modify the filtering logic in the dashboard to add new filter options or change existing ones.

## 📋 File Structure
```
emergency-incidents-analysis/
├── NERIS_COMPLETE_INCIDENTS.csv    # ✅ Source data (21MB, 50K records)
├── data_analyzer.py                # Main analysis script
├── dashboard.py                     # Streamlit dashboard
├── database_summary.py              # Database summary generator
├── quick_preview.py                 # Quick data overview
├── requirements.txt                 # Python dependencies
├── setup.sh                         # Setup script
├── .gitignore                       # Git ignore file
├── README.md                        # This file
└── Generated files (included):
    ├── incident_analysis.png        # ✅ Analysis visualizations
    ├── quick_overview.png           # ✅ Data overview charts
    ├── database_summary.md          # ✅ Comprehensive analysis report
    └── database_summary.json       # ✅ Structured analysis data
```

**All files included - ready to run!** ✅

## 🎯 Use Cases

### Emergency Management
- **Response Optimization**: Identify areas for improving response times
- **Resource Allocation**: Optimize unit placement and staffing
- **Performance Monitoring**: Track KPIs and service level objectives

### Public Safety Planning
- **Risk Assessment**: Identify high-incident areas and patterns
- **Infrastructure Planning**: Inform decisions about station locations
- **Community Outreach**: Target safety programs based on incident data

### Research & Analysis
- **Trend Analysis**: Study long-term patterns and changes
- **Comparative Studies**: Compare performance across jurisdictions
- **Predictive Modeling**: Use historical data for forecasting

## 🔍 Data Quality Notes
- All timestamps are in Eastern Time (UTC-4)
- Response times calculated from alarm to arrival
- Geographic coordinates provided for mapping analysis
- Some records may have missing values for certain fields

## 🛠️ Troubleshooting

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Virtual Environment Issues
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Dashboard Won't Start
```bash
# Make sure you're in the project directory
cd emergency-incidents-analysis

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch dashboard
streamlit run dashboard.py
```

## 🤝 Contributing
To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support
For questions or issues:
- Review the code comments for implementation details
- Check the generated analysis reports for data insights
- Examine the dashboard filters for data exploration options

---

**Built with:** Python, Pandas, Plotly, Streamlit, Folium
**Data Source:** NERIS Emergency Response Information System
