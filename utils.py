"""
Utility functions for the resume-job description comparison application.
Provides helper functions for data visualization, formatting, and common operations.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisualizationUtils:
    """Utility class for creating visualizations and charts."""
    
    @staticmethod
    def create_similarity_gauge(score: float, method: str = "Combined") -> go.Figure:
        """
        Create a gauge chart showing the similarity score.
        
        Args:
            score (float): Similarity score (0-100)
            method (str): Method used for calculation
            
        Returns:
            go.Figure: Plotly figure object
        """
        # Determine color based on score
        if score >= 80:
            color = "green"
        elif score >= 60:
            color = "lightgreen"
        elif score >= 40:
            color = "yellow"
        elif score >= 20:
            color = "orange"
        else:
            color = "red"
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"{method} Similarity Score"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 20], 'color': "lightgray"},
                    {'range': [20, 40], 'color': "gray"},
                    {'range': [40, 60], 'color': "lightyellow"},
                    {'range': [60, 80], 'color': "lightgreen"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            title=f"Resume-Job Description Match Score",
            font=dict(size=16),
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_method_comparison_chart(tfidf_score: float, bert_score: float) -> go.Figure:
        """
        Create a bar chart comparing TF-IDF and BERT scores.
        
        Args:
            tfidf_score (float): TF-IDF similarity score
            bert_score (float): BERT similarity score
            
        Returns:
            go.Figure: Plotly figure object
        """
        methods = ['TF-IDF', 'BERT']
        scores = [tfidf_score, bert_score]
        colors = ['#1f77b4', '#ff7f0e']
        
        fig = go.Figure(data=[
            go.Bar(
                x=methods,
                y=scores,
                marker_color=colors,
                text=[f"{score:.1f}%" for score in scores],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Similarity Score Comparison by Method",
            xaxis_title="Method",
            yaxis_title="Similarity Score (%)",
            yaxis=dict(range=[0, 100]),
            height=400,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_keyword_analysis_chart(important_features: Dict[str, Any]) -> go.Figure:
        """
        Create a chart showing keyword analysis results.
        
        Args:
            important_features (Dict[str, Any]): TF-IDF important features
            
        Returns:
            go.Figure: Plotly figure object
        """
        if not important_features or 'common_features' not in important_features:
            return go.Figure()
        
        common_features = important_features['common_features'][:15]  # Top 15
        
        if not common_features:
            return go.Figure()
        
        features = [item['feature'] for item in common_features]
        avg_scores = [item['average_score'] for item in common_features]
        
        fig = go.Figure(data=[
            go.Bar(
                x=avg_scores,
                y=features,
                orientation='h',
                marker_color='lightblue',
                text=[f"{score:.4f}" for score in avg_scores],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Top Common Keywords (TF-IDF Analysis)",
            xaxis_title="Average TF-IDF Score",
            yaxis_title="Keywords",
            height=max(400, len(features) * 25),
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_text_statistics_chart(job_desc_stats: Dict[str, Any], 
                                   resume_stats: Dict[str, Any]) -> go.Figure:
        """
        Create a chart comparing text statistics between job description and resume.
        
        Args:
            job_desc_stats (Dict[str, Any]): Job description statistics
            resume_stats (Dict[str, Any]): Resume statistics
            
        Returns:
            go.Figure: Plotly figure object
        """
        if not job_desc_stats or not resume_stats:
            return go.Figure()
        
        metrics = ['word_count', 'sentence_count', 'character_count']
        job_values = [job_desc_stats.get(metric, 0) for metric in metrics]
        resume_values = [resume_stats.get(metric, 0) for metric in metrics]
        
        fig = go.Figure(data=[
            go.Bar(
                name='Job Description',
                x=metrics,
                y=job_values,
                marker_color='#1f77b4'
            ),
            go.Bar(
                name='Resume',
                x=metrics,
                y=resume_values,
                marker_color='#ff7f0e'
            )
        ])
        
        fig.update_layout(
            title="Text Statistics Comparison",
            xaxis_title="Metrics",
            yaxis_title="Count",
            barmode='group',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_confidence_indicator(confidence: str) -> str:
        """
        Create a visual confidence indicator.
        
        Args:
            confidence (str): Confidence level
            
        Returns:
            str: HTML string with confidence indicator
        """
        confidence_colors = {
            'very_low': '🔴',
            'low': '🟠',
            'medium': '🟡',
            'high': '🟢',
            'very_high': '🟢'
        }
        
        confidence_labels = {
            'very_low': 'Very Low',
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High',
            'very_high': 'Very High'
        }
        
        emoji = confidence_colors.get(confidence, '⚪')
        label = confidence_labels.get(confidence, confidence.title())
        
        return f"{emoji} {label} Confidence"


class DataUtils:
    """Utility class for data processing and formatting."""
    
    @staticmethod
    def format_percentage(value: float, decimal_places: int = 2) -> str:
        """
        Format a decimal value as a percentage string.
        
        Args:
            value (float): Decimal value (0-1)
            decimal_places (int): Number of decimal places
            
        Returns:
            str: Formatted percentage string
        """
        if value is None:
            return "N/A"
        
        percentage = value * 100
        return f"{percentage:.{decimal_places}f}%"
    
    @staticmethod
    def format_score(score: float, decimal_places: int = 2) -> str:
        """
        Format a similarity score.
        
        Args:
            score (float): Score value
            decimal_places (int): Number of decimal places
            
        Returns:
            str: Formatted score string
        """
        if score is None:
            return "N/A"
        
        return f"{score:.{decimal_places}f}%"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """
        Truncate text to a maximum length.
        
        Args:
            text (str): Input text
            max_length (int): Maximum length
            suffix (str): Suffix to add when truncating
            
        Returns:
            str: Truncated text
        """
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def clean_text_for_display(text: str, max_length: int = 200) -> str:
        """
        Clean and format text for display purposes.
        
        Args:
            text (str): Input text
            max_length (int): Maximum length for display
            
        Returns:
            str: Cleaned and formatted text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    
    @staticmethod
    def extract_file_extension(filename: str) -> str:
        """
        Extract file extension from filename.
        
        Args:
            filename (str): Filename
            
        Returns:
            str: File extension (with dot)
        """
        if not filename:
            return ""
        
        # Find the last dot
        last_dot = filename.rfind('.')
        if last_dot == -1:
            return ""
        
        return filename[last_dot:].lower()
    
    @staticmethod
    def get_file_size_display(size_bytes: int) -> str:
        """
        Convert file size in bytes to human-readable format.
        
        Args:
            size_bytes (int): Size in bytes
            
        Returns:
            str: Human-readable size string
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


class ValidationUtils:
    """Utility class for data validation."""
    
    @staticmethod
    def validate_text_input(text: str, min_length: int = 10, max_length: int = 50000) -> Tuple[bool, str]:
        """
        Validate text input for processing.
        
        Args:
            text (str): Text to validate
            min_length (int): Minimum required length
            max_length (int): Maximum allowed length
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not text:
            return False, "Text input is required"
        
        if not isinstance(text, str):
            return False, "Text input must be a string"
        
        text_length = len(text.strip())
        
        if text_length < min_length:
            return False, f"Text must be at least {min_length} characters long"
        
        if text_length > max_length:
            return False, f"Text must be no more than {max_length} characters long"
        
        return True, ""
    
    @staticmethod
    def validate_similarity_score(score: float) -> Tuple[bool, str]:
        """
        Validate similarity score.
        
        Args:
            score (float): Score to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not isinstance(score, (int, float)):
            return False, "Score must be a number"
        
        if score < 0 or score > 100:
            return False, "Score must be between 0 and 100"
        
        return True, ""
    
    @staticmethod
    def validate_file_path(file_path: str) -> Tuple[bool, str]:
        """
        Validate file path.
        
        Args:
            file_path (str): File path to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not file_path:
            return False, "File path is required"
        
        if not isinstance(file_path, str):
            return False, "File path must be a string"
        
        # Check if path contains invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in file_path for char in invalid_chars):
            return False, "File path contains invalid characters"
        
        return True, ""


