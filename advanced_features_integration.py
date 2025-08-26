"""
Advanced Features Integration Module for IKF HR Platform
Integrates all new advanced features into a unified system.
"""

import logging
import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Import new advanced modules
from ml_predictor import MLPredictor
from analytics_dashboard import HRAnalyticsDashboard
from workflow_manager import WorkflowManager, WorkflowInstance, WorkflowStage
from market_intelligence import MarketIntelligence

# Import existing modules
from text_processor import TextProcessor
from similarity_calculator import SimilarityCalculator
from file_handler import FileHandler

logger = logging.getLogger(__name__)

class AdvancedFeaturesIntegration:
    """
    Integration layer for all advanced features.
    Provides unified interface for ML predictions, analytics, workflows, and market intelligence.
    """
    
    def __init__(self):
        """Initialize the advanced features integration."""
        # Initialize all advanced modules
        self.ml_predictor = MLPredictor()
        self.analytics_dashboard = HRAnalyticsDashboard()
        self.workflow_manager = WorkflowManager()
        self.market_intelligence = MarketIntelligence()
        
        # Initialize existing modules
        self.text_processor = TextProcessor()
        self.similarity_calculator = SimilarityCalculator()
        self.file_handler = FileHandler()
        
        logger.info("Advanced Features Integration initialized successfully")
    
    def comprehensive_candidate_evaluation(self, resume_file, job_description: str, 
                                       candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive candidate evaluation using all advanced features.
        
        Args:
            resume_file: Uploaded resume file
            job_description (str): Job description text
            candidate_data (Dict[str, Any]): Additional candidate information
            
        Returns:
            Dict[str, Any]: Comprehensive evaluation results
        """
        try:
            # Extract text from resume
            resume_text = self._extract_resume_text(resume_file)
            if not resume_text:
                return {'error': 'Could not extract text from resume'}
            
            # Basic similarity analysis
            similarity_results = self.similarity_calculator.calculate_combined_similarity(
                job_description, resume_text
            )
            
            # ML-powered predictions
            ml_features = self.ml_predictor.extract_resume_features(resume_text, candidate_data)
            hiring_prediction = self.ml_predictor.predict_hiring_success(ml_features)
            resume_quality = self.ml_predictor.score_resume_quality(resume_text, candidate_data)
            salary_prediction = self.ml_predictor.predict_salary_range(
                ml_features, {'job_description': job_description}
            )
            
            # Market intelligence
            market_report = self.market_intelligence.generate_market_report(
                candidate_data.get('position', 'Software Engineer'),
                candidate_data.get('location', 'Remote'),
                candidate_data.get('experience_years', 3)
            )
            
            # Create comprehensive evaluation
            evaluation = {
                'candidate_id': candidate_data.get('candidate_id', 'unknown'),
                'position': candidate_data.get('position', 'unknown'),
                'evaluation_date': datetime.now().isoformat(),
                
                # Basic similarity analysis
                'similarity_analysis': similarity_results,
                
                # ML predictions
                'hiring_prediction': hiring_prediction,
                'resume_quality': resume_quality,
                'salary_prediction': salary_prediction,
                
                # Market intelligence
                'market_intelligence': market_report,
                
                # Overall assessment
                'overall_score': self._calculate_overall_score(
                    similarity_results, hiring_prediction, resume_quality
                ),
                'recommendations': self._generate_comprehensive_recommendations(
                    similarity_results, hiring_prediction, resume_quality, market_report
                ),
                'risk_assessment': self._assess_candidate_risks(
                    hiring_prediction, resume_quality
                )
            }
            
            # Add to analytics dashboard
            self._add_to_analytics(evaluation, candidate_data)
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error in comprehensive evaluation: {str(e)}")
            return {'error': str(e)}
    
    def create_evaluation_workflow(self, candidate_data: Dict[str, Any], 
                                 evaluation_results: Dict[str, Any]) -> str:
        """
        Create an evaluation workflow for a candidate.
        
        Args:
            candidate_data (Dict[str, Any]): Candidate information
            evaluation_results (Dict[str, Any]): Initial evaluation results
            
        Returns:
            str: Workflow instance ID
        """
        try:
            # Determine workflow template based on position and evaluation results
            template_id = self._select_workflow_template(candidate_data, evaluation_results)
            
            # Create workflow instance
            workflow_instance_id = self.workflow_manager.instantiate_workflow(
                template_id, candidate_data
            )
            
            # Start the workflow
            self.workflow_manager.start_workflow(workflow_instance_id)
            
            logger.info(f"Created evaluation workflow: {workflow_instance_id}")
            return workflow_instance_id
            
        except Exception as e:
            logger.error(f"Error creating evaluation workflow: {str(e)}")
            return ""
    
    def get_advanced_analytics(self, date_range: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Get comprehensive analytics dashboard.
        
        Args:
            date_range (Optional[tuple]): Date range for analysis
            
        Returns:
            Dict[str, Any]: Comprehensive analytics data
        """
        try:
            # Get all analytics
            analytics = self.analytics_dashboard.get_comprehensive_dashboard(date_range)
            
            # Add workflow analytics
            workflow_analytics = self._get_workflow_analytics()
            analytics['workflow_analytics'] = workflow_analytics
            
            # Add market intelligence summary
            market_summary = self._get_market_intelligence_summary()
            analytics['market_intelligence_summary'] = market_summary
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting advanced analytics: {str(e)}")
            return {'error': str(e)}
    
    def generate_executive_report(self, date_range: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Generate executive-level report with key insights.
        
        Args:
            date_range (Optional[tuple]): Date range for analysis
            
        Returns:
            Dict[str, Any]: Executive report
        """
        try:
            # Get comprehensive analytics
            analytics = self.get_advanced_analytics(date_range)
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(analytics)
            
            # Generate strategic recommendations
            strategic_recommendations = self._generate_strategic_recommendations(analytics)
            
            # Generate market insights
            market_insights = self._generate_market_insights(analytics)
            
            report = {
                'report_date': datetime.now().isoformat(),
                'date_range': date_range,
                'executive_summary': executive_summary,
                'key_metrics': self._extract_key_metrics(analytics),
                'strategic_recommendations': strategic_recommendations,
                'market_insights': market_insights,
                'risk_assessment': self._assess_business_risks(analytics),
                'opportunity_analysis': self._analyze_business_opportunities(analytics)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating executive report: {str(e)}")
            return {'error': str(e)}
    
    def _extract_resume_text(self, resume_file) -> str:
        """Extract text from resume file."""
        try:
            if hasattr(resume_file, 'name'):
                file_path = resume_file.name
                success, text = self.file_handler.extract_text(file_path)
                if success:
                    return text
                else:
                    logger.error(f"Failed to extract text: {text}")
                    return ""
            else:
                logger.error("Invalid resume file")
                return ""
        except Exception as e:
            logger.error(f"Error extracting resume text: {str(e)}")
            return ""
    
    def _calculate_overall_score(self, similarity_results: Dict, hiring_prediction: Dict, 
                               resume_quality: Dict) -> float:
        """Calculate overall candidate score."""
        try:
            # Weighted scoring
            similarity_weight = 0.4
            hiring_weight = 0.35
            quality_weight = 0.25
            
            # Similarity score (0-100)
            similarity_score = similarity_results.get('combined_score', 0)
            
            # Hiring success probability (0-1)
            hiring_score = hiring_prediction.get('success_probability', 0.5) * 100
            
            # Resume quality score (0-1)
            quality_score = resume_quality.get('overall_score', 0.5) * 100
            
            # Calculate weighted average
            overall_score = (
                similarity_score * similarity_weight +
                hiring_score * hiring_weight +
                quality_score * quality_weight
            )
            
            return round(overall_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating overall score: {str(e)}")
            return 0.0
    
    def _generate_comprehensive_recommendations(self, similarity_results: Dict, 
                                             hiring_prediction: Dict, resume_quality: Dict,
                                             market_report: Dict) -> List[str]:
        """Generate comprehensive recommendations."""
        recommendations = []
        
        try:
            # Similarity-based recommendations
            similarity_score = similarity_results.get('combined_score', 0)
            if similarity_score < 60:
                recommendations.append("Candidate shows low alignment with job requirements")
            elif similarity_score < 80:
                recommendations.append("Candidate has moderate alignment - consider additional screening")
            else:
                recommendations.append("Candidate shows strong alignment with job requirements")
            
            # Hiring prediction recommendations
            success_prob = hiring_prediction.get('success_probability', 0.5)
            if success_prob < 0.6:
                recommendations.append("Low hiring success probability - consider alternative candidates")
            elif success_prob < 0.8:
                recommendations.append("Moderate hiring success probability - proceed with caution")
            else:
                recommendations.append("High hiring success probability - strong candidate")
            
            # Resume quality recommendations
            quality_score = resume_quality.get('overall_score', 0.5)
            if quality_score < 0.6:
                recommendations.append("Resume quality needs improvement - provide feedback to candidate")
            
            # Market-based recommendations
            if market_report:
                market_insights = market_report.get('insights', [])
                recommendations.extend(market_insights[:2])  # Top 2 market insights
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Error generating recommendations"]
    
    def _assess_candidate_risks(self, hiring_prediction: Dict, resume_quality: Dict) -> List[str]:
        """Assess candidate risks."""
        risks = []
        
        try:
            # Hiring success risks
            success_prob = hiring_prediction.get('success_probability', 0.5)
            if success_prob < 0.6:
                risks.append("Low hiring success probability")
            
            # Resume quality risks
            quality_score = resume_quality.get('overall_score', 0.5)
            if quality_score < 0.6:
                risks.append("Poor resume quality")
            
            # Retention risks
            retention_prob = hiring_prediction.get('retention_likelihood', 0.5)
            if retention_prob < 0.6:
                risks.append("Low retention likelihood")
            
            return risks
            
        except Exception as e:
            logger.error(f"Error assessing candidate risks: {str(e)}")
            return ["Error assessing risks"]
    
    def _select_workflow_template(self, candidate_data: Dict[str, Any], 
                                evaluation_results: Dict[str, Any]) -> str:
        """Select appropriate workflow template."""
        # This would implement logic to select workflow template based on:
        # - Position type
        # - Evaluation results
        # - Company requirements
        
        # For now, return a default template ID
        return "default_template"
    
    def _add_to_analytics(self, evaluation: Dict[str, Any], candidate_data: Dict[str, Any]):
        """Add evaluation data to analytics dashboard."""
        try:
            # Add recruitment record
            recruitment_record = {
                'candidate_id': candidate_data.get('candidate_id', 'unknown'),
                'position': candidate_data.get('position', 'unknown'),
                'source': candidate_data.get('source', 'direct'),
                'date_applied': datetime.now().isoformat(),
                'status': 'evaluated'
            }
            self.analytics_dashboard.add_recruitment_record(recruitment_record)
            
            # Add candidate data
            candidate_analytics = {
                'candidate_id': candidate_data.get('candidate_id', 'unknown'),
                'age': candidate_data.get('age', 30),
                'gender': candidate_data.get('gender', 'unknown'),
                'ethnicity': candidate_data.get('ethnicity', 'unknown'),
                'location': candidate_data.get('location', 'unknown')
            }
            self.analytics_dashboard.add_candidate_data(candidate_analytics)
            
        except Exception as e:
            logger.error(f"Error adding to analytics: {str(e)}")
    
    def _get_workflow_analytics(self) -> Dict[str, Any]:
        """Get workflow analytics."""
        try:
            # Get active workflows
            active_workflows = len(self.workflow_manager.active_workflows)
            
            # Calculate workflow metrics
            workflow_metrics = {
                'active_workflows': active_workflows,
                'completed_workflows': 0,  # Would calculate from completed workflows
                'average_completion_time': 0,  # Would calculate from historical data
                'workflow_efficiency': 0.85  # Mock efficiency score
            }
            
            return workflow_metrics
            
        except Exception as e:
            logger.error(f"Error getting workflow analytics: {str(e)}")
            return {}
    
    def _get_market_intelligence_summary(self) -> Dict[str, Any]:
        """Get market intelligence summary."""
        try:
            # Get market trends
            market_trends = self.market_intelligence.get_market_trends()
            
            # Get skills demand
            skills_demand = self.market_intelligence.get_skills_demand_analysis(
                ['Python', 'JavaScript', 'SQL', 'Machine Learning']
            )
            
            return {
                'market_trends': market_trends,
                'skills_demand': skills_demand,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting market intelligence summary: {str(e)}")
            return {}
    
    def _generate_executive_summary(self, analytics: Dict[str, Any]) -> str:
        """Generate executive summary."""
        try:
            # Extract key metrics
            total_applications = analytics.get('overall_kpis', {}).get('total_applications', 0)
            total_hires = analytics.get('overall_kpis', {}).get('total_hires', 0)
            conversion_rate = analytics.get('overall_kpis', {}).get('overall_conversion_rate', 0)
            
            summary = f"""
            **Executive Summary - HR Recruitment Performance**
            
            **Key Metrics:**
            - Total Applications: {total_applications}
            - Total Hires: {total_hires}
            - Overall Conversion Rate: {conversion_rate:.1f}%
            
            **Performance Overview:**
            The recruitment team has processed {total_applications} applications, 
            resulting in {total_hires} successful hires. The overall conversion rate 
            of {conversion_rate:.1f}% indicates {'strong' if conversion_rate > 15 else 'moderate'} 
            recruitment effectiveness.
            """
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            return "Error generating executive summary"
    
    def _generate_strategic_recommendations(self, analytics: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []
        
        try:
            # Analyze conversion rates
            conversion_rate = analytics.get('overall_kpis', {}).get('overall_conversion_rate', 0)
            if conversion_rate < 10:
                recommendations.append("Improve candidate screening process to increase conversion rates")
            
            # Analyze time-to-hire
            time_analytics = analytics.get('time_analytics', {})
            if time_analytics:
                recommendations.append("Optimize workflow processes to reduce time-to-hire")
            
            # Analyze diversity
            diversity_analytics = analytics.get('diversity_analytics', {})
            if diversity_analytics:
                recommendations.append("Implement diversity-focused recruitment strategies")
            
            # Market intelligence recommendations
            market_summary = analytics.get('market_intelligence_summary', {})
            if market_summary:
                recommendations.append("Leverage market intelligence for competitive hiring strategies")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating strategic recommendations: {str(e)}")
            return ["Error generating strategic recommendations"]
    
    def _generate_market_insights(self, analytics: Dict[str, Any]) -> List[str]:
        """Generate market insights."""
        insights = []
        
        try:
            market_summary = analytics.get('market_intelligence_summary', {})
            if market_summary:
                market_trends = market_summary.get('market_trends', {})
                skills_demand = market_summary.get('skills_demand', {})
                
                if market_trends:
                    insights.append("Market trends indicate growing demand for technical talent")
                
                if skills_demand:
                    hot_skills = skills_demand.get('hot_skills', [])
                    if hot_skills:
                        insights.append(f"High-demand skills: {', '.join(hot_skills[:3])}")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating market insights: {str(e)}")
            return ["Error generating market insights"]
    
    def _extract_key_metrics(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from analytics."""
        try:
            overall_kpis = analytics.get('overall_kpis', {})
            
            key_metrics = {
                'total_applications': overall_kpis.get('total_applications', 0),
                'total_hires': overall_kpis.get('total_hires', 0),
                'conversion_rate': overall_kpis.get('overall_conversion_rate', 0),
                'average_time_to_hire': overall_kpis.get('average_time_to_hire', 0),
                'cost_per_hire': overall_kpis.get('cost_per_hire', 0)
            }
            
            return key_metrics
            
        except Exception as e:
            logger.error(f"Error extracting key metrics: {str(e)}")
            return {}
    
    def _assess_business_risks(self, analytics: Dict[str, Any]) -> List[str]:
        """Assess business risks from analytics."""
        risks = []
        
        try:
            # Low conversion rate risk
            conversion_rate = analytics.get('overall_kpis', {}).get('overall_conversion_rate', 0)
            if conversion_rate < 10:
                risks.append("Low conversion rate may indicate poor candidate quality or screening issues")
            
            # High time-to-hire risk
            time_to_hire = analytics.get('overall_kpis', {}).get('average_time_to_hire', 0)
            if time_to_hire > 30:
                risks.append("Extended time-to-hire may result in losing top candidates to competitors")
            
            # High cost-per-hire risk
            cost_per_hire = analytics.get('overall_kpis', {}).get('cost_per_hire', 0)
            if cost_per_hire > 10000:
                risks.append("High cost-per-hire may impact recruitment budget and ROI")
            
            return risks
            
        except Exception as e:
            logger.error(f"Error assessing business risks: {str(e)}")
            return ["Error assessing business risks"]
    
    def _analyze_business_opportunities(self, analytics: Dict[str, Any]) -> List[str]:
        """Analyze business opportunities from analytics."""
        opportunities = []
        
        try:
            # High conversion rate opportunity
            conversion_rate = analytics.get('overall_kpis', {}).get('overall_conversion_rate', 0)
            if conversion_rate > 20:
                opportunities.append("High conversion rate suggests strong recruitment processes - consider scaling")
            
            # Market intelligence opportunities
            market_summary = analytics.get('market_intelligence_summary', {})
            if market_summary:
                opportunities.append("Leverage market intelligence for strategic talent acquisition")
            
            # Workflow optimization opportunities
            workflow_analytics = analytics.get('workflow_analytics', {})
            if workflow_analytics:
                opportunities.append("Optimize workflow processes to improve efficiency")
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error analyzing business opportunities: {str(e)}")
            return ["Error analyzing business opportunities"]
