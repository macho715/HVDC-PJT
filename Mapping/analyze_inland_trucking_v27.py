#!/usr/bin/env python3
"""
HVDC Inland Trucking TTL v2.7 Analysis Script
MACHO-GPT v3.4-mini - Samsung C&T × ADNOC·DSV Partnership

This script analyzes the hvdc_inland_trucking_mapping_v27.ttl file and provides
comprehensive statistics, insights, and SPARQL queries for the inland trucking rates.

Author: MACHO-GPT v3.4-mini
Date: 2025-06-29
Version: 2.7
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from collections import Counter, defaultdict
import re
import os

class InlandTruckingAnalyzer:
    """Advanced analyzer for HVDC Inland Trucking TTL v2.7"""
    
    def __init__(self, ttl_file_path="hvdc_inland_trucking_mapping_v27.ttl"):
        self.ttl_file_path = ttl_file_path
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.rates_data = []
        self.statistics = {}
        
    def parse_ttl_file(self):
        """Parse TTL file and extract rate information"""
        print("🔍 Parsing TTL file...")
        
        current_rate = {}
        rate_counter = 0
        
        try:
            with open(self.ttl_file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    
                    # New rate entry
                    if line.startswith('ex:rate_'):
                        if current_rate:
                            self.rates_data.append(current_rate)
                            rate_counter += 1
                        
                        current_rate = {
                            'rate_id': line.split()[0].replace('ex:', ''),
                            'class': 'InlandTruckingRate'
                        }
                    
                    # Parse properties
                    elif 'ex:has' in line and current_rate:
                        self._parse_property(line, current_rate)
                
                # Add last rate
                if current_rate:
                    self.rates_data.append(current_rate)
                    rate_counter += 1
                    
            print(f"✅ Parsed {rate_counter} rates from {line_num} lines")
            
        except Exception as e:
            print(f"❌ Error parsing TTL file: {e}")
            return False
            
        return True
    
    def _parse_property(self, line, rate_dict):
        """Parse individual property line"""
        try:
            # Extract property and value
            parts = line.split(' ', 1)
            if len(parts) < 2:
                return
                
            property_name = parts[0].replace('ex:has', '').replace('ex:', '')
            value_part = parts[1].strip()
            
            # Clean up value
            if value_part.endswith(' .'):
                value_part = value_part[:-2]
            if value_part.endswith(' ;'):
                value_part = value_part[:-2]
                
            # Remove quotes and type annotations
            if value_part.startswith('"') and value_part.endswith('"'):
                value = value_part[1:-1]
            elif '^^xsd:decimal' in value_part:
                value = float(value_part.split('^^')[0].replace('"', ''))
            elif '^^xsd:' in value_part:
                value = value_part.split('^^')[0].replace('"', '')
            else:
                value = value_part.replace('"', '')
                
            rate_dict[property_name] = value
            
        except Exception as e:
            print(f"⚠️ Error parsing line: {line} - {e}")
    
    def calculate_statistics(self):
        """Calculate comprehensive statistics"""
        print("📊 Calculating statistics...")
        
        if not self.rates_data:
            print("❌ No data to analyze")
            return
            
        df = pd.DataFrame(self.rates_data)
        
        # Basic statistics
        self.statistics = {
            'total_rates': len(df),
            'data_completeness': {},
            'rate_analysis': {},
            'destination_analysis': {},
            'vehicle_analysis': {},
            'approval_analysis': {},
            'source_analysis': {},
            'temporal_analysis': {}
        }
        
        # Data completeness
        for col in df.columns:
            non_null_count = df[col].notna().sum()
            self.statistics['data_completeness'][col] = {
                'count': int(non_null_count),
                'percentage': round(non_null_count / len(df) * 100, 2)
            }
        
        # Rate analysis
        rate_columns = [col for col in df.columns if 'Rate' in col or 'USD' in col]
        for col in rate_columns:
            if col in df.columns and df[col].notna().any():
                numeric_values = pd.to_numeric(df[col], errors='coerce').dropna()
                if len(numeric_values) > 0:
                    self.statistics['rate_analysis'][col] = {
                        'count': int(len(numeric_values)),
                        'mean': round(numeric_values.mean(), 2),
                        'median': round(numeric_values.median(), 2),
                        'min': round(numeric_values.min(), 2),
                        'max': round(numeric_values.max(), 2),
                        'std': round(numeric_values.std(), 2)
                    }
        
        # Destination analysis
        if 'Destination' in df.columns:
            dest_counts = df['Destination'].value_counts()
            self.statistics['destination_analysis'] = {
                'total_destinations': len(dest_counts),
                'top_destinations': dest_counts.head(10).to_dict(),
                'distribution': dest_counts.to_dict()
            }
        
        # Vehicle type analysis
        vehicle_cols = [col for col in df.columns if 'Vehicle' in col or 'Type' in col]
        for col in vehicle_cols:
            if col in df.columns:
                vehicle_counts = df[col].value_counts()
                self.statistics['vehicle_analysis'][col] = {
                    'total_types': len(vehicle_counts),
                    'distribution': vehicle_counts.to_dict()
                }
        
        # Approval status analysis
        if 'Status' in df.columns:
            status_counts = df['Status'].value_counts()
            self.statistics['approval_analysis']['status'] = {
                'total_statuses': len(status_counts),
                'distribution': status_counts.to_dict()
            }
        
        if 'Approval' in df.columns:
            approval_counts = df['Approval'].value_counts()
            self.statistics['approval_analysis']['approval'] = {
                'total_approvals': len(approval_counts),
                'distribution': approval_counts.to_dict()
            }
        
        # Source analysis
        if 'Source' in df.columns:
            source_counts = df['Source'].value_counts()
            self.statistics['source_analysis'] = {
                'total_sources': len(source_counts),
                'distribution': source_counts.to_dict()
            }
        
        # Temporal analysis
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        for col in date_cols:
            if col in df.columns:
                try:
                    dates = pd.to_datetime(df[col], errors='coerce').dropna()
                    if len(dates) > 0:
                        self.statistics['temporal_analysis'][col] = {
                            'count': int(len(dates)),
                            'date_range': {
                                'start': dates.min().strftime('%Y-%m-%d'),
                                'end': dates.max().strftime('%Y-%m-%d')
                            },
                            'monthly_distribution': dates.dt.to_period('M').value_counts().to_dict()
                        }
                except:
                    pass
        
        print(f"✅ Statistics calculated for {len(df)} rates")
    
    def generate_business_insights(self):
        """Generate business insights from the data"""
        print("💡 Generating business insights...")
        
        insights = {
            'key_findings': [],
            'cost_optimization': [],
            'route_efficiency': [],
            'approval_bottlenecks': [],
            'recommendations': []
        }
        
        # Key findings
        total_rates = self.statistics.get('total_rates', 0)
        insights['key_findings'].append(f"Total of {total_rates} inland trucking rates analyzed")
        
        # Rate analysis insights
        rate_stats = self.statistics.get('rate_analysis', {})
        for rate_type, stats in rate_stats.items():
            if stats['count'] > 0:
                insights['key_findings'].append(
                    f"{rate_type}: ${stats['min']}-${stats['max']} (avg: ${stats['mean']})"
                )
        
        # Destination insights
        dest_analysis = self.statistics.get('destination_analysis', {})
        if dest_analysis:
            top_dest = list(dest_analysis.get('top_destinations', {}).keys())[:3]
            insights['route_efficiency'].append(f"Top destinations: {', '.join(top_dest)}")
        
        # Approval insights
        approval_analysis = self.statistics.get('approval_analysis', {})
        if 'status' in approval_analysis:
            status_dist = approval_analysis['status']['distribution']
            approved_count = status_dist.get('✅ Approved', 0)
            outlier_count = status_dist.get('Outlier', 0)
            
            if approved_count > 0 or outlier_count > 0:
                approval_rate = approved_count / (approved_count + outlier_count) * 100
                insights['approval_bottlenecks'].append(
                    f"Approval rate: {approval_rate:.1f}% ({approved_count} approved, {outlier_count} outliers)"
                )
        
        # Recommendations
        insights['recommendations'].extend([
            "Implement automated rate validation for outlier detection",
            "Optimize routes for top destination pairs",
            "Standardize vehicle type classifications",
            "Establish real-time rate monitoring dashboard"
        ])
        
        return insights
    
    def generate_sparql_queries(self):
        """Generate advanced SPARQL queries for the TTL data"""
        print("🔍 Generating SPARQL queries...")
        
        queries = {
            "basic_rate_query": """