class ExportUtils:
    """Utility class for exporting data."""
    
    @staticmethod
    def export_results_to_json(results: Dict[str, Any], file_path: str) -> Tuple[bool, str]:
        """
        Export results to JSON file.
        
        Args:
            results (Dict[str, Any]): Results to export
            file_path (str): Output file path
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        try:
            # Add export timestamp
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'results': results
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results exported to {file_path}")
            return True, ""
            
        except Exception as e:
            error_msg = f"Error exporting results: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def export_results_to_csv(results: Dict[str, Any], file_path: str) -> Tuple[bool, str]:
        """
        Export results to CSV file.
        
        Args:
            results (Dict[str, Any]): Results to export
            file_path (str): Output file path
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        try:
            # Flatten results for CSV export
            flat_data = []
            
            def flatten_dict(data, prefix=""):
                for key, value in data.items():
                    new_key = f"{prefix}.{key}" if prefix else key
                    if isinstance(value, dict):
                        flatten_dict(value, new_key)
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            if isinstance(item, dict):
                                flatten_dict(item, f"{new_key}[{i}]")
                            else:
                                flat_data.append([f"{new_key}[{i}]", str(item)])
                    else:
                        flat_data.append([new_key, str(value)])
            
            flatten_dict(results)
            
            # Create DataFrame and export
            df = pd.DataFrame(flat_data, columns=['Key', 'Value'])
            df.to_csv(file_path, index=False, encoding='utf-8')
            
            logger.info(f"Results exported to {file_path}")
            return True, ""
            
        except Exception as e:
            error_msg = f"Error exporting results: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def create_summary_report(results: Dict[str, Any]) -> str:
        """
        Create a human-readable summary report.
        
        Args:
            results (Dict[str, Any]): Analysis results
            
        Returns:
            str: Formatted summary report
        """
        if not results:
            return "No results available for summary."
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("RESUME-JOB DESCRIPTION ANALYSIS SUMMARY")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # Overall score
        if 'overall_score' in results:
            report_lines.append(f"Overall Match Score: {results['overall_score']}%")
            report_lines.append("")
        
        # Method comparison
        if 'methods' in results:
            methods = results['methods']
            if 'tfidf' in methods:
                report_lines.append(f"TF-IDF Score: {methods['tfidf'].get('similarity_score', 'N/A')}%")
            if 'bert' in methods:
                report_lines.append(f"BERT Score: {methods['bert'].get('similarity_score', 'N/A')}%")
            report_lines.append("")
        
        # Recommendations
        if 'recommendations' in results:
            report_lines.append("RECOMMENDATIONS:")
            for i, rec in enumerate(results['recommendations'], 1):
                report_lines.append(f"{i}. {rec}")
            report_lines.append("")
        
        # Text analysis
        if 'text_analysis' in results:
            text_analysis = results['text_analysis']
            if 'job_description' in text_analysis:
                job_stats = text_analysis['job_description']
                report_lines.append(f"Job Description: {job_stats.get('word_count', 0)} words")
            if 'resume' in text_analysis:
                resume_stats = text_analysis['resume']
                report_lines.append(f"Resume: {resume_stats.get('word_count', 0)} words")
            report_lines.append("")
        
        report_lines.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
