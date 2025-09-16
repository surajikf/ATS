#!/usr/bin/env python3
"""
Demo script for the Saved Job Description functionality.
This demonstrates how the system works without running the full Streamlit app.
"""

import json
import os
from datetime import datetime

def load_saved_jds():
    """Load saved job descriptions from JSON file"""
    try:
        if os.path.exists('saved_job_descriptions.json'):
            with open('saved_job_descriptions.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading saved job descriptions: {e}")
        return []

def save_jd_to_storage(jd_data):
    """Save a new job description to storage"""
    try:
        saved_jds = load_saved_jds()
        
        # Check if JD with same title already exists
        existing_index = next((i for i, jd in enumerate(saved_jds) if jd['title'] == jd_data['title']), None)
        
        if existing_index is not None:
            # Update existing JD
            saved_jds[existing_index].update(jd_data)
            saved_jds[existing_index]['last_updated'] = datetime.now().isoformat()
            saved_jds[existing_index]['usage_count'] = saved_jds[existing_index].get('usage_count', 0) + 1
            print(f"✅ Updated existing job description: {jd_data['title']}")
        else:
            # Add new JD
            jd_data['id'] = len(saved_jds) + 1
            jd_data['created_date'] = datetime.now().isoformat()
            jd_data['last_updated'] = datetime.now().isoformat()
            jd_data['usage_count'] = 1
            saved_jds.append(jd_data)
            print(f"✅ Added new job description: {jd_data['title']}")
        
        # Save to file
        with open('saved_job_descriptions.json', 'w', encoding='utf-8') as f:
            json.dump(saved_jds, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error saving job description: {e}")
        return False

def delete_saved_jd(jd_id):
    """Delete a saved job description"""
    try:
        saved_jds = load_saved_jds()
        jd_to_delete = next((jd for jd in saved_jds if jd['id'] == jd_id), None)
        
        if jd_to_delete:
            saved_jds = [jd for jd in saved_jds if jd['id'] != jd_id]
            
            # Reassign IDs
            for i, jd in enumerate(saved_jds):
                jd['id'] = i + 1
            
            with open('saved_job_descriptions.json', 'w', encoding='utf-8') as f:
                json.dump(saved_jds, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Deleted job description: {jd_to_delete['title']}")
            return True
        else:
            print(f"❌ Job description with ID {jd_id} not found")
            return False
            
    except Exception as e:
        print(f"Error deleting job description: {e}")
        return False

def display_saved_jds():
    """Display all saved job descriptions"""
    saved_jds = load_saved_jds()
    
    if not saved_jds:
        print("📝 No saved job descriptions found.")
        return
    
    print(f"\n📚 Found {len(saved_jds)} saved job description(s):")
    print("=" * 80)
    
    for jd in saved_jds:
        print(f"📋 {jd['title']}")
        print(f"   ID: {jd['id']}")
        print(f"   Description: {jd.get('description', 'No description')[:100]}...")
        print(f"   Category: {jd.get('category', 'General')}")
        print(f"   Created: {jd['created_date'][:10]}")
        print(f"   Last Updated: {jd['last_updated'][:10]}")
        print(f"   Usage Count: {jd.get('usage_count', 0)}")
        print("-" * 80)

def demo_saved_jd_functionality():
    """Demonstrate the saved JD functionality"""
    print("🚀 Saved Job Description Functionality Demo")
    print("=" * 50)
    
    # Clear any existing data
    if os.path.exists('saved_job_descriptions.json'):
        os.remove('saved_job_descriptions.json')
        print("🗑️ Cleared existing data")
    
    print("\n1️⃣ Adding sample job descriptions...")
    
    # Add some sample job descriptions
    sample_jds = [
        {
            'title': 'Software Engineer - Full Stack',
            'description': 'Full-stack development with React, Node.js, and cloud technologies',
            'requirements': 'React, Node.js, Python, AWS, Docker',
            'category': 'Engineering'
        },
        {
            'title': 'Data Scientist',
            'description': 'Machine learning, Python, and statistical analysis expertise',
            'requirements': 'Python, ML, Statistics, SQL, Pandas',
            'category': 'Data Science'
        },
        {
            'title': 'Product Manager',
            'description': 'Product strategy, user research, and agile methodologies',
            'requirements': 'Product Strategy, User Research, Agile, Analytics',
            'category': 'Product'
        }
    ]
    
    for jd in sample_jds:
        save_jd_to_storage(jd)
    
    print("\n2️⃣ Displaying saved job descriptions...")
    display_saved_jds()
    
    print("\n3️⃣ Updating a job description...")
    # Update the first JD
    update_jd = {
        'title': 'Software Engineer - Full Stack',
        'description': 'Full-stack development with React, Node.js, Python, and cloud technologies. Experience with microservices and CI/CD required.',
        'requirements': 'React, Node.js, Python, AWS, Docker, Kubernetes, CI/CD',
        'category': 'Engineering'
    }
    save_jd_to_storage(update_jd)
    
    print("\n4️⃣ Displaying updated job descriptions...")
    display_saved_jds()
    
    print("\n5️⃣ Deleting a job description...")
    delete_saved_jd(2)  # Delete the Data Scientist JD
    
    print("\n6️⃣ Final state of saved job descriptions...")
    display_saved_jds()
    
    print("\n✅ Demo completed successfully!")
    print("\n💡 Key Features Demonstrated:")
    print("   • Save new job descriptions")
    print("   • Update existing job descriptions")
    print("   • Track usage count and timestamps")
    print("   • Delete job descriptions")
    print("   • Persistent storage in JSON format")
    print("   • Automatic ID management")

if __name__ == "__main__":
    demo_saved_jd_functionality()
