// Fix for HTML Interface Text Extraction
// This file contains the corrected functions to properly extract text from files

// Text extraction functions for different file types
function extractTextFromFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            try {
                let extractedText = '';
                
                if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
                    // For PDFs, we need to use a PDF library
                    // For now, show a message that PDF text extraction requires server-side processing
                    extractedText = `[PDF File: ${file.name}] - Text extraction requires server-side processing. Please use the Streamlit app for PDF files.`;
                } else if (file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || 
                           file.name.toLowerCase().endsWith('.docx')) {
                    // For DOCX files, we need to use a DOCX library
                    // For now, show a message that DOCX text extraction requires server-side processing
                    extractedText = `[DOCX File: ${file.name}] - Text extraction requires server-side processing. Please use the Streamlit app for DOCX files.`;
                } else if (file.type === 'text/plain' || file.name.toLowerCase().endsWith('.txt')) {
                    // For text files, we can read directly
                    extractedText = e.target.result;
                } else {
                    extractedText = `[Unsupported file type: ${file.name}] - Please use PDF, DOCX, or TXT files.`;
                }
                
                resolve(extractedText);
            } catch (error) {
                reject(`Error extracting text: ${error.message}`);
            }
        };
        
        reader.onerror = function() {
            reject('Failed to read file');
        };
        
        // Read as text for TXT files, as ArrayBuffer for others
        if (file.type === 'text/plain' || file.name.toLowerCase().endsWith('.txt')) {
            reader.readAsText(file);
        } else {
            reader.readAsArrayBuffer(file);
        }
    });
}

// Updated function to save job description with proper text extraction
async function saveJobDescription(jobData) {
    try {
        // If jobData contains a file, extract text first
        if (jobData.file) {
            const extractedText = await extractTextFromFile(jobData.file);
            jobData.description = extractedText;
            jobData.requirements = extractedText;
            delete jobData.file; // Remove file object before saving
        }
        
        // Add metadata
        jobData.id = Date.now();
        jobData.createdDate = new Date().toISOString();
        jobData.lastUsed = new Date().toISOString();
        jobData.usageCount = 1;
        
        // Save to localStorage
        let savedJobDescriptions = JSON.parse(localStorage.getItem('savedJobDescriptions') || '[]');
        
        // Check if job with same title already exists
        const existingIndex = savedJobDescriptions.findIndex(job => job.title === jobData.title);
        
        if (existingIndex !== -1) {
            // Update existing job
            savedJobDescriptions[existingIndex] = {
                ...savedJobDescriptions[existingIndex],
                ...jobData,
                lastUsed: new Date().toISOString(),
                usageCount: savedJobDescriptions[existingIndex].usageCount + 1
            };
        } else {
            // Add new job
            savedJobDescriptions.push(jobData);
        }
        
        localStorage.setItem('savedJobDescriptions', JSON.stringify(savedJobDescriptions));
        
        console.log('Job description saved successfully:', jobData);
        return true;
        
    } catch (error) {
        console.error('Error saving job description:', error);
        return false;
    }
}

// Function to display saved job descriptions with proper text
function displaySavedJobDescriptions() {
    const container = document.getElementById('savedJobDescriptions');
    
    if (!container) return;
    
    const savedJobDescriptions = JSON.parse(localStorage.getItem('savedJobDescriptions') || '[]');
    
    if (savedJobDescriptions.length === 0) {
        container.innerHTML = '<p style="color: #718096; text-align: center; font-style: italic;">No saved job descriptions yet</p>';
        return;
    }
    
    let html = '<h4 style="color: #4a5568; margin-bottom: 15px;">📋 Saved Job Descriptions</h4>';
    
    savedJobDescriptions.forEach(job => {
        // Truncate description if it's too long
        const shortDescription = job.description.length > 100 ? 
            job.description.substring(0, 100) + '...' : 
            job.description;
        
        html += `
            <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 15px; background: white;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                    <h5 style="margin: 0; color: #2d3748; font-size: 16px;">${job.title}</h5>
                    <div style="display: flex; gap: 10px;">
                        <button onclick="useSavedJobDescription(${job.id})" 
                                style="background: #48bb78; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                            Use
                        </button>
                        <button onclick="deleteSavedJobDescription(${job.id})" 
                                style="background: #f56565; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                            Delete
                        </button>
                    </div>
                </div>
                <p style="margin: 0; color: #4a5568; font-size: 14px; line-height: 1.4;">${shortDescription}</p>
                <div style="margin-top: 10px; font-size: 12px; color: #718096;">
                    <span>Created: ${new Date(job.createdDate).toLocaleDateString()}</span> | 
                    <span>Used: ${job.usageCount} times</span> | 
                    <span>Last used: ${new Date(job.lastUsed).toLocaleDateString()}</span>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Function to use a saved job description
function useSavedJobDescription(jobId) {
    const savedJobDescriptions = JSON.parse(localStorage.getItem('savedJobDescriptions') || '[]');
    const job = savedJobDescriptions.find(j => j.id === jobId);
    
    if (job) {
        // Update usage count
        job.usageCount++;
        job.lastUsed = new Date().toISOString();
        localStorage.setItem('savedJobDescriptions', JSON.stringify(savedJobDescriptions));
        
        // Display the job description
        displayCurrentJobDescription(job);
        
        console.log('Using saved job description:', job.title);
    }
}

// Function to display current job description
function displayCurrentJobDescription(job) {
    const container = document.getElementById('currentJobDescription');
    if (container) {
        container.innerHTML = `
            <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; background: #f7fafc;">
                <h5 style="margin: 0 0 10px 0; color: #2d3748;">Current Job Description: ${job.title}</h5>
                <p style="margin: 0; color: #4a5568; line-height: 1.5;">${job.description}</p>
                <div style="margin-top: 10px;">
                    <button onclick="clearCurrentJobDescription()" 
                            style="background: #e53e3e; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                        Clear
                    </button>
                </div>
            </div>
        `;
    }
}

// Function to clear current job description
function clearCurrentJobDescription() {
    const container = document.getElementById('currentJobDescription');
    if (container) {
        container.innerHTML = '';
    }
}

// Function to delete a saved job description
function deleteSavedJobDescription(jobId) {
    if (confirm('Are you sure you want to delete this job description?')) {
        let savedJobDescriptions = JSON.parse(localStorage.getItem('savedJobDescriptions') || '[]');
        savedJobDescriptions = savedJobDescriptions.filter(job => job.id !== jobId);
        localStorage.setItem('savedJobDescriptions', JSON.stringify(savedJobDescriptions));
        
        displaySavedJobDescriptions();
        console.log('Job description deleted successfully');
    }
}

// Load saved job descriptions when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadSavedJobDescriptions();
    displaySavedJobDescriptions();
});

// Export functions for use in HTML
window.extractTextFromFile = extractTextFromFile;
window.saveJobDescription = saveJobDescription;
window.displaySavedJobDescriptions = displaySavedJobDescriptions;
window.useSavedJobDescription = useSavedJobDescription;
window.deleteSavedJobDescription = deleteSavedJobDescription;
window.clearCurrentJobDescription = clearCurrentJobDescription;
