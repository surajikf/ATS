"""
Market Intelligence Module for IKF HR Platform
Salary benchmarking, skills demand analysis, and competitive intelligence.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import requests
import json
import streamlit as st

logger = logging.getLogger(__name__)

class MarketIntelligence:
    """Market intelligence and competitive analysis for HR decisions."""
    
    def __init__(self):
        """Initialize market intelligence system."""
        self.salary_data = {}
        self.skills_data = {}
        self.market_trends = {}
        self.competitor_data = {}
        
        # API endpoints (placeholder)
        self.salary_api = "https://api.salary.com/v1"
        self.skills_api = "https://api.skills.com/v1"
        self.market_api = "https://api.market.com/v1"
        
        logger.info("Market Intelligence initialized")
    
    def get_salary_benchmark(self, position: str, location: str, experience_years: int) -> Dict[str, Any]:
        """Get salary benchmark for a position."""
        try:
            # Mock data - in real implementation, this would call external APIs
            base_salaries = {
                'Software Engineer': 80000,
                'Data Scientist': 90000,
                'Product Manager': 100000,
                'DevOps Engineer': 85000,
                'UX Designer': 75000
            }
            
            base_salary = base_salaries.get(position, 70000)
            
            # Location adjustment
            location_multipliers = {
                'San Francisco': 1.4,
                'New York': 1.3,
                'Seattle': 1.2,
                'Austin': 1.1,
                'Remote': 0.9
            }
            
            location_mult = location_multipliers.get(location, 1.0)
            
            # Experience adjustment
            exp_multiplier = 1 + (experience_years * 0.1)
            
            # Calculate benchmark
            benchmark_salary = base_salary * location_mult * exp_multiplier
            
            return {
                'position': position,
                'location': location,
                'experience_years': experience_years,
                'benchmark_salary': round(benchmark_salary, 2),
                'percentile_25': round(benchmark_salary * 0.8, 2),
                'percentile_50': round(benchmark_salary, 2),
                'percentile_75': round(benchmark_salary * 1.2, 2),
                'market_trend': 'Increasing',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting salary benchmark: {str(e)}")
            return {}
    
    def get_skills_demand_analysis(self, skills: List[str], location: str = "Global") -> Dict[str, Any]:
        """Analyze demand for specific skills."""
        try:
            # Mock skills demand data
            skills_demand = {}
            
            for skill in skills:
                # Generate mock demand score (0-100)
                demand_score = np.random.randint(60, 95)
                
                # Categorize demand level
                if demand_score >= 85:
                    demand_level = "Very High"
                    trend = "Rapidly Growing"
                elif demand_score >= 75:
                    demand_level = "High"
                    trend = "Growing"
                elif demand_score >= 65:
                    demand_level = "Moderate"
                    trend = "Stable"
                else:
                    demand_level = "Low"
                    trend = "Declining"
                
                skills_demand[skill] = {
                    'demand_score': demand_score,
                    'demand_level': demand_level,
                    'trend': trend,
                    'market_value': demand_score * 1000,  # Mock market value
                    'growth_rate': np.random.uniform(5, 25)
                }
            
            return {
                'location': location,
                'skills_analysis': skills_demand,
                'overall_market_demand': np.mean([s['demand_score'] for s in skills_demand.values()]),
                'hot_skills': [skill for skill, data in skills_demand.items() if data['demand_score'] >= 80],
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing skills demand: {str(e)}")
            return {}
    
    def get_market_trends(self, industry: str = "Technology") -> Dict[str, Any]:
        """Get market trends for an industry."""
        try:
            # Mock market trends data
            trends = {
                'hiring_volume': {
                    'trend': 'Increasing',
                    'percentage_change': 15.5,
                    'forecast': 'Continued growth expected'
                },
                'salary_trends': {
                    'trend': 'Rising',
                    'percentage_change': 8.2,
                    'forecast': 'Moderate increases expected'
                },
                'skills_demand': {
                    'trend': 'Shifting',
                    'hot_skills': ['AI/ML', 'Cloud Computing', 'Cybersecurity'],
                    'declining_skills': ['Legacy Systems', 'Manual Testing']
                },
                'remote_work': {
                    'trend': 'Stable',
                    'percentage': 65,
                    'forecast': 'Hybrid models preferred'
                }
            }
            
            return {
                'industry': industry,
                'trends': trends,
                'analysis_date': datetime.now().isoformat(),
                'confidence_level': 'High'
            }
            
        except Exception as e:
            logger.error(f"Error getting market trends: {str(e)}")
            return {}
    
    def get_competitive_intelligence(self, company_name: str) -> Dict[str, Any]:
        """Get competitive intelligence for a company."""
        try:
            # Mock competitive data
            competitor_data = {
                'Glassdoor_rating': np.random.uniform(3.5, 4.5),
                'employee_count': np.random.randint(1000, 50000),
                'hiring_rate': np.random.uniform(5, 20),
                'salary_competitiveness': np.random.uniform(0.8, 1.2),
                'benefits_rating': np.random.uniform(3.0, 4.5),
                'work_life_balance': np.random.uniform(3.0, 4.5)
            }
            
            return {
                'company_name': company_name,
                'competitive_metrics': competitor_data,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting competitive intelligence: {str(e)}")
            return {}
    
    def generate_market_report(self, position: str, location: str, experience_years: int) -> Dict[str, Any]:
        """Generate comprehensive market report."""
        try:
            # Gather all market intelligence
            salary_benchmark = self.get_salary_benchmark(position, location, experience_years)
            skills_analysis = self.get_skills_demand_analysis(['Python', 'JavaScript', 'SQL'], location)
            market_trends = self.get_market_trends()
            
            # Generate insights
            insights = self._generate_market_insights(salary_benchmark, skills_analysis, market_trends)
            
            # Generate recommendations
            recommendations = self._generate_market_recommendations(salary_benchmark, skills_analysis, market_trends)
            
            return {
                'position': position,
                'location': location,
                'experience_years': experience_years,
                'salary_benchmark': salary_benchmark,
                'skills_analysis': skills_analysis,
                'market_trends': market_trends,
                'insights': insights,
                'recommendations': recommendations,
                'report_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating market report: {str(e)}")
            return {}
    
    def _generate_market_insights(self, salary_data: Dict, skills_data: Dict, trends_data: Dict) -> List[str]:
        """Generate market insights from data."""
        insights = []
        
        if salary_data:
            insights.append(f"Salary benchmark: ${salary_data.get('benchmark_salary', 0):,} for this position")
        
        if skills_data:
            hot_skills = skills_data.get('hot_skills', [])
            if hot_skills:
                insights.append(f"High-demand skills: {', '.join(hot_skills)}")
        
        if trends_data:
            hiring_trend = trends_data.get('trends', {}).get('hiring_volume', {}).get('trend', '')
            if hiring_trend == 'Increasing':
                insights.append("Hiring volume is increasing in this market")
        
        return insights
    
    def _generate_market_recommendations(self, salary_data: Dict, skills_data: Dict, trends_data: Dict) -> List[str]:
        """Generate market recommendations."""
        recommendations = []
        
        if salary_data:
            recommendations.append("Consider offering competitive salary within market range")
        
        if skills_data:
            recommendations.append("Focus on high-demand skills in job requirements")
        
        if trends_data:
            recommendations.append("Monitor market trends for strategic hiring decisions")
        
        return recommendations
