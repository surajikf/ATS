#!/usr/bin/env python3
"""
Test script for the enhanced bulk resume processing functionality.
This script demonstrates the key features of the bulk processor.
"""

import os
import tempfile
from pathlib import Path
from bulk_processor import BulkResumeProcessor

def create_sample_files():
    """Create sample text files for testing."""
    sample_resumes = [
        ("John_Doe_Resume.txt", """
        JOHN DOE
        Software Engineer
        
        SKILLS:
        - Python, JavaScript, React
        - Machine Learning, Data Analysis
        - AWS, Docker, Kubernetes
        
        EXPERIENCE:
        - Senior Developer at Tech Corp (3 years)
        - Full Stack Developer at Startup Inc (2 years)
        """),
        
        ("Jane_Smith_CV.txt", """
        JANE SMITH
        Data Scientist
        
        SKILLS:
        - Python, R, SQL
        - TensorFlow, PyTorch, Scikit-learn
        - Data Visualization, Statistical Analysis
        
        EXPERIENCE:
        - Data Scientist at Data Corp (4 years)
        - Research Assistant at University (2 years)
        """),
        
        ("Bob_Johnson_Resume.txt", """
        BOB JOHNSON
        Product Manager
        
        SKILLS:
        - Product Strategy, User Research
        - Agile, Scrum, JIRA
        - Market Analysis, Competitive Research
        
        EXPERIENCE:
        - Product Manager at Product Corp (5 years)
        - Business Analyst at Consulting Inc (3 years)
        """)
    ]
    
    temp_files = []
    for filename, content in sample_resumes:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_file.write(content)
        temp_file.close()
        
        # Create a mock file object similar to Streamlit's uploaded file
        class MockFile:
            def __init__(self, path, name):
                self.path = path
                self.name = name
            
            def getvalue(self):
                with open(self.path, 'r') as f:
                    return f.read().encode()
            
            @property
            def size(self):
                return len(self.getvalue())
        
        temp_files.append(MockFile(temp_file.name, filename))
    
    return temp_files

def cleanup_temp_files(temp_files):
    """Clean up temporary files."""
    for mock_file in temp_files:
        try:
            os.unlink(mock_file.path)
        except:
            pass

def test_bulk_processing():
    """Test the bulk processing functionality."""
    print("🏭 I Knowledge Factory Pvt. Ltd.")
    print("🚀 Testing Enhanced Bulk Resume Processing")
    print("=" * 50)
    
    # Sample job description
    job_description = """
    SENIOR SOFTWARE ENGINEER
    
    We are looking for a Senior Software Engineer with expertise in:
    - Python, JavaScript, and modern web frameworks
    - Machine Learning and Data Analysis
    - Cloud platforms (AWS, Azure, GCP)
    - DevOps practices and containerization
    
    REQUIREMENTS:
    - 5+ years of software development experience
    - Strong problem-solving skills
    - Experience with agile methodologies
    - Bachelor's degree in Computer Science or related field
    """
    
    print(f"📋 Job Description Length: {len(job_description)} characters")
    
    # Create sample resume files
    print("\n📄 Creating sample resume files...")
    temp_files = create_sample_files()
    
    try:
        # Initialize bulk processor
        print("🔧 Initializing bulk processor...")
        bulk_processor = BulkResumeProcessor()
        
        # Process resumes
        print(f"\n🔄 Processing {len(temp_files)} sample resumes...")
        print("Note: This is a simulation - actual Streamlit UI will show progress bars and real-time updates")
        
        # Simulate processing (without Streamlit UI elements)
        results = bulk_processor.process_bulk_resumes(
            job_description, 
            temp_files, 
            "Combined (TF-IDF + BERT)"
        )
        
        # Display results
        print("\n📊 Processing Results:")
        print(f"✅ Total Files: {results['summary']['total_files']}")
        print(f"✅ Successfully Processed: {results['summary']['successful']}")
        print(f"❌ Failed: {results['summary']['failed']}")
        print(f"📈 Success Rate: {results['summary']['success_rate']:.1f}%")
        print(f"🎯 Average Score: {results['summary']['average_score']:.1f}%")
        
        # Show top candidates
        if results['summary']['top_candidates']:
            print("\n🏆 Top Candidates:")
            for i, candidate in enumerate(results['summary']['top_candidates'][:3], 1):
                print(f"{i}. {candidate['filename']}: {candidate['similarity_score']:.1f}%")
        
        # Show score distribution
        if results['summary']['score_distribution']:
            print("\n📈 Score Distribution:")
            for range_name, count in results['summary']['score_distribution'].items():
                print(f"   {range_name}: {count} candidates")
        
        # Test export functionality
        print("\n📤 Testing export functionality...")
        for export_format in ['excel', 'csv', 'json']:
            success, file_path_or_error = bulk_processor.export_bulk_results(results, export_format)
            if success:
                print(f"✅ {export_format.upper()} export successful: {file_path_or_error}")
                # Clean up exported file
                try:
                    os.unlink(file_path_or_error)
                except:
                    pass
            else:
                print(f"❌ {export_format.upper()} export failed: {file_path_or_error}")
        
        print("\n🎉 Bulk processing test completed successfully!")
        print("The enhanced UI will provide:")
        print("   • Beautiful gradient cards and visual elements")
        print("   • Real-time progress tracking with ETA")
        print("   • File validation before processing")
        print("   • Enhanced error handling and user feedback")
        print("   • Professional HR-focused interface")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
    
    finally:
        # Clean up
        cleanup_temp_files(temp_files)
        print("\n🧹 Temporary files cleaned up")

if __name__ == "__main__":
    test_bulk_processing()