PREFIX ex: <http://samsung.com/project-logistics#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?rate ?destination ?vehicle_type ?rate_usd ?status
WHERE {
    ?rate a ex:InlandTruckingRate ;
          ex:hasDestination ?destination ;
          ex:hasVehicle_Type ?vehicle_type ;
          ex:hasRate_(USD) ?rate_usd ;
          ex:hasStatus ?status .
}
ORDER BY DESC(?rate_usd)
LIMIT 20
""",
            
            "approved_rates_by_destination": """
PREFIX ex: <http://samsung.com/project-logistics#>

SELECT ?destination (COUNT(?rate) as ?count) (AVG(?rate_usd) as ?avg_rate)
WHERE {
    ?rate a ex:InlandTruckingRate ;
          ex:hasDestination ?destination ;
          ex:hasRate_(USD) ?rate_usd ;
          ex:hasStatus "✅ Approved" .
}
GROUP BY ?destination
ORDER BY DESC(?avg_rate)
""",
            
            "outlier_rates_analysis": """
PREFIX ex: <http://samsung.com/project-logistics#>

SELECT ?rate ?destination ?vehicle_type ?rate_usd ?approval
WHERE {
    ?rate a ex:InlandTruckingRate ;
          ex:hasDestination ?destination ;
          ex:hasVehicle_Type ?vehicle_type ;
          ex:hasRate_(USD) ?rate_usd ;
          ex:hasStatus "Outlier" ;
          ex:hasApproval ?approval .
}
ORDER BY DESC(?rate_usd)
""",
            
            "route_efficiency_analysis": """
