"""
Similarity calculation module for resume-job description comparison.
Implements TF-IDF and BERT-based similarity calculations.
"""

import logging
import numpy as np
from typing import Dict, Tuple, Optional, Union, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import torch
import torch.nn.functional as F

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimilarityCalculator:
    """
    A class for calculating similarity between resume and job description texts
    using different methods: TF-IDF and BERT.
    """
    
    def __init__(self, use_gpu: bool = False):
        """
        Initialize the SimilarityCalculator.
        
        Args:
            use_gpu (bool): Whether to use GPU for BERT calculations
        """
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.device = torch.device('cuda' if self.use_gpu else 'cpu')
        
        # Initialize TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        
        # BERT model and tokenizer will be loaded on first use
        self.bert_model = None
        self.bert_tokenizer = None
        
        logger.info(f"SimilarityCalculator initialized on device: {self.device}")
    
    def calculate_tfidf_similarity(self, job_desc: str, resume: str) -> Dict[str, any]:
        """
        Calculate similarity using TF-IDF vectorization.
        
        Args:
            job_desc (str): Job description text
            resume (str): Resume text
            
        Returns:
            Dict[str, any]: TF-IDF similarity results
        """
        try:
            # Preprocess texts
            processed_job_desc = self._preprocess_for_tfidf(job_desc)
            processed_resume = self._preprocess_for_tfidf(resume)
            
            if not processed_job_desc or not processed_resume:
                return {
                    'method': 'TF-IDF',
                    'similarity_score': 0.0,
                    'confidence': 'low',
                    'error': 'Insufficient text for analysis'
                }
            
            # Create TF-IDF vectors
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([processed_job_desc, processed_resume])
            
            # Calculate cosine similarity
            similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Convert to percentage
            similarity_percentage = similarity_score * 100
            
            # Get feature names and their importance
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            job_desc_tfidf = tfidf_matrix[0].toarray()[0]
            resume_tfidf = tfidf_matrix[1].toarray()[0]
            
            # Find important features
            important_features = self._get_important_features(
                feature_names, job_desc_tfidf, resume_tfidf
            )
            
            # Determine confidence level
            confidence = self._get_confidence_level(similarity_percentage)
            
            return {
                'method': 'TF-IDF',
                'similarity_score': round(similarity_percentage, 2),
                'raw_score': similarity_score,
                'confidence': confidence,
                'important_features': important_features,
                'feature_count': len(feature_names),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error in TF-IDF calculation: {str(e)}")
            return {
                'method': 'TF-IDF',
                'similarity_score': 0.0,
                'confidence': 'low',
                'error': f'Calculation error: {str(e)}'
            }
    
    def calculate_bert_similarity(self, job_desc: str, resume: str) -> Dict[str, any]:
        """
        Calculate similarity using BERT embeddings.
        
        Args:
            job_desc (str): Job description text
            resume (str): Resume text
            
        Returns:
            Dict[str, any]: BERT similarity results
        """
        try:
            # Load BERT model if not already loaded
            if self.bert_model is None:
                self._load_bert_model()
            
            # Preprocess texts
            processed_job_desc = self._preprocess_for_bert(job_desc)
            processed_resume = self._preprocess_for_bert(resume)
            
            if not processed_job_desc or not processed_resume:
                return {
                    'method': 'BERT',
                    'similarity_score': 0.0,
                    'confidence': 'low',
                    'error': 'Insufficient text for analysis'
                }
            
            # Get BERT embeddings
            job_desc_embeddings = self._get_bert_embeddings(processed_job_desc)
            resume_embeddings = self._get_bert_embeddings(processed_resume)
            
            # Calculate cosine similarity
            similarity_score = F.cosine_similarity(
                job_desc_embeddings.unsqueeze(0), 
                resume_embeddings.unsqueeze(0)
            ).item()
            
            # Convert to percentage
            similarity_percentage = similarity_score * 100
            
            # Determine confidence level
            confidence = self._get_confidence_level(similarity_percentage)
            
            return {
                'method': 'BERT',
                'similarity_score': round(similarity_percentage, 2),
                'raw_score': similarity_score,
                'confidence': confidence,
                'embedding_dimension': job_desc_embeddings.shape[0],
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error in BERT calculation: {str(e)}")
            return {
                'method': 'BERT',
                'similarity_score': 0.0,
                'confidence': 'low',
                'error': f'Calculation error: {str(e)}'
            }
    
    def calculate_combined_similarity(self, job_desc: str, resume: str) -> Dict[str, any]:
        """
        Calculate similarity using both methods and combine results.
        
        Args:
            job_desc (str): Job description text
            resume (str): Resume text
            
        Returns:
            Dict[str, any]: Combined similarity results
        """
        # Calculate both similarities
        tfidf_results = self.calculate_tfidf_similarity(job_desc, resume)
        bert_results = self.calculate_bert_similarity(job_desc, resume)
        
        # Calculate weighted average (TF-IDF: 40%, BERT: 60%)
        tfidf_weight = 0.4
        bert_weight = 0.6
        
        combined_score = (
            tfidf_results['similarity_score'] * tfidf_weight +
            bert_results['similarity_score'] * bert_weight
        )
        
        # Determine overall confidence
        overall_confidence = self._get_combined_confidence(
            tfidf_results['confidence'], 
            bert_results['confidence']
        )
        
        return {
            'method': 'Combined (TF-IDF + BERT)',
            'similarity_score': round(combined_score, 2),
            'tfidf_score': tfidf_results['similarity_score'],
            'bert_score': bert_results['similarity_score'],
            'confidence': overall_confidence,
            'tfidf_results': tfidf_results,
            'bert_results': bert_results,
            'weights': {'tfidf': tfidf_weight, 'bert': bert_weight}
        }
    
    def _preprocess_for_tfidf(self, text: str) -> str:
        """Preprocess text for TF-IDF analysis."""
        if not text:
            return ""
        
        # Basic cleaning for TF-IDF
        text = text.lower().strip()
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def _preprocess_for_bert(self, text: str) -> str:
        """Preprocess text for BERT analysis."""
        if not text:
            return ""
        
        # BERT can handle more complex text, so minimal preprocessing
        text = text.strip()
        # Limit length to avoid memory issues
        if len(text) > 2000:
            text = text[:2000]
        return text
    
    def _load_bert_model(self):
        """Load BERT model and tokenizer."""
        try:
            from transformers import BertTokenizer, BertModel
            
            logger.info("Loading BERT model...")
            self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            self.bert_model = BertModel.from_pretrained('bert-base-uncased')
            
            # Move to device
            self.bert_model.to(self.device)
            self.bert_model.eval()
            
            logger.info("BERT model loaded successfully")
            
        except ImportError:
            logger.error("Transformers library not found. Please install it:")
            logger.error("pip install transformers torch")
            raise
        except Exception as e:
            logger.error(f"Error loading BERT model: {str(e)}")
            raise
    
    def _get_bert_embeddings(self, text: str) -> torch.Tensor:
        """Get BERT embeddings for the given text."""
        # Tokenize and encode
        inputs = self.bert_tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            padding=True, 
            max_length=512
        )
        
        # Move inputs to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get embeddings
        with torch.no_grad():
            outputs = self.bert_model(**inputs)
        
        # Use mean pooling of last hidden state
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
        
        return embeddings
    
    def _get_important_features(self, feature_names: np.ndarray, 
                               job_desc_tfidf: np.ndarray, 
                               resume_tfidf: np.ndarray) -> Dict[str, any]:
        """Get important features from TF-IDF analysis."""
        # Find features that appear in both texts
        common_features = []
        job_desc_features = []
        resume_features = []
        
        for i, feature in enumerate(feature_names):
            job_score = job_desc_tfidf[i]
            resume_score = resume_tfidf[i]
            
            if job_score > 0 and resume_score > 0:
                common_features.append({
                    'feature': feature,
                    'job_desc_score': round(job_score, 4),
                    'resume_score': round(resume_score, 4),
                    'average_score': round((job_score + resume_score) / 2, 4)
                })
            elif job_score > 0:
                job_desc_features.append({
                    'feature': feature,
                    'score': round(job_score, 4)
                })
            elif resume_score > 0:
                resume_features.append({
                    'feature': feature,
                    'score': round(resume_score, 4)
                })
        
        # Sort by importance
        common_features.sort(key=lambda x: x['average_score'], reverse=True)
        job_desc_features.sort(key=lambda x: x['score'], reverse=True)
        resume_features.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'common_features': common_features[:20],  # Top 20 common features
            'job_desc_only': job_desc_features[:10],  # Top 10 job description features
            'resume_only': resume_features[:10]       # Top 10 resume features
        }
    
    def _get_confidence_level(self, score: float) -> str:
        """Determine confidence level based on similarity score."""
        if score >= 80:
            return 'very_high'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        elif score >= 20:
            return 'low'
        else:
            return 'very_low'
    
    def _get_combined_confidence(self, tfidf_confidence: str, bert_confidence: str) -> str:
        """Determine overall confidence from both methods."""
        confidence_levels = {
            'very_low': 1, 'low': 2, 'medium': 3, 'high': 4, 'very_high': 5
        }
        
        tfidf_level = confidence_levels.get(tfidf_confidence, 1)
        bert_level = confidence_levels.get(bert_confidence, 1)
        
        # Average confidence level
        avg_level = (tfidf_level + bert_level) / 2
        
        if avg_level >= 4.5:
            return 'very_high'
        elif avg_level >= 3.5:
            return 'high'
        elif avg_level >= 2.5:
            return 'medium'
        elif avg_level >= 1.5:
            return 'low'
        else:
            return 'very_low'
    
    def get_similarity_breakdown(self, job_desc: str, resume: str) -> Dict[str, any]:
        """
        Get a comprehensive breakdown of similarity analysis.
        
        Args:
            job_desc (str): Job description text
            resume (str): Resume text
            
        Returns:
            Dict[str, any]: Comprehensive similarity breakdown
        """
        # Calculate all similarity methods
        tfidf_results = self.calculate_tfidf_similarity(job_desc, resume)
        bert_results = self.calculate_bert_similarity(job_desc, resume)
        combined_results = self.calculate_combined_similarity(job_desc, resume)
        
        # Get text statistics
        job_desc_stats = self._get_text_statistics(job_desc)
        resume_stats = self._get_text_statistics(resume)
        
        return {
            'overall_score': combined_results['similarity_score'],
            'overall_confidence': combined_results['confidence'],
            'methods': {
                'tfidf': tfidf_results,
                'bert': bert_results,
                'combined': combined_results
            },
            'text_analysis': {
                'job_description': job_desc_stats,
                'resume': resume_stats
            },
            'recommendations': self._generate_recommendations(combined_results)
        }
    
    def _get_text_statistics(self, text: str) -> Dict[str, any]:
        """Get basic statistics about the text."""
        if not text:
            return {}
        
        words = text.split()
        sentences = text.split('.')
        
        return {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'character_count': len(text),
            'average_word_length': round(sum(len(word) for word in words) / len(words), 2) if words else 0
        }
    
    def _generate_recommendations(self, results: Dict[str, any]) -> List[str]:
        """Generate recommendations based on similarity results."""
        recommendations = []
        score = results['similarity_score']
        
        if score < 30:
            recommendations.extend([
                "Consider adding more relevant keywords from the job description",
                "Highlight specific skills and experiences mentioned in the job posting",
                "Review and update your resume to better match the job requirements"
            ])
        elif score < 50:
            recommendations.extend([
                "Add more specific examples of relevant experience",
                "Include industry-specific terminology",
                "Emphasize transferable skills that match the job description"
            ])
        elif score < 70:
            recommendations.extend([
                "Fine-tune your resume with more targeted keywords",
                "Add quantifiable achievements that relate to the job",
                "Consider reorganizing sections to highlight most relevant experience"
            ])
        else:
            recommendations.extend([
                "Your resume shows good alignment with the job description",
                "Consider adding any missing technical skills",
                "Highlight recent and relevant experience prominently"
            ])
        
        return recommendations
