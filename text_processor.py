"""
Text processing module for resume-job description comparison.
Handles text preprocessing, cleaning, and analysis using spaCy.
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
import spacy
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextProcessor:
    """
    A class for processing and analyzing text using spaCy.
    Handles text cleaning, preprocessing, and feature extraction.
    """
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the TextProcessor with a spaCy model.
        
        Args:
            model_name (str): Name of the spaCy model to use
        """
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.error(f"spaCy model '{model_name}' not found. Please install it using:")
            logger.error(f"python -m spacy download {model_name}")
            raise
        
        # Common resume sections to look for
        self.resume_sections = [
            'skills', 'experience', 'education', 'summary', 'objective',
            'work history', 'employment', 'qualifications', 'certifications',
            'projects', 'achievements', 'awards'
        ]
        
        # Technical skills keywords (can be expanded)
        self.technical_keywords = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch'],
            'frameworks': ['django', 'flask', 'react', 'angular', 'vue', 'spring', 'express'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'],
            'ml_ai': ['tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy']
        }
    
    def preprocess_text(self, text: str, remove_stopwords: bool = True) -> str:
        """
        Preprocess the input text by cleaning and normalizing it.
        
        Args:
            text (str): Input text to process
            remove_stopwords (bool): Whether to remove stopwords
            
        Returns:
            str: Preprocessed text
        """
        if not text or not text.strip():
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Process with spaCy
        doc = self.nlp(text)
        
        # Extract tokens based on criteria
        tokens = []
        for token in doc:
            # Skip if it's a stopword and we want to remove them
            if remove_stopwords and token.is_stop:
                continue
            
            # Skip punctuation
            if token.is_punct:
                continue
            
            # Skip whitespace
            if token.is_space:
                continue
            
            # Lemmatize the token
            lemma = token.lemma_.lower().strip()
            
            # Only add non-empty lemmas
            if lemma and len(lemma) > 1:
                tokens.append(lemma)
        
        return " ".join(tokens)
    
    def extract_keywords(self, text: str, top_n: int = 20) -> List[Tuple[str, int]]:
        """
        Extract the most common keywords from the text.
        
        Args:
            text (str): Input text
            top_n (int): Number of top keywords to return
            
        Returns:
            List[Tuple[str, int]]: List of (keyword, frequency) tuples
        """
        processed_text = self.preprocess_text(text, remove_stopwords=True)
        if not processed_text:
            return []
        
        # Split into words and count frequencies
        words = processed_text.split()
        word_counts = Counter(words)
        
        # Return top N most common words
        return word_counts.most_common(top_n)
    
    def extract_technical_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extract technical skills from the text based on predefined categories.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping skill categories to found skills
        """
        processed_text = self.preprocess_text(text, remove_stopwords=False)
        if not processed_text:
            return {}
        
        found_skills = {}
        
        for category, keywords in self.technical_keywords.items():
            found = []
            for keyword in keywords:
                if keyword.lower() in processed_text.lower():
                    found.append(keyword)
            if found:
                found_skills[category] = found
        
        return found_skills
    
    def identify_resume_sections(self, text: str) -> Dict[str, str]:
        """
        Identify different sections in a resume.
        
        Args:
            text (str): Resume text to analyze
            
        Returns:
            Dict[str, str]: Dictionary mapping section names to their content
        """
        sections = {}
        lines = text.split('\n')
        current_section = "general"
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a section header
            line_lower = line.lower()
            is_header = False
            
            for section in self.resume_sections:
                if section in line_lower:
                    # Save previous section content
                    if current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Start new section
                    current_section = section
                    current_content = []
                    is_header = True
                    break
            
            if not is_header:
                current_content.append(line)
        
        # Save the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def calculate_text_statistics(self, text: str) -> Dict[str, any]:
        """
        Calculate various statistics about the text.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, any]: Dictionary containing text statistics
        """
        if not text:
            return {}
        
        # Basic statistics
        stats = {
            'total_characters': len(text),
            'total_words': len(text.split()),
            'total_sentences': len([sent for sent in self.nlp(text).sents]),
            'unique_words': len(set(text.lower().split())),
            'average_word_length': 0,
            'readability_score': 0
        }
        
        # Calculate average word length
        words = text.split()
        if words:
            total_length = sum(len(word) for word in words)
            stats['average_word_length'] = round(total_length / len(words), 2)
        
        # Simple readability score (Flesch Reading Ease approximation)
        if stats['total_sentences'] > 0 and stats['total_words'] > 0:
            # Simplified Flesch score
            avg_sentence_length = stats['total_words'] / stats['total_sentences']
            stats['readability_score'] = max(0, min(100, 100 - avg_sentence_length * 2))
        
        return stats
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from the text using spaCy.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping entity types to lists of entities
        """
        doc = self.nlp(text)
        entities = {}
        
        for ent in doc.ents:
            ent_type = ent.label_
            if ent_type not in entities:
                entities[ent_type] = []
            
            entity_text = ent.text.strip()
            if entity_text and entity_text not in entities[ent_type]:
                entities[ent_type].append(entity_text)
        
        return entities
    
    def get_text_summary(self, text: str) -> Dict[str, any]:
        """
        Get a comprehensive summary of the text.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict[str, any]: Dictionary containing text summary
        """
        summary = {
            'statistics': self.calculate_text_statistics(text),
            'keywords': self.extract_keywords(text),
            'technical_skills': self.extract_technical_skills(text),
            'entities': self.extract_entities(text)
        }
        
        # Add section analysis if it looks like a resume
        if any(section in text.lower() for section in self.resume_sections):
            summary['resume_sections'] = self.identify_resume_sections(text)
        
        return summary
    
    def compare_texts(self, text1: str, text2: str, method: str = "keywords") -> Dict[str, any]:
        """
        Compare two texts and return similarity metrics.
        
        Args:
            text1 (str): First text (e.g., resume)
            text2 (str): Second text (e.g., job description)
            method (str): Comparison method ('keywords', 'entities', 'skills')
            
        Returns:
            Dict[str, any]: Comparison results
        """
        if method == "keywords":
            return self._compare_keywords(text1, text2)
        elif method == "entities":
            return self._compare_entities(text1, text2)
        elif method == "skills":
            return self._compare_skills(text1, text2)
        else:
            raise ValueError(f"Unknown comparison method: {method}")
    
    def _compare_keywords(self, text1: str, text2: str) -> Dict[str, any]:
        """Compare texts based on keyword overlap."""
        keywords1 = set(word for word, _ in self.extract_keywords(text1, top_n=50))
        keywords2 = set(word for word, _ in self.extract_keywords(text2, top_n=50))
        
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        jaccard_similarity = len(intersection) / len(union) if union else 0
        
        return {
            'method': 'keywords',
            'similarity_score': jaccard_similarity,
            'common_keywords': list(intersection),
            'unique_to_text1': list(keywords1 - keywords2),
            'unique_to_text2': list(keywords2 - keywords1),
            'total_keywords_text1': len(keywords1),
            'total_keywords_text2': len(keywords2)
        }
    
    def _compare_entities(self, text1: str, text2: str) -> Dict[str, any]:
        """Compare texts based on named entity overlap."""
        entities1 = self.extract_entities(text1)
        entities2 = self.extract_entities(text2)
        
        # Flatten all entities
        all_entities1 = set()
        all_entities2 = set()
        
        for entity_list in entities1.values():
            all_entities1.update(entity_list)
        
        for entity_list in entities2.values():
            all_entities2.update(entity_list)
        
        intersection = all_entities1.intersection(all_entities2)
        union = all_entities1.union(all_entities2)
        
        jaccard_similarity = len(intersection) / len(union) if union else 0
        
        return {
            'method': 'entities',
            'similarity_score': jaccard_similarity,
            'common_entities': list(intersection),
            'entities_text1': entities1,
            'entities_text2': entities2
        }
    
    def _compare_skills(self, text1: str, text2: str) -> Dict[str, any]:
        """Compare texts based on technical skills overlap."""
        skills1 = self.extract_technical_skills(text1)
        skills2 = self.extract_technical_skills(text2)
        
        # Flatten all skills
        all_skills1 = set()
        all_skills2 = set()
        
        for skill_list in skills1.values():
            all_skills1.update(skill_list)
        
        for skill_list in skills2.values():
            all_skills2.update(skill_list)
        
        intersection = all_skills1.intersection(all_skills2)
        union = all_skills1.union(all_skills2)
        
        jaccard_similarity = len(intersection) / len(union) if union else 0
        
        return {
            'method': 'skills',
            'similarity_score': jaccard_similarity,
            'common_skills': list(intersection),
            'skills_text1': skills1,
            'skills_text2': skills2
        }