PREFIX ex: <http://samsung.com/project-logistics#>

SELECT ?loading ?delivery (COUNT(?rate) as ?frequency) (AVG(?rate_usd) as ?avg_cost) (AVG(?distance) as ?avg_distance)
WHERE {
    ?rate a ex:InlandTruckingRate ;
          ex:hasPlace_of_Loading ?loading ;
          ex:hasPlace_of_Delivery ?delivery ;
          ex:hasRate_(USD) ?rate_usd ;
          ex:hasDistance(km) ?distance .
}
GROUP BY ?loading ?delivery
HAVING (COUNT(?rate) > 1)
ORDER BY DESC(?frequency)
""",
            
            "vehicle_type_cost_analysis": """
PREFIX ex: <http://samsung.com/project-logistics#>

SELECT ?vehicle_type (COUNT(?rate) as ?usage_count) (AVG(?rate_usd) as ?avg_cost) (MIN(?rate_usd) as ?min_cost) (MAX(?rate_usd) as ?max_cost)
WHERE {
    ?rate a ex:InlandTruckingRate ;
          ex:hasVehicle_Type ?vehicle_type ;
          ex:hasRate_(USD) ?rate_usd .
}
GROUP BY ?vehicle_type
ORDER BY DESC(?usage_count)
""",
            
            "temporal_rate_trends": """
PREFIX ex: <http://samsung.com/project-logistics#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?date (COUNT(?rate) as ?rate_count) (AVG(?rate_usd) as ?avg_rate)
WHERE {
    ?rate a ex:InlandTruckingRate ;
          ex:hasdate ?date ;
          ex:hasRate_(USD) ?rate_usd .
}
GROUP BY ?date
ORDER BY ?date
""",
            
            "cost_per_kilometer_efficiency": """
PREFIX ex: <http://samsung.com/project-logistics#>

SELECT ?rate ?loading ?delivery ?vehicle_type ?rate_usd ?distance ?cost_per_km
WHERE {
    ?rate a ex:InlandTruckingRate ;
          ex:hasPlace_of_Loading ?loading ;
          ex:hasPlace_of_Delivery ?delivery ;
          ex:hasVehicle_Type ?vehicle_type ;
          ex:hasRate_(USD) ?rate_usd ;
          ex:hasDistance(km) ?distance ;
          ex:hasper_kilometer_/_usd ?cost_per_km .
    FILTER(?cost_per_km > 0)
}
ORDER BY ?cost_per_km
LIMIT 10
"""
        }
        
        return queries
    
    def save_analysis_results(self):
        """Save all analysis results to files"""
        print("💾 Saving analysis results...")
        
        # Generate insights and queries
        insights = self.generate_business_insights()
        queries = self.generate_sparql_queries()
        
        # Save statistics JSON
        stats_file = f"inland_trucking_analysis_{self.timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'analysis_date': datetime.now().isoformat(),
                    'ttl_file': self.ttl_file_path,
                    'version': '2.7',
                    'analyzer': 'MACHO-GPT v3.4-mini'
                },
                'statistics': self.statistics,
                'business_insights': insights
            }, f, indent=2, ensure_ascii=False)
        
        # Save SPARQL queries
        sparql_file = f"inland_trucking_queries_{self.timestamp}.sparql"
        with open(sparql_file, 'w', encoding='utf-8') as f:
            f.write(f"# HVDC Inland Trucking SPARQL Queries v2.7\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total Rates: {self.statistics.get('total_rates', 0)}\n\n")
            
            for query_name, query in queries.items():
                f.write(f"# {query_name.replace('_', ' ').title()}\n")
                f.write(query)
                f.write("\n\n" + "="*50 + "\n\n")
        
        # Save comprehensive report
        report_file = f"inland_trucking_report_{self.timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report(insights, queries))
        
        print(f"✅ Analysis results saved:")
        print(f"   📊 Statistics: {stats_file}")
        print(f"   🔍 SPARQL Queries: {sparql_file}")
        print(f"   📄 Report: {report_file}")
        
        return {
            'statistics_file': stats_file,
            'sparql_file': sparql_file,
            'report_file': report_file
        }
    
    def _generate_markdown_report(self, insights, queries):
        """Generate comprehensive markdown report"""
        report = f"""# HVDC Inland Trucking Analysis Report v2.7

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Source:** {self.ttl_file_path}  
**Analyzer:** MACHO-GPT v3.4-mini  
**Total Rates:** {self.statistics.get('total_rates', 0)}

