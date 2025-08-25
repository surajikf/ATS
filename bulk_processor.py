"""
Bulk resume processing module for HR teams.
Handles multiple resume uploads and batch comparison against job descriptions.
"""

import logging
import pandas as pd
import tempfile
import os
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
from datetime import datetime
import streamlit as st

from text_processor import TextProcessor
from similarity_calculator import SimilarityCalculator
from file_handler import FileHandler
from utils import ExportUtils

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BulkResumeProcessor:
    """
    A class for processing multiple resumes against a single job description.
    Designed for HR teams to efficiently screen multiple candidates.
    
    Powered by I Knowledge Factory Pvt. Ltd.
    Advanced AI & NLP Technology for HR Excellence
    """
    
    def __init__(self):
        """Initialize the bulk processor."""
        self.text_processor = TextProcessor()
        self.similarity_calculator = SimilarityCalculator(use_gpu=False)
        self.file_handler = FileHandler()
        
        # Supported file types for bulk upload
        self.supported_extensions = ['.pdf', '.docx', '.txt']
        
        # Results storage
        self.bulk_results = []
        self.job_description = ""
        
    def process_bulk_resumes(self, job_description: str, resume_files: List, 
                           comparison_method: str = "Combined") -> Dict[str, Any]:
        """
        Process multiple resumes against a single job description.
        
        Args:
            job_description (str): The job description to compare against
            resume_files (List): List of uploaded resume files
            comparison_method (str): Method to use for comparison
            
        Returns:
            Dict[str, Any]: Bulk processing results
        """
        self.job_description = job_description
        self.bulk_results = []
        
        total_files = len(resume_files)
        successful = 0
        failed = 0
        
        # Enhanced progress tracking with better UI
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create a more informative progress display
        progress_container = st.container()
        with progress_container:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                progress_text = st.empty()
            with col2:
                success_count = st.empty()
            with col3:
                failed_count = st.empty()
            with col4:
                eta_text = st.empty()
        
        # Estimate processing time (rough estimate: 2-5 seconds per file)
        estimated_time_per_file = 3  # seconds
        total_estimated_time = total_files * estimated_time_per_file
        eta_text.text(f"⏱️ Est. Time: {total_estimated_time//60}m {total_estimated_time%60}s")
        
        # Pre-validate files
        st.info(f"🔍 Validating {total_files} files before processing...")
        valid_files = []
        for file in resume_files:
            file_ext = Path(file.name).suffix.lower()
            if file_ext in ['.pdf', '.docx', '.txt']:
                valid_files.append(file)
            else:
                st.warning(f"⚠️ {file.name} has unsupported format: {file_ext}")
        
        if len(valid_files) != len(resume_files):
            st.warning(f"⚠️ {len(resume_files) - len(valid_files)} files have unsupported formats and will be skipped.")
        
        # Use only valid files for processing
        resume_files = valid_files
        total_files = len(resume_files)
        
        if total_files == 0:
            st.error("❌ No valid files to process. Please upload files with supported formats (PDF, DOCX, TXT).")
            return {
                'summary': {
                    'total_files': 0,
                    'successful': 0,
                    'failed': 0,
                    'success_rate': 0,
                    'average_score': 0,
                    'top_candidates': [],
                    'score_distribution': {}
                },
                'results': [],
                'job_description': job_description,
                'comparison_method': comparison_method,
                'timestamp': datetime.now().isoformat()
            }
        
        for idx, resume_file in enumerate(resume_files):
            try:
                # Update progress
                progress = (idx + 1) / total_files
                progress_bar.progress(progress)
                
                # Update status information
                status_text.text(f"🔄 Processing: {resume_file.name}")
                progress_text.text(f"Progress: {idx + 1}/{total_files} ({progress*100:.1f}%)")
                success_count.text(f"✅ Success: {successful}")
                failed_count.text(f"❌ Failed: {failed}")
                
                # Process individual resume
                result = self._process_single_resume(resume_file, comparison_method)
                
                if result:
                    self.bulk_results.append(result)
                    successful += 1
                    # Show success feedback
                    st.success(f"✅ {resume_file.name} processed successfully")
                else:
                    failed += 1
                    # Show failure feedback
                    st.error(f"❌ {resume_file.name} failed to process")
                    
            except Exception as e:
                logger.error(f"Error processing {resume_file.name}: {str(e)}")
                failed += 1
                # Add failed result for tracking
                self.bulk_results.append({
                    'filename': resume_file.name,
                    'status': 'failed',
                    'error': str(e),
                    'similarity_score': 0,
                    'processing_time': 0,
                    'word_count': 0,
                    'key_skills': [],
                    'resume_text_length': 0
                })
                # Show error feedback
                st.error(f"❌ {resume_file.name} - Error: {str(e)}")
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        progress_container.empty()
        
        # Show final summary
        if successful > 0:
            st.success(f"🎉 Bulk processing complete! {successful} out of {total_files} resumes processed successfully.")
        if failed > 0:
            st.warning(f"⚠️ {failed} resumes failed to process. Check the detailed results below.")
        
        # Generate summary
        summary = self._generate_bulk_summary(successful, failed, total_files)
        
        return {
            'summary': summary,
            'results': self.bulk_results,
            'job_description': job_description,
            'comparison_method': comparison_method,
            'timestamp': datetime.now().isoformat()
        }
    
    def _process_single_resume(self, resume_file, comparison_method: str) -> Optional[Dict[str, Any]]:
        """Process a single resume file."""
        start_time = datetime.now()
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(resume_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Extract text from resume
            success, text_or_error = self.file_handler.extract_text(tmp_file_path)
            
            if not success:
                logger.error(f"Failed to extract text from {resume_file.name}: {text_or_error}")
                return None
            
            resume_text = text_or_error
            
            # Calculate similarity based on method
            if comparison_method == "Combined (TF-IDF + BERT)":
                similarity_result = self.similarity_calculator.get_similarity_breakdown(
                    self.job_description, resume_text
                )
                score = similarity_result['overall_score']
            elif comparison_method == "TF-IDF Only":
                similarity_result = self.similarity_calculator.calculate_tfidf_similarity(
                    self.job_description, resume_text
                )
                score = similarity_result['similarity_score']
            else:  # BERT Only
                similarity_result = self.similarity_calculator.calculate_bert_similarity(
                    self.job_description, resume_text
                )
                score = similarity_result['similarity_score']
            
            # Get text analysis
            text_analysis = self.text_processor.get_text_summary(resume_text)
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            return {
                'filename': resume_file.name,
                'status': 'success',
                'similarity_score': score,
                'resume_text_length': len(resume_text),
                'word_count': text_analysis['statistics']['total_words'],
                'key_skills': list(text_analysis['technical_skills'].keys()),
                'processing_time': processing_time,
                'comparison_method': comparison_method,
                'full_results': similarity_result
            }
            
        except Exception as e:
            logger.error(f"Error processing {resume_file.name}: {str(e)}")
            # Clean up temp file if it exists
            if 'tmp_file_path' in locals():
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
            return None
    
    def _generate_bulk_summary(self, successful: int, failed: int, total: int) -> Dict[str, Any]:
        """Generate a summary of bulk processing results."""
        if not self.bulk_results:
            return {
                'total_files': total,
                'successful': successful,
                'failed': failed,
                'success_rate': 0,
                'average_score': 0,
                'top_candidates': [],
                'score_distribution': {}
            }
        
        # Calculate statistics
        successful_results = [r for r in self.bulk_results if r['status'] == 'success']
        
        if successful_results:
            scores = [r['similarity_score'] for r in successful_results]
            average_score = sum(scores) / len(scores)
            
            # Top candidates (top 5 by score)
            top_candidates = sorted(successful_results, key=lambda x: x['similarity_score'], reverse=True)[:5]
            
            # Score distribution
            score_ranges = {
                'Excellent (80-100%)': len([s for s in scores if s >= 80]),
                'Good (60-79%)': len([s for s in scores if 60 <= s < 80]),
                'Fair (40-59%)': len([s for s in scores if 40 <= s < 60]),
                'Poor (20-39%)': len([s for s in scores if 20 <= s < 40]),
                'Very Poor (0-19%)': len([s for s in scores if s < 20])
            }
        else:
            average_score = 0
            top_candidates = []
            score_ranges = {}
        
        return {
            'total_files': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total) * 100 if total > 0 else 0,
            'average_score': round(average_score, 2),
            'top_candidates': top_candidates,
            'score_distribution': score_ranges
        }
    
    def export_bulk_results(self, results: Dict[str, Any], format_type: str = "excel") -> Tuple[bool, str]:
        """
        Export bulk processing results.
        
        Args:
            results (Dict[str, Any]): Bulk processing results
            format_type (str): Export format ('excel', 'csv', 'json')
            
        Returns:
            Tuple[bool, str]: (success, file_path_or_error)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format_type == "excel":
                return self._export_to_excel(results, timestamp)
            elif format_type == "csv":
                return self._export_to_csv(results, timestamp)
            else:  # JSON
                return self._export_to_json(results, timestamp)
                
        except Exception as e:
            error_msg = f"Error exporting bulk results: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _export_to_excel(self, results: Dict[str, Any], timestamp: str) -> Tuple[bool, str]:
        """Export results to Excel format."""
        try:
            # Create main results DataFrame
            results_data = []
            for result in results['results']:
                if result['status'] == 'success':
                    results_data.append({
                        'Filename': result['filename'],
                        'Similarity Score (%)': result['similarity_score'],
                        'Word Count': result['word_count'],
                        'Key Skills': ', '.join(result['key_skills']),
                        'Processing Time (s)': result['processing_time'],
                        'Status': result['status']
                    })
                else:
                    results_data.append({
                        'Filename': result['filename'],
                        'Similarity Score (%)': 'N/A',
                        'Word Count': 'N/A',
                        'Key Skills': 'N/A',
                        'Processing Time (s)': 'N/A',
                        'Status': result['status'],
                        'Error': result.get('error', 'Unknown error')
                    })
            
            # Create summary DataFrame
            summary_data = [{
                'Metric': 'Total Files',
                'Value': results['summary']['total_files']
            }, {
                'Metric': 'Successfully Processed',
                'Value': results['summary']['successful']
            }, {
                'Metric': 'Failed',
                'Value': results['summary']['failed']
            }, {
                'Metric': 'Success Rate (%)',
                'Value': results['summary']['success_rate']
            }, {
                'Metric': 'Average Similarity Score (%)',
                'Value': results['summary']['average_score']
            }]
            
            # Create score distribution DataFrame
            dist_data = []
            for range_name, count in results['summary']['score_distribution'].items():
                dist_data.append({
                    'Score Range': range_name,
                    'Number of Candidates': count
                })
            
            # Export to Excel
            filename = f"bulk_resume_analysis_{timestamp}.xlsx"
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                pd.DataFrame(results_data).to_excel(writer, sheet_name='Results', index=False)
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                pd.DataFrame(dist_data).to_excel(writer, sheet_name='Score Distribution', index=False)
            
            return True, filename
            
        except Exception as e:
            return False, f"Error creating Excel file: {str(e)}"
    
    def _export_to_csv(self, results: Dict[str, Any], timestamp: str) -> Tuple[bool, str]:
        """Export results to CSV format."""
        try:
            # Create results DataFrame
            results_data = []
            for result in results['results']:
                if result['status'] == 'success':
                    results_data.append({
                        'filename': result['filename'],
                        'similarity_score': result['similarity_score'],
                        'word_count': result['word_count'],
                        'key_skills': ', '.join(result['key_skills']),
                        'processing_time': result['processing_time'],
                        'status': result['status']
                    })
                else:
                    results_data.append({
                        'filename': result['filename'],
                        'similarity_score': 'N/A',
                        'word_count': 'N/A',
                        'key_skills': 'N/A',
                        'processing_time': 'N/A',
                        'status': result['status'],
                        'error': result.get('error', 'Unknown error')
                    })
            
            filename = f"bulk_resume_analysis_{timestamp}.csv"
            df = pd.DataFrame(results_data)
            df.to_csv(filename, index=False)
            
            return True, filename
            
        except Exception as e:
            return False, f"Error creating CSV file: {str(e)}"
    
    def _export_to_json(self, results: Dict[str, Any], timestamp: str) -> Tuple[bool, str]:
        """Export results to JSON format."""
        try:
            filename = f"bulk_resume_analysis_{timestamp}.json"
            success, error = ExportUtils.export_results_to_json(results, filename)
            return success, filename if success else error
            
        except Exception as e:
            return False, f"Error creating JSON file: {str(e)}"
    
    def get_top_candidates(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Get top N candidates by similarity score."""
        successful_results = [r for r in self.bulk_results if r['status'] == 'success']
        return sorted(successful_results, key=lambda x: x['similarity_score'], reverse=True)[:top_n]
    
    def get_candidates_by_score_range(self, min_score: float, max_score: float) -> List[Dict[str, Any]]:
        """Get candidates within a specific score range."""
        successful_results = [r for r in self.bulk_results if r['status'] == 'success']
        return [r for r in successful_results if min_score <= r['similarity_score'] <= max_score]
