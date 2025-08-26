"""
Advanced HR Analytics Dashboard Module for IKF HR Platform
Comprehensive analytics for hiring metrics, diversity tracking, and recruitment insights.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from collections import defaultdict, Counter
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HRAnalyticsDashboard:
    """
    Comprehensive HR Analytics Dashboard for recruitment insights.
    Provides hiring funnel analytics, diversity metrics, and performance tracking.
    """
    
    def __init__(self):
        """Initialize the analytics dashboard."""
        self.recruitment_data = []
        self.candidate_data = []
        self.hiring_data = []
        self.diversity_data = []
        
        # Analytics cache
        self.analytics_cache = {}
        self.cache_timestamp = None
        self.cache_duration = timedelta(hours=1)
        
        logger.info("HR Analytics Dashboard initialized successfully")
    
    def add_recruitment_record(self, record: Dict[str, Any]):
        """Add a new recruitment record to the analytics system."""
        try:
            # Ensure required fields
            required_fields = ['candidate_id', 'position', 'source', 'date_applied', 'status']
            for field in required_fields:
                if field not in record:
                    logger.warning(f"Missing required field: {field}")
                    return False
            
            # Add timestamp if not present
            if 'timestamp' not in record:
                record['timestamp'] = datetime.now().isoformat()
            
            # Add to recruitment data
            self.recruitment_data.append(record)
            
            # Clear cache to ensure fresh analytics
            self._clear_cache()
            
            logger.info(f"Added recruitment record for candidate: {record['candidate_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding recruitment record: {str(e)}")
            return False
    
    def add_candidate_data(self, candidate: Dict[str, Any]):
        """Add candidate demographic and profile data."""
        try:
            required_fields = ['candidate_id', 'age', 'gender', 'ethnicity', 'location']
            for field in required_fields:
                if field not in candidate:
                    logger.warning(f"Missing required field: {field}")
                    return False
            
            # Add timestamp
            candidate['timestamp'] = datetime.now().isoformat()
            
            # Add to candidate data
            self.candidate_data.append(candidate)
            
            # Clear cache
            self._clear_cache()
            
            logger.info(f"Added candidate data for: {candidate['candidate_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding candidate data: {str(e)}")
            return False
    
    def add_hiring_record(self, hiring: Dict[str, Any]):
        """Add hiring outcome data."""
        try:
            required_fields = ['candidate_id', 'position', 'hire_date', 'salary', 'retention_days']
            for field in required_fields:
                if field not in hiring:
                    logger.warning(f"Missing required field: {field}")
                    return False
            
            # Add timestamp
            hiring['timestamp'] = datetime.now().isoformat()
            
            # Add to hiring data
            self.hiring_data.append(hiring)
            
            # Clear cache
            self._clear_cache()
            
            logger.info(f"Added hiring record for: {hiring['candidate_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding hiring record: {str(e)}")
            return False
    
    def get_hiring_funnel_analytics(self, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """
        Analyze hiring funnel metrics and conversion rates.
        
        Args:
            date_range (Optional[Tuple[datetime, datetime]]): Date range for analysis
            
        Returns:
            Dict[str, Any]: Hiring funnel analytics
        """
        try:
            # Check cache first
            cache_key = f"funnel_analytics_{date_range}"
            if self._is_cache_valid(cache_key):
                return self.analytics_cache[cache_key]
            
            # Filter data by date range
            filtered_data = self._filter_data_by_date(self.recruitment_data, date_range)
            
            if not filtered_data:
                return self._empty_funnel_analytics()
            
            # Calculate funnel metrics
            funnel_data = self._calculate_funnel_metrics(filtered_data)
            
            # Calculate conversion rates
            conversion_rates = self._calculate_conversion_rates(funnel_data)
            
            # Calculate time metrics
            time_metrics = self._calculate_time_metrics(filtered_data)
            
            # Generate funnel chart
            funnel_chart = self._create_funnel_chart(funnel_data)
            
            analytics = {
                'funnel_data': funnel_data,
                'conversion_rates': conversion_rates,
                'time_metrics': time_metrics,
                'funnel_chart': funnel_chart,
                'summary': self._generate_funnel_summary(funnel_data, conversion_rates),
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache results
            self._cache_results(cache_key, analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error in hiring funnel analytics: {str(e)}")
            return self._empty_funnel_analytics()
    
    def get_time_to_hire_metrics(self, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """
        Analyze time-to-hire metrics and recruitment efficiency.
        
        Args:
            date_range (Optional[Tuple[datetime, datetime]]): Date range for analysis
            
        Returns:
            Dict[str, Any]: Time-to-hire analytics
        """
        try:
            cache_key = f"time_to_hire_{date_range}"
            if self._is_cache_valid(cache_key):
                return self.analytics_cache[cache_key]
            
            # Filter data
            filtered_recruitment = self._filter_data_by_date(self.recruitment_data, date_range)
            filtered_hiring = self._filter_data_by_date(self.hiring_data, date_range)
            
            if not filtered_recruitment or not filtered_hiring:
                return self._empty_time_to_hire_analytics()
            
            # Calculate time metrics
            time_metrics = self._calculate_detailed_time_metrics(filtered_recruitment, filtered_hiring)
            
            # Calculate efficiency metrics
            efficiency_metrics = self._calculate_efficiency_metrics(filtered_recruitment, filtered_hiring)
            
            # Generate time series chart
            time_series_chart = self._create_time_series_chart(filtered_recruitment, filtered_hiring)
            
            analytics = {
                'time_metrics': time_metrics,
                'efficiency_metrics': efficiency_metrics,
                'time_series_chart': time_series_chart,
                'bottleneck_analysis': self._identify_bottlenecks(filtered_recruitment),
                'optimization_recommendations': self._generate_optimization_recommendations(time_metrics),
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache results
            self._cache_results(cache_key, analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error in time-to-hire analytics: {str(e)}")
            return self._empty_time_to_hire_analytics()
    
    def get_diversity_analytics(self, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """
        Analyze diversity and inclusion metrics.
        
        Args:
            date_range (Optional[Tuple[datetime, datetime]]): Date range for analysis
            
        Returns:
            Dict[str, Any]: Diversity analytics
        """
        try:
            cache_key = f"diversity_analytics_{date_range}"
            if self._is_cache_valid(cache_key):
                return self.analytics_cache[cache_key]
            
            # Filter data
            filtered_candidates = self._filter_data_by_date(self.candidate_data, date_range)
            filtered_hiring = self._filter_data_by_date(self.hiring_data, date_range)
            
            if not filtered_candidates:
                return self._empty_diversity_analytics()
            
            # Calculate diversity metrics
            diversity_metrics = self._calculate_diversity_metrics(filtered_candidates, filtered_hiring)
            
            # Calculate representation metrics
            representation_metrics = self._calculate_representation_metrics(filtered_candidates, filtered_hiring)
            
            # Generate diversity charts
            diversity_charts = self._create_diversity_charts(diversity_metrics, representation_metrics)
            
            analytics = {
                'diversity_metrics': diversity_metrics,
                'representation_metrics': representation_metrics,
                'diversity_charts': diversity_charts,
                'inclusion_score': self._calculate_inclusion_score(diversity_metrics),
                'diversity_recommendations': self._generate_diversity_recommendations(diversity_metrics),
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache results
            self._cache_results(cache_key, analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error in diversity analytics: {str(e)}")
            return self._empty_diversity_analytics()
    
    def get_source_effectiveness_analytics(self, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """
        Analyze recruitment source effectiveness.
        
        Args:
            date_range (Optional[Tuple[datetime, datetime]]): Date range for analysis
            
        Returns:
            Dict[str, Any]: Source effectiveness analytics
        """
        try:
            cache_key = f"source_effectiveness_{date_range}"
            if self._is_cache_valid(cache_key):
                return self.analytics_cache[cache_key]
            
            # Filter data
            filtered_recruitment = self._filter_data_by_date(self.recruitment_data, date_range)
            filtered_hiring = self._filter_data_by_date(self.hiring_data, date_range)
            
            if not filtered_recruitment:
                return self._empty_source_effectiveness_analytics()
            
            # Calculate source metrics
            source_metrics = self._calculate_source_metrics(filtered_recruitment, filtered_hiring)
            
            # Calculate ROI metrics
            roi_metrics = self._calculate_source_roi(filtered_recruitment, filtered_hiring)
            
            # Generate source charts
            source_charts = self._create_source_charts(source_metrics, roi_metrics)
            
            analytics = {
                'source_metrics': source_metrics,
                'roi_metrics': roi_metrics,
                'source_charts': source_charts,
                'top_performing_sources': self._identify_top_sources(source_metrics),
                'optimization_recommendations': self._generate_source_optimization_recommendations(source_metrics),
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache results
            self._cache_results(cache_key, analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error in source effectiveness analytics: {str(e)}")
            return self._empty_source_effectiveness_analytics()
    
    def get_cost_per_hire_analytics(self, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """
        Analyze cost-per-hire and recruitment ROI.
        
        Args:
            date_range (Optional[Tuple[datetime, datetime]]): Date range for analysis
            
        Returns:
            Dict[str, Any]: Cost-per-hire analytics
        """
        try:
            cache_key = f"cost_per_hire_{date_range}"
            if self._is_cache_valid(cache_key):
                return self.analytics_cache[cache_key]
            
            # Filter data
            filtered_recruitment = self._filter_data_by_date(self.recruitment_data, date_range)
            filtered_hiring = self._filter_data_by_date(self.hiring_data, date_range)
            
            if not filtered_recruitment or not filtered_hiring:
                return self._empty_cost_per_hire_analytics()
            
            # Calculate cost metrics
            cost_metrics = self._calculate_cost_metrics(filtered_recruitment, filtered_hiring)
            
            # Calculate ROI metrics
            roi_metrics = self._calculate_recruitment_roi(filtered_recruitment, filtered_hiring)
            
            # Generate cost charts
            cost_charts = self._create_cost_charts(cost_metrics, roi_metrics)
            
            analytics = {
                'cost_metrics': cost_metrics,
                'roi_metrics': roi_metrics,
                'cost_charts': cost_charts,
                'cost_breakdown': self._breakdown_recruitment_costs(filtered_recruitment),
                'optimization_opportunities': self._identify_cost_optimization_opportunities(cost_metrics),
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache results
            self._cache_results(cache_key, analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error in cost-per-hire analytics: {str(e)}")
            return self._empty_cost_per_hire_analytics()
    
    def get_comprehensive_dashboard(self, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """
        Get comprehensive analytics dashboard with all metrics.
        
        Args:
            date_range (Optional[Tuple[datetime, datetime]]): Date range for analysis
            
        Returns:
            Dict[str, Any]: Comprehensive dashboard data
        """
        try:
            # Get all analytics
            funnel_analytics = self.get_hiring_funnel_analytics(date_range)
            time_analytics = self.get_time_to_hire_metrics(date_range)
            diversity_analytics = self.get_diversity_analytics(date_range)
            source_analytics = self.get_source_effectiveness_analytics(date_range)
            cost_analytics = self.get_cost_per_hire_analytics(date_range)
            
            # Calculate overall KPIs
            overall_kpis = self._calculate_overall_kpis(
                funnel_analytics, time_analytics, diversity_analytics, 
                source_analytics, cost_analytics
            )
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(
                funnel_analytics, time_analytics, diversity_analytics,
                source_analytics, cost_analytics
            )
            
            dashboard = {
                'overall_kpis': overall_kpis,
                'executive_summary': executive_summary,
                'funnel_analytics': funnel_analytics,
                'time_analytics': time_analytics,
                'diversity_analytics': diversity_analytics,
                'source_analytics': source_analytics,
                'cost_analytics': cost_analytics,
                'timestamp': datetime.now().isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error in comprehensive dashboard: {str(e)}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _filter_data_by_date(self, data: List[Dict], date_range: Optional[Tuple[datetime, datetime]]) -> List[Dict]:
        """Filter data by date range."""
        if not date_range:
            return data
        
        start_date, end_date = date_range
        filtered_data = []
        
        for record in data:
            try:
                record_date = datetime.fromisoformat(record.get('date_applied', record.get('timestamp', '')))
                if start_date <= record_date <= end_date:
                    filtered_data.append(record)
            except (ValueError, TypeError):
                continue
        
        return filtered_data
    
    def _calculate_funnel_metrics(self, data: List[Dict]) -> Dict[str, int]:
        """Calculate hiring funnel metrics."""
        funnel = {
            'applications': len(data),
            'screening': 0,
            'interview': 0,
            'offer': 0,
            'hired': 0
        }
        
        for record in data:
            status = record.get('status', '').lower()
            if 'screening' in status or 'review' in status:
                funnel['screening'] += 1
            elif 'interview' in status:
                funnel['interview'] += 1
            elif 'offer' in status:
                funnel['offer'] += 1
            elif 'hired' in status or 'accepted' in status:
                funnel['hired'] += 1
        
        return funnel
    
    def _calculate_conversion_rates(self, funnel_data: Dict[str, int]) -> Dict[str, float]:
        """Calculate conversion rates between funnel stages."""
        rates = {}
        
        if funnel_data['applications'] > 0:
            rates['screening_rate'] = funnel_data['screening'] / funnel_data['applications']
            rates['interview_rate'] = funnel_data['interview'] / funnel_data['applications']
            rates['offer_rate'] = funnel_data['offer'] / funnel_data['applications']
            rates['hire_rate'] = funnel_data['hired'] / funnel_data['applications']
        
        if funnel_data['screening'] > 0:
            rates['screening_to_interview'] = funnel_data['interview'] / funnel_data['screening']
        
        if funnel_data['interview'] > 0:
            rates['interview_to_offer'] = funnel_data['offer'] / funnel_data['interview']
        
        if funnel_data['offer'] > 0:
            rates['offer_to_hire'] = funnel_data['hired'] / funnel_data['offer']
        
        return rates
    
    def _calculate_time_metrics(self, data: List[Dict]) -> Dict[str, float]:
        """Calculate time-based metrics."""
        time_metrics = {
            'avg_time_to_screening': 0,
            'avg_time_to_interview': 0,
            'avg_time_to_offer': 0,
            'avg_time_to_hire': 0
        }
        
        # Implementation would calculate actual time differences
        # For now, return placeholder values
        return time_metrics
    
    def _create_funnel_chart(self, funnel_data: Dict[str, int]) -> go.Figure:
        """Create funnel chart for hiring stages."""
        stages = list(funnel_data.keys())
        values = list(funnel_data.values())
        
        fig = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            textposition="inside",
            marker={"color": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]},
            connector={"line": {"color": "royalblue", "width": 3}}
        ))
        
        fig.update_layout(
            title="Hiring Funnel Analysis",
            height=500,
            showlegend=False
        )
        
        return fig
    
    def _generate_funnel_summary(self, funnel_data: Dict[str, int], conversion_rates: Dict[str, float]) -> str:
        """Generate summary of funnel performance."""
        total_applications = funnel_data['applications']
        total_hires = funnel_data['hired']
        
        if total_applications == 0:
            return "No applications in the selected period."
        
        overall_conversion = (total_hires / total_applications) * 100
        
        summary = f"""
        **Hiring Funnel Summary:**
        - **Total Applications:** {total_applications}
        - **Total Hires:** {total_hires}
        - **Overall Conversion Rate:** {overall_conversion:.1f}%
        - **Top Funnel Stage:** {max(funnel_data, key=funnel_data.get)}
        - **Bottleneck Stage:** {min(funnel_data, key=funnel_data.get)}
        """
        
        return summary
    
    def _empty_funnel_analytics(self) -> Dict[str, Any]:
        """Return empty funnel analytics structure."""
        return {
            'funnel_data': {},
            'conversion_rates': {},
            'time_metrics': {},
            'funnel_chart': None,
            'summary': "No data available for the selected period.",
            'timestamp': datetime.now().isoformat()
        }
    
    def _empty_time_to_hire_analytics(self) -> Dict[str, Any]:
        """Return empty time-to-hire analytics structure."""
        return {
            'time_metrics': {},
            'efficiency_metrics': {},
            'time_series_chart': None,
            'bottleneck_analysis': [],
            'optimization_recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
    
    def _empty_diversity_analytics(self) -> Dict[str, Any]:
        """Return empty diversity analytics structure."""
        return {
            'diversity_metrics': {},
            'representation_metrics': {},
            'diversity_charts': {},
            'inclusion_score': 0,
            'diversity_recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
    
    def _empty_source_effectiveness_analytics(self) -> Dict[str, Any]:
        """Return empty source effectiveness analytics structure."""
        return {
            'source_metrics': {},
            'roi_metrics': {},
            'source_charts': {},
            'top_performing_sources': [],
            'optimization_recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
    
    def _empty_cost_per_hire_analytics(self) -> Dict[str, Any]:
        """Return empty cost-per-hire analytics structure."""
        return {
            'cost_metrics': {},
            'roi_metrics': {},
            'cost_charts': {},
            'cost_breakdown': {},
            'optimization_opportunities': [],
            'timestamp': datetime.now().isoformat()
        }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self.analytics_cache:
            return False
        
        if self.cache_timestamp is None:
            return False
        
        return datetime.now() - self.cache_timestamp < self.cache_duration
    
    def _cache_results(self, cache_key: str, results: Dict[str, Any]):
        """Cache analytics results."""
        self.analytics_cache[cache_key] = results
        self.cache_timestamp = datetime.now()
    
    def _clear_cache(self):
        """Clear analytics cache."""
        self.analytics_cache.clear()
        self.cache_timestamp = None
    
    # Additional helper methods would be implemented here for:
    # - _calculate_detailed_time_metrics
    # - _calculate_efficiency_metrics
    # - _identify_bottlenecks
    # - _generate_optimization_recommendations
    # - _calculate_diversity_metrics
    # - _calculate_representation_metrics
    # - _create_diversity_charts
    # - _calculate_inclusion_score
    # - _generate_diversity_recommendations
    # - _calculate_source_metrics
    # - _calculate_source_roi
    # - _create_source_charts
    # - _identify_top_sources
    # - _generate_source_optimization_recommendations
    # - _calculate_cost_metrics
    # - _calculate_recruitment_roi
    # - _create_cost_charts
    # - _breakdown_recruitment_costs
    # - _identify_cost_optimization_opportunities
    # - _calculate_overall_kpis
    # - _generate_executive_summary
    
    def export_analytics_report(self, date_range: Optional[Tuple[datetime, datetime]] = None, 
                              format: str = 'json') -> str:
        """
        Export analytics report in specified format.
        
        Args:
            date_range (Optional[Tuple[datetime, datetime]]): Date range for analysis
            format (str): Export format ('json', 'csv', 'excel')
            
        Returns:
            str: File path to exported report
        """
        try:
            dashboard_data = self.get_comprehensive_dashboard(date_range)
            
            if format.lower() == 'json':
                return self._export_json_report(dashboard_data)
            elif format.lower() == 'csv':
                return self._export_csv_report(dashboard_data)
            elif format.lower() == 'excel':
                return self._export_excel_report(dashboard_data)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting analytics report: {str(e)}")
            return ""
    
    def _export_json_report(self, data: Dict[str, Any]) -> str:
        """Export report as JSON file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hr_analytics_report_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"JSON report exported to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting JSON report: {str(e)}")
            return ""
    
    def _export_csv_report(self, data: Dict[str, Any]) -> str:
        """Export report as CSV file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hr_analytics_report_{timestamp}.csv"
            
            # Flatten the nested data structure for CSV export
            flattened_data = self._flatten_data_for_csv(data)
            
            df = pd.DataFrame(flattened_data)
            df.to_csv(filename, index=False)
            
            logger.info(f"CSV report exported to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting CSV report: {str(e)}")
            return ""
    
    def _export_excel_report(self, data: Dict[str, Any]) -> str:
        """Export report as Excel file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hr_analytics_report_{timestamp}.xlsx"
            
            # Create Excel writer
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Export different sections to different sheets
                self._export_excel_sheets(data, writer)
            
            logger.info(f"Excel report exported to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting Excel report: {str(e)}")
            return ""
    
    def _flatten_data_for_csv(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Flatten nested data structure for CSV export."""
        flattened = []
        
        def flatten_dict(d, prefix=''):
            for key, value in d.items():
                if isinstance(value, dict):
                    flatten_dict(value, f"{prefix}{key}_")
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            flatten_dict(item, f"{prefix}{key}_{i}_")
                        else:
                            flattened.append({f"{prefix}{key}_{i}": item})
                else:
                    flattened.append({f"{prefix}{key}": value})
        
        flatten_dict(data)
        return flattened
    
    def _export_excel_sheets(self, data: Dict[str, Any], writer: pd.ExcelWriter):
        """Export different data sections to Excel sheets."""
        # Overview sheet
        overview_data = {
            'Metric': ['Total Applications', 'Total Hires', 'Overall Conversion Rate'],
            'Value': [
                data.get('overall_kpis', {}).get('total_applications', 0),
                data.get('overall_kpis', {}).get('total_hires', 0),
                f"{data.get('overall_kpis', {}).get('overall_conversion_rate', 0):.1f}%"
            ]
        }
        pd.DataFrame(overview_data).to_excel(writer, sheet_name='Overview', index=False)
        
        # Funnel Analytics sheet
        if 'funnel_analytics' in data:
            funnel_df = pd.DataFrame([data['funnel_analytics']['funnel_data']])
            funnel_df.to_excel(writer, sheet_name='Funnel Analytics', index=False)
        
        # Time Analytics sheet
        if 'time_analytics' in data:
            time_df = pd.DataFrame([data['time_analytics']['time_metrics']])
            time_df.to_excel(writer, sheet_name='Time Analytics', index=False)
        
        # Diversity Analytics sheet
        if 'diversity_analytics' in data:
            diversity_df = pd.DataFrame([data['diversity_analytics']['diversity_metrics']])
            diversity_df.to_excel(writer, sheet_name='Diversity Analytics', index=False)
