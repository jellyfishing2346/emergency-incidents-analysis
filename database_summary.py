#!/usr/bin/env python3
"""
Database Summary Generator
Creates a formatted summary of the emergency incidents database
"""

import pandas as pd
import json
from datetime import datetime

def generate_database_summary():
    """Generate a comprehensive database summary."""
    
    # Load the data
    df = pd.read_csv('/Users/test/emergency-incidents-analysis/NERIS_COMPLETE_INCIDENTS.csv')
    
    # Convert datetime
    df['alarm_datetime'] = pd.to_datetime(df['alarm_datetime'], errors='coerce', utc=True)
    
    # Basic statistics
    summary = {
        "database_info": {
            "total_records": len(df),
            "total_columns": len(df.columns),
            "file_size_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 1),
            "date_range": {
                "start": df['alarm_datetime'].min().strftime('%Y-%m-%d') if df['alarm_datetime'].notna().any() else "N/A",
                "end": df['alarm_datetime'].max().strftime('%Y-%m-%d') if df['alarm_datetime'].notna().any() else "N/A",
                "span_years": round((df['alarm_datetime'].max() - df['alarm_datetime'].min()).days / 365.25, 1) if df['alarm_datetime'].notna().any() else 0
            }
        },
        "geographic_coverage": {
            "unique_cities": df['city'].nunique(),
            "unique_zip_codes": df['zip_code'].nunique(),
            "place_types": df['place_type'].nunique(),
            "top_cities": df['city'].value_counts().head(5).to_dict()
        },
        "incident_statistics": {
            "unique_incident_types": df['incident_type'].nunique(),
            "unique_incident_categories": df['incident_category'].nunique(),
            "total_casualties": int(pd.to_numeric(df['total_casualties'], errors='coerce').sum()),
            "incidents_with_casualties": int((pd.to_numeric(df['total_casualties'], errors='coerce') > 0).sum()),
            "top_incident_descriptions": df['incident_description'].value_counts().head(5).to_dict()
        },
        "response_metrics": {
            "average_response_time": round(pd.to_numeric(df['response_time_minutes'], errors='coerce').mean(), 2),
            "median_response_time": round(pd.to_numeric(df['response_time_minutes'], errors='coerce').median(), 2),
            "fastest_response": round(pd.to_numeric(df['response_time_minutes'], errors='coerce').min(), 2),
            "slowest_response": round(pd.to_numeric(df['response_time_minutes'], errors='coerce').max(), 2),
            "average_units_responded": round(pd.to_numeric(df['units_responded'], errors='coerce').mean(), 1)
        },
        "medical_outcomes": {
            "transport_disposition": df['transport_disposition'].value_counts().to_dict(),
            "patient_care_evaluations": df['patient_care_evaluation'].value_counts().to_dict()
        },
        "data_quality": {
            "completeness": {},
            "missing_data_analysis": {}
        }
    }
    
    # Data quality analysis
    for col in df.columns:
        missing_pct = round((df[col].isnull().sum() / len(df)) * 100, 1)
        summary["data_quality"]["completeness"][col] = 100 - missing_pct
        if missing_pct > 0:
            summary["data_quality"]["missing_data_analysis"][col] = missing_pct
    
    # Generate formatted report
    report = f"""
# 🚨 EMERGENCY INCIDENTS DATABASE SUMMARY
*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*

---

## 📊 DATABASE OVERVIEW

| Metric | Value |
|--------|--------|
| **Total Records** | {summary['database_info']['total_records']:,} |
| **Total Columns** | {summary['database_info']['total_columns']} |
| **File Size** | {summary['database_info']['file_size_mb']} MB |
| **Date Range** | {summary['database_info']['date_range']['start']} to {summary['database_info']['date_range']['end']} |
| **Time Span** | {summary['database_info']['date_range']['span_years']} years |

---

## 🗺️ GEOGRAPHIC COVERAGE

| Coverage | Count |
|----------|--------|
| **Cities** | {summary['geographic_coverage']['unique_cities']} |
| **ZIP Codes** | {summary['geographic_coverage']['unique_zip_codes']} |
| **Place Types** | {summary['geographic_coverage']['place_types']} |

### Top 5 Cities by Incident Count:
"""
    
    for i, (city, count) in enumerate(summary['geographic_coverage']['top_cities'].items(), 1):
        percentage = (count / summary['database_info']['total_records']) * 100
        report += f"{i}. **{city}**: {count:,} incidents ({percentage:.1f}%)\n"
    
    report += f"""
---

## 🚑 INCIDENT STATISTICS

| Metric | Value |
|--------|--------|
| **Unique Incident Types** | {summary['incident_statistics']['unique_incident_types']} |
| **Incident Categories** | {summary['incident_statistics']['unique_incident_categories']} |
| **Total Casualties** | {summary['incident_statistics']['total_casualties']:,} |
| **Incidents with Casualties** | {summary['incident_statistics']['incidents_with_casualties']:,} |

### Top 5 Incident Types:
"""
    
    for i, (incident, count) in enumerate(summary['incident_statistics']['top_incident_descriptions'].items(), 1):
        percentage = (count / summary['database_info']['total_records']) * 100
        report += f"{i}. **{incident}**: {count:,} incidents ({percentage:.1f}%)\n"
    
    report += f"""
---

## ⏱️ RESPONSE PERFORMANCE

| Metric | Value |
|--------|--------|
| **Average Response Time** | {summary['response_metrics']['average_response_time']} minutes |
| **Median Response Time** | {summary['response_metrics']['median_response_time']} minutes |
| **Fastest Response** | {summary['response_metrics']['fastest_response']} minutes |
| **Slowest Response** | {summary['response_metrics']['slowest_response']} minutes |
| **Average Units per Incident** | {summary['response_metrics']['average_units_responded']} |

---

## 🏥 MEDICAL OUTCOMES

### Transport Disposition:
"""
    
    total_transport = sum(summary['medical_outcomes']['transport_disposition'].values())
    for disposition, count in summary['medical_outcomes']['transport_disposition'].items():
        percentage = (count / total_transport) * 100
        report += f"- **{disposition}**: {count:,} ({percentage:.1f}%)\n"
    
    report += f"""
### Patient Care Evaluation:
"""
    
    total_care = sum(summary['medical_outcomes']['patient_care_evaluations'].values())
    for evaluation, count in summary['medical_outcomes']['patient_care_evaluations'].items():
        if pd.notna(evaluation):
            percentage = (count / total_care) * 100
            report += f"- **{evaluation}**: {count:,} ({percentage:.1f}%)\n"
    
    report += f"""
---

## 🔍 DATA QUALITY ASSESSMENT

### Data Completeness:
- **High Quality Fields** (>95% complete): {len([k for k, v in summary['data_quality']['completeness'].items() if v >= 95])} columns
- **Good Quality Fields** (80-95% complete): {len([k for k, v in summary['data_quality']['completeness'].items() if 80 <= v < 95])} columns
- **Poor Quality Fields** (<80% complete): {len([k for k, v in summary['data_quality']['completeness'].items() if v < 80])} columns

### Fields with Missing Data:
"""
    
    # Sort missing data by percentage
    sorted_missing = sorted(summary['data_quality']['missing_data_analysis'].items(), key=lambda x: x[1], reverse=True)
    for field, missing_pct in sorted_missing[:10]:  # Top 10 missing fields
        report += f"- **{field}**: {missing_pct}% missing\n"
    
    report += f"""
---

## 🎯 KEY INSIGHTS

### Performance Highlights:
- Emergency response system serves **{summary['geographic_coverage']['unique_cities']} cities** across Maryland
- Average response time of **{summary['response_metrics']['average_response_time']} minutes** demonstrates efficient emergency services
- **{summary['incident_statistics']['incidents_with_casualties']:,} incidents** resulted in casualties, representing {(summary['incident_statistics']['incidents_with_casualties']/summary['database_info']['total_records']*100):.1f}% of all calls

### Operational Insights:
- Most incidents occur in **{list(summary['geographic_coverage']['top_cities'].keys())[0]}** with {list(summary['geographic_coverage']['top_cities'].values())[0]:,} incidents
- **{list(summary['medical_outcomes']['transport_disposition'].keys())[0]}** is the most common transport outcome
- Database spans **{summary['database_info']['date_range']['span_years']} years** of comprehensive emergency response data

---

*This summary was automatically generated from the NERIS Emergency Incidents Database*
"""
    
    # Save both JSON and Markdown versions
    with open('/Users/test/emergency-incidents-analysis/database_summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    with open('/Users/test/emergency-incidents-analysis/database_summary.md', 'w') as f:
        f.write(report)
    
    print("📊 Database summary generated!")
    print("   - database_summary.json (structured data)")
    print("   - database_summary.md (formatted report)")
    
    return summary, report

if __name__ == "__main__":
    summary, report = generate_database_summary()
    print("\n" + "="*60)
    print("DATABASE SUMMARY PREVIEW")
    print("="*60)
    print(report[:1500] + "...")
    print("\n📄 Complete reports saved to files!")