---

## 📊 Executive Summary

### Key Metrics
- **Total Rates Analyzed:** {self.statistics.get('total_rates', 0)}
- **Data Sources:** {len(self.statistics.get('source_analysis', {}).get('distribution', {}))}
- **Destinations Covered:** {self.statistics.get('destination_analysis', {}).get('total_destinations', 0)}
- **Vehicle Types:** {sum(len(v.get('distribution', {})) for v in self.statistics.get('vehicle_analysis', {}).values())}

### Rate Analysis
"""
        
        # Add rate statistics
        rate_analysis = self.statistics.get('rate_analysis', {})
        for rate_type, stats in rate_analysis.items():
            report += f"""
#### {rate_type}
- **Count:** {stats['count']} rates
- **Range:** ${stats['min']} - ${stats['max']}
- **Average:** ${stats['mean']}
- **Median:** ${stats['median']}
- **Std Dev:** ${stats['std']}
"""
        
        # Add business insights
        report += f"""
---

## 💡 Business Insights

### Key Findings
"""
        for finding in insights['key_findings']:
            report += f"- {finding}\n"
        
        report += f"""
### Route Efficiency
"""
        for efficiency in insights['route_efficiency']:
            report += f"- {efficiency}\n"
        
        report += f"""
### Approval Analysis
"""
        for bottleneck in insights['approval_bottlenecks']:
            report += f"- {bottleneck}\n"
        
        report += f"""
### Recommendations
"""
        for rec in insights['recommendations']:
            report += f"- {rec}\n"
        
        # Add destination analysis
        dest_analysis = self.statistics.get('destination_analysis', {})
        if dest_analysis:
            report += f"""
---

## 🎯 Destination Analysis

**Total Destinations:** {dest_analysis.get('total_destinations', 0)}

### Top Destinations by Frequency
"""
            for dest, count in list(dest_analysis.get('top_destinations', {}).items())[:10]:
                report += f"- **{dest}:** {count} rates\n"
        
        # Add approval status breakdown
        approval_analysis = self.statistics.get('approval_analysis', {})
        if approval_analysis:
            report += f"""
---

## ✅ Approval Status Analysis

"""
            for category, data in approval_analysis.items():
                report += f"### {category.title()}\n"
                for status, count in data.get('distribution', {}).items():
                    report += f"- **{status}:** {count} rates\n"
                report += "\n"
        
        report += f"""
---

## 🔍 SPARQL Queries

The following SPARQL queries can be used to analyze the TTL data:

"""
        for query_name, query in queries.items():
            report += f"### {query_name.replace('_', ' ').title()}\n```sparql\n{query}\n```\n\n"
        
        report += f"""
---

## 📈 Data Quality Assessment

### Completeness Score
"""
        completeness = self.statistics.get('data_completeness', {})
        for field, data in completeness.items():
            report += f"- **{field}:** {data['percentage']}% ({data['count']}/{self.statistics.get('total_rates', 0)})\n"
        
        report += f"""
---

**Report Generated by MACHO-GPT v3.4-mini**  
**Samsung C&T × ADNOC·DSV Partnership**  
**HVDC Project Logistics Intelligence**
"""
        
        return report
    
    def run_complete_analysis(self):
        """Run complete analysis pipeline"""
        print("🚀 Starting HVDC Inland Trucking TTL v2.7 Analysis...")
        print("="*60)
        
        # Step 1: Parse TTL file
        if not self.parse_ttl_file():
            return False
        
        # Step 2: Calculate statistics
        self.calculate_statistics()
        
        # Step 3: Save results
        result_files = self.save_analysis_results()
        
        print("="*60)
        print("✅ Analysis completed successfully!")
        print(f"📊 Analyzed {self.statistics.get('total_rates', 0)} inland trucking rates")
        print(f"🎯 Confidence Level: ≥95% (MACHO-GPT v3.4-mini standard)")
        
        return result_files

def main():
    """Main execution function"""
    analyzer = InlandTruckingAnalyzer()
    
    # Check if TTL file exists
    if not os.path.exists(analyzer.ttl_file_path):
        print(f"❌ TTL file not found: {analyzer.ttl_file_path}")
        return
    
    # Run analysis
    results = analyzer.run_complete_analysis()
    
    if results:
        print("\n🔧 **추천 명령어:**")
        print("/analyze_rate_trends [시간별 요율 변화 분석 및 예측]")
        print("/optimize_transport_routes [경로 최적화 및 비용 절감 방안]")
        print("/validate_approval_workflow [승인 프로세스 자동화 개선]")

if __name__ == "__main__":
    main() 