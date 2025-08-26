"""
Machine Learning Predictor Module for IKF HR Platform
Advanced AI-powered predictions for hiring success, resume quality, and salary analysis.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
import joblib
import pickle
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLPredictor:
    """
    Advanced Machine Learning predictor for HR decisions.
    Provides hiring success prediction, resume quality scoring, and salary analysis.
    """
    
    def __init__(self):
        """Initialize the ML predictor with models and encoders."""
        self.hiring_success_model = None
        self.resume_quality_model = None
        self.salary_predictor = None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        # Feature importance tracking
        self.feature_importance = {}
        
        # Model performance metrics
        self.model_performance = {}
        
        logger.info("ML Predictor initialized successfully")
    
    def extract_resume_features(self, resume_text: str, candidate_data: Dict) -> Dict[str, Any]:
        """
        Extract comprehensive features from resume and candidate data.
        
        Args:
            resume_text (str): Resume text content
            candidate_data (Dict): Additional candidate information
            
        Returns:
            Dict[str, Any]: Extracted features for ML models
        """
        features = {}
        
        # Text-based features
        features['text_length'] = len(resume_text)
        features['word_count'] = len(resume_text.split())
        features['sentence_count'] = len(re.split(r'[.!?]+', resume_text))
        
        # Skills and keywords
        technical_skills = self._extract_technical_skills(resume_text)
        features['technical_skill_count'] = len(technical_skills)
        features['unique_skills'] = len(set(technical_skills))
        
        # Experience features
        experience_years = candidate_data.get('experience_years', 0)
        features['experience_years'] = experience_years
        features['experience_level'] = self._categorize_experience(experience_years)
        
        # Education features
        education_level = candidate_data.get('education_level', 'bachelor')
        features['education_score'] = self._score_education(education_level)
        
        # Professional features
        features['certification_count'] = candidate_data.get('certification_count', 0)
        features['project_count'] = candidate_data.get('project_count', 0)
        features['publication_count'] = candidate_data.get('publication_count', 0)
        
        # Formatting features
        features['has_contact_info'] = self._has_contact_info(resume_text)
        features['has_summary'] = self._has_summary_section(resume_text)
        features['has_achievements'] = self._has_achievements_section(resume_text)
        
        # Industry-specific features
        features['industry_alignment'] = self._calculate_industry_alignment(
            resume_text, candidate_data.get('target_industry', '')
        )
        
        return features
    
    def _extract_technical_skills(self, text: str) -> List[str]:
        """Extract technical skills from resume text."""
        technical_keywords = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust', 'php', 'swift'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sql server'],
            'frameworks': ['django', 'flask', 'react', 'angular', 'vue', 'spring', 'express', 'laravel', 'asp.net'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'gitlab'],
            'ml_ai': ['tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'trello', 'asana', 'figma', 'sketch']
        }
        
        found_skills = []
        text_lower = text.lower()
        
        for category, skills in technical_keywords.items():
            for skill in skills:
                if skill in text_lower:
                    found_skills.append(skill)
        
        return found_skills
    
    def _categorize_experience(self, years: int) -> str:
        """Categorize experience level."""
        if years < 2:
            return 'junior'
        elif years < 5:
            return 'mid'
        elif years < 10:
            return 'senior'
        else:
            return 'expert'
    
    def _score_education(self, level: str) -> int:
        """Score education level numerically."""
        education_scores = {
            'high_school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'phd': 5,
            'certification': 2
        }
        return education_scores.get(level.lower(), 3)
    
    def _has_contact_info(self, text: str) -> int:
        """Check if resume has contact information."""
        contact_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\(\d{3}\) \d{3}-\d{4}',  # Phone (US format)
            r'\d{3}-\d{3}-\d{4}',  # Phone (US format)
            r'linkedin\.com',  # LinkedIn
            r'github\.com'  # GitHub
        ]
        
        for pattern in contact_patterns:
            if re.search(pattern, text):
                return 1
        return 0
    
    def _has_summary_section(self, text: str) -> int:
        """Check if resume has summary/objective section."""
        summary_keywords = ['summary', 'objective', 'profile', 'overview']
        text_lower = text.lower()
        
        for keyword in summary_keywords:
            if keyword in text_lower:
                return 1
        return 0
    
    def _has_achievements_section(self, text: str) -> int:
        """Check if resume has achievements section."""
        achievement_keywords = ['achievements', 'accomplishments', 'awards', 'recognition']
        text_lower = text.lower()
        
        for keyword in achievement_keywords:
            if keyword in text_lower:
                return 1
        return 0
    
    def _calculate_industry_alignment(self, resume_text: str, target_industry: str) -> float:
        """Calculate industry alignment score."""
        if not target_industry:
            return 0.5
        
        # Industry-specific keywords (can be expanded)
        industry_keywords = {
            'technology': ['software', 'development', 'programming', 'coding', 'algorithm', 'database'],
            'healthcare': ['medical', 'patient', 'clinical', 'healthcare', 'pharmaceutical', 'biotech'],
            'finance': ['financial', 'banking', 'investment', 'trading', 'risk', 'compliance'],
            'marketing': ['marketing', 'advertising', 'brand', 'campaign', 'social media', 'seo'],
            'sales': ['sales', 'revenue', 'customer', 'account', 'business development', 'partnership']
        }
        
        if target_industry.lower() not in industry_keywords:
            return 0.5
        
        keywords = industry_keywords[target_industry.lower()]
        text_lower = resume_text.lower()
        
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        return min(matches / len(keywords), 1.0)
    
    def predict_hiring_success(self, candidate_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict hiring success probability and retention likelihood.
        
        Args:
            candidate_features (Dict[str, Any]): Extracted candidate features
            
        Returns:
            Dict[str, Any]: Prediction results with confidence scores
        """
        try:
            if not self.hiring_success_model:
                # Load pre-trained model or use default predictions
                return self._default_hiring_prediction(candidate_features)
            
            # Prepare features for prediction
            feature_vector = self._prepare_feature_vector(candidate_features)
            
            # Make prediction
            success_probability = self.hiring_success_model.predict_proba([feature_vector])[0]
            
            # Calculate retention likelihood based on features
            retention_score = self._calculate_retention_score(candidate_features)
            
            return {
                'success_probability': float(success_probability[1]),
                'retention_likelihood': retention_score,
                'confidence_score': self._calculate_confidence_score(candidate_features),
                'risk_factors': self._identify_risk_factors(candidate_features),
                'recommendations': self._generate_hiring_recommendations(candidate_features),
                'prediction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in hiring success prediction: {str(e)}")
            return self._default_hiring_prediction(candidate_features)
    
    def score_resume_quality(self, resume_text: str, candidate_data: Dict) -> Dict[str, Any]:
        """
        Score resume quality and professional presentation.
        
        Args:
            resume_text (str): Resume text content
            candidate_data (Dict): Additional candidate information
            
        Returns:
            Dict[str, Any]: Quality score and improvement suggestions
        """
        try:
            # Extract features
            features = self.extract_resume_features(resume_text, candidate_data)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(features)
            
            # Generate improvement suggestions
            suggestions = self._generate_quality_suggestions(features, resume_text)
            
            return {
                'overall_score': quality_score,
                'content_score': self._calculate_content_score(features),
                'format_score': self._calculate_format_score(features),
                'professional_score': self._calculate_professional_score(features),
                'suggestions': suggestions,
                'strengths': self._identify_resume_strengths(features),
                'areas_for_improvement': self._identify_improvement_areas(features),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in resume quality scoring: {str(e)}")
            return {
                'overall_score': 0.5,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def predict_salary_range(self, candidate_features: Dict[str, Any], 
                           job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict salary range based on candidate profile and job requirements.
        
        Args:
            candidate_features (Dict[str, Any]): Candidate features
            job_requirements (Dict[str, Any]): Job requirements and market data
            
        Returns:
            Dict[str, Any]: Salary prediction with market analysis
        """
        try:
            # Calculate base salary
            base_salary = self._calculate_base_salary(candidate_features)
            
            # Apply market adjustments
            market_adjustment = self._calculate_market_adjustment(job_requirements)
            
            # Calculate experience multiplier
            experience_multiplier = self._calculate_experience_multiplier(
                candidate_features.get('experience_years', 0)
            )
            
            # Calculate skills premium
            skills_premium = self._calculate_skills_premium(candidate_features)
            
            # Final salary calculation
            predicted_salary = base_salary * market_adjustment * experience_multiplier + skills_premium
            
            # Calculate salary range
            salary_range = self._calculate_salary_range(predicted_salary)
            
            return {
                'predicted_salary': round(predicted_salary, 2),
                'salary_range': salary_range,
                'market_percentile': self._calculate_market_percentile(predicted_salary, job_requirements),
                'factors': {
                    'base_salary': base_salary,
                    'market_adjustment': market_adjustment,
                    'experience_multiplier': experience_multiplier,
                    'skills_premium': skills_premium
                },
                'market_analysis': self._generate_market_analysis(job_requirements),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in salary prediction: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_quality_score(self, features: Dict[str, Any]) -> float:
        """Calculate overall resume quality score."""
        scores = []
        
        # Content quality (40% weight)
        content_score = self._calculate_content_score(features)
        scores.append(content_score * 0.4)
        
        # Format quality (30% weight)
        format_score = self._calculate_format_score(features)
        scores.append(format_score * 0.3)
        
        # Professional quality (30% weight)
        professional_score = self._calculate_professional_score(features)
        scores.append(professional_score * 0.3)
        
        return sum(scores)
    
    def _calculate_content_score(self, features: Dict[str, Any]) -> float:
        """Calculate content quality score."""
        score = 0.0
        
        # Skills and experience
        if features.get('technical_skill_count', 0) > 0:
            score += 0.3
        if features.get('experience_years', 0) > 0:
            score += 0.2
        
        # Education
        education_score = features.get('education_score', 3)
        score += min(education_score / 5.0, 0.2)
        
        # Professional elements
        if features.get('has_summary', 0):
            score += 0.1
        if features.get('has_achievements', 0):
            score += 0.1
        if features.get('certification_count', 0) > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_format_score(self, features: Dict[str, Any]) -> float:
        """Calculate format quality score."""
        score = 0.0
        
        # Contact information
        if features.get('has_contact_info', 0):
            score += 0.3
        
        # Text structure
        text_length = features.get('text_length', 0)
        if 1000 <= text_length <= 5000:  # Optimal length
            score += 0.3
        elif 500 <= text_length <= 8000:  # Acceptable length
            score += 0.2
        
        # Professional presentation
        if features.get('has_summary', 0):
            score += 0.2
        if features.get('has_achievements', 0):
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_professional_score(self, features: Dict[str, Any]) -> float:
        """Calculate professional quality score."""
        score = 0.0
        
        # Experience level
        experience_years = features.get('experience_years', 0)
        if experience_years >= 5:
            score += 0.3
        elif experience_years >= 2:
            score += 0.2
        elif experience_years >= 1:
            score += 0.1
        
        # Skills diversity
        unique_skills = features.get('unique_skills', 0)
        if unique_skills >= 10:
            score += 0.3
        elif unique_skills >= 5:
            score += 0.2
        elif unique_skills >= 3:
            score += 0.1
        
        # Certifications and projects
        if features.get('certification_count', 0) > 0:
            score += 0.2
        if features.get('project_count', 0) > 0:
            score += 0.2
        
        return min(score, 1.0)
    
    def _generate_quality_suggestions(self, features: Dict[str, Any], resume_text: str) -> List[str]:
        """Generate improvement suggestions for resume."""
        suggestions = []
        
        # Content suggestions
        if features.get('technical_skill_count', 0) < 5:
            suggestions.append("Add more technical skills and technologies")
        
        if features.get('has_summary', 0) == 0:
            suggestions.append("Include a professional summary or objective section")
        
        if features.get('has_achievements', 0) == 0:
            suggestions.append("Add quantifiable achievements and results")
        
        # Format suggestions
        if features.get('has_contact_info', 0) == 0:
            suggestions.append("Ensure contact information is clearly visible")
        
        text_length = features.get('text_length', 0)
        if text_length < 1000:
            suggestions.append("Expand resume content with more details")
        elif text_length > 5000:
            suggestions.append("Condense resume to focus on most relevant information")
        
        # Professional suggestions
        if features.get('certification_count', 0) == 0:
            suggestions.append("Consider adding relevant certifications")
        
        if features.get('project_count', 0) == 0:
            suggestions.append("Include notable projects and their outcomes")
        
        return suggestions
    
    def _identify_resume_strengths(self, features: Dict[str, Any]) -> List[str]:
        """Identify resume strengths."""
        strengths = []
        
        if features.get('technical_skill_count', 0) >= 8:
            strengths.append("Strong technical skill set")
        
        if features.get('experience_years', 0) >= 5:
            strengths.append("Significant professional experience")
        
        if features.get('education_score', 3) >= 4:
            strengths.append("Advanced educational background")
        
        if features.get('certification_count', 0) > 0:
            strengths.append("Professional certifications")
        
        if features.get('project_count', 0) > 0:
            strengths.append("Project portfolio")
        
        return strengths
    
    def _identify_improvement_areas(self, features: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement."""
        areas = []
        
        if features.get('technical_skill_count', 0) < 5:
            areas.append("Technical skills")
        
        if features.get('has_summary', 0) == 0:
            areas.append("Professional summary")
        
        if features.get('has_achievements', 0) == 0:
            areas.append("Quantifiable achievements")
        
        if features.get('certification_count', 0) == 0:
            areas.append("Professional certifications")
        
        return areas
    
    def _default_hiring_prediction(self, candidate_features: Dict[str, Any]) -> Dict[str, Any]:
        """Provide default prediction when model is not available."""
        experience_years = candidate_features.get('experience_years', 0)
        education_score = candidate_features.get('education_score', 3)
        
        # Simple heuristic-based prediction
        base_probability = 0.5
        if experience_years >= 3:
            base_probability += 0.2
        if education_score >= 4:
            base_probability += 0.1
        if candidate_features.get('technical_skill_count', 0) >= 5:
            base_probability += 0.2
        
        return {
            'success_probability': min(base_probability, 0.9),
            'retention_likelihood': 0.7,
            'confidence_score': 0.6,
            'risk_factors': ['Limited model training data'],
            'recommendations': ['Consider additional evaluation methods'],
            'prediction_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_retention_score(self, features: Dict[str, Any]) -> float:
        """Calculate retention likelihood score."""
        score = 0.5  # Base score
        
        # Experience factors
        experience_years = features.get('experience_years', 0)
        if 2 <= experience_years <= 8:
            score += 0.2  # Optimal experience range
        elif experience_years > 8:
            score += 0.1  # Very experienced
        
        # Education factors
        education_score = features.get('education_score', 3)
        if education_score >= 4:
            score += 0.1
        
        # Skills factors
        if features.get('technical_skill_count', 0) >= 8:
            score += 0.1
        
        # Professional factors
        if features.get('certification_count', 0) > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_confidence_score(self, features: Dict[str, Any]) -> float:
        """Calculate prediction confidence score."""
        confidence = 0.5  # Base confidence
        
        # Feature completeness
        required_features = ['experience_years', 'education_score', 'technical_skill_count']
        available_features = sum(1 for f in required_features if f in features)
        confidence += (available_features / len(required_features)) * 0.3
        
        # Data quality
        if features.get('text_length', 0) > 1000:
            confidence += 0.1
        
        if features.get('has_contact_info', 0):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _identify_risk_factors(self, features: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors."""
        risks = []
        
        if features.get('experience_years', 0) < 1:
            risks.append("Limited professional experience")
        
        if features.get('technical_skill_count', 0) < 3:
            risks.append("Limited technical skills")
        
        if features.get('education_score', 3) < 3:
            risks.append("Basic education level")
        
        if features.get('has_contact_info', 0) == 0:
            risks.append("Missing contact information")
        
        return risks
    
    def _generate_hiring_recommendations(self, features: Dict[str, Any]) -> List[str]:
        """Generate hiring recommendations."""
        recommendations = []
        
        if features.get('success_probability', 0) >= 0.8:
            recommendations.append("Strong candidate - recommend for interview")
        elif features.get('success_probability', 0) >= 0.6:
            recommendations.append("Good candidate - consider for interview")
        else:
            recommendations.append("Consider additional screening or training")
        
        if features.get('experience_years', 0) < 2:
            recommendations.append("May benefit from mentorship program")
        
        if features.get('technical_skill_count', 0) < 5:
            recommendations.append("Consider skill development plan")
        
        return recommendations
    
    def _prepare_feature_vector(self, features: Dict[str, Any]) -> List[float]:
        """Prepare feature vector for ML model prediction."""
        # This would be implemented based on the specific model requirements
        # For now, return a simple feature vector
        return [
            features.get('experience_years', 0),
            features.get('education_score', 3),
            features.get('technical_skill_count', 0),
            features.get('certification_count', 0),
            features.get('project_count', 0)
        ]
    
    def _calculate_base_salary(self, features: Dict[str, Any]) -> float:
        """Calculate base salary based on candidate features."""
        base_salary = 50000  # Base salary
        
        # Experience adjustment
        experience_years = features.get('experience_years', 0)
        if experience_years > 0:
            base_salary += experience_years * 5000
        
        # Education adjustment
        education_score = features.get('education_score', 3)
        if education_score >= 4:
            base_salary += 10000
        elif education_score >= 5:
            base_salary += 20000
        
        return base_salary
    
    def _calculate_market_adjustment(self, job_requirements: Dict[str, Any]) -> float:
        """Calculate market adjustment factor."""
        # Default market adjustment
        return 1.0
    
    def _calculate_experience_multiplier(self, experience_years: int) -> float:
        """Calculate experience multiplier."""
        if experience_years < 2:
            return 0.8
        elif experience_years < 5:
            return 1.0
        elif experience_years < 10:
            return 1.2
        else:
            return 1.3
    
    def _calculate_skills_premium(self, features: Dict[str, Any]) -> float:
        """Calculate skills premium."""
        skill_count = features.get('technical_skill_count', 0)
        return skill_count * 1000  # $1000 per skill
    
    def _calculate_salary_range(self, predicted_salary: float) -> Dict[str, float]:
        """Calculate salary range."""
        range_width = predicted_salary * 0.15  # 15% range
        
        return {
            'min': round(predicted_salary - range_width, 2),
            'max': round(predicted_salary + range_width, 2)
        }
    
    def _calculate_market_percentile(self, salary: float, job_requirements: Dict[str, Any]) -> str:
        """Calculate market percentile."""
        # Simplified percentile calculation
        if salary > 100000:
            return "90th percentile"
        elif salary > 80000:
            return "75th percentile"
        elif salary > 60000:
            return "50th percentile"
        else:
            return "25th percentile"
    
    def _generate_market_analysis(self, job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate market analysis."""
        return {
            'market_trend': "Growing",
            'demand_level': "High",
            'competition_level': "Medium",
            'salary_trend': "Increasing"
        }
    
    def save_models(self, filepath: str):
        """Save trained models to file."""
        try:
            models = {
                'hiring_success_model': self.hiring_success_model,
                'resume_quality_model': self.resume_quality_model,
                'salary_predictor': self.salary_predictor,
                'tfidf_vectorizer': self.tfidf_vectorizer,
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'feature_importance': self.feature_importance,
                'model_performance': self.model_performance
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(models, f)
            
            logger.info(f"Models saved successfully to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
    
    def load_models(self, filepath: str):
        """Load trained models from file."""
        try:
            with open(filepath, 'rb') as f:
                models = pickle.load(f)
            
            self.hiring_success_model = models.get('hiring_success_model')
            self.resume_quality_model = models.get('resume_quality_model')
            self.salary_predictor = models.get('salary_predictor')
            self.tfidf_vectorizer = models.get('tfidf_vectorizer')
            self.scaler = models.get('scaler')
            self.label_encoders = models.get('label_encoders', {})
            self.feature_importance = models.get('feature_importance', {})
            self.model_performance = models.get('model_performance', {})
            
            logger.info(f"Models loaded successfully from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
