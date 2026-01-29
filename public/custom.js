// Research RAG - Custom JavaScript for UI interactions

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Research RAG UI initialized');
    
    // Check for indexing status periodically
    checkIndexingStatus();
    setInterval(checkIndexingStatus, 5000); // Check every 5 seconds
});

// Check if indexing is in progress
function checkIndexingStatus() {
    // This will be updated by Chainlit backend
    const indexingIndicator = document.getElementById('indexing-progress');
    if (indexingIndicator) {
        // Show/hide based on data attributes set by backend
        const isIndexing = indexingIndicator.dataset.indexing === 'true';
        indexingIndicator.style.display = isIndexing ? 'block' : 'none';
    }
}

// Update slider values in real-time
function updateSliderValue(sliderId, displayId) {
    const slider = document.getElementById(sliderId);
    const display = document.getElementById(displayId);
    if (slider && display) {
        display.textContent = slider.value;
    }
}

// Model selection handler
function onModelChange(selectElement) {
    const selectedModel = selectElement.value;
    console.log('Model changed to:', selectedModel);
    
    // Send to backend via Chainlit
    if (window.chainlit) {
        window.chainlit.sendMessage({
            type: 'model_change',
            model: selectedModel
        });
    }
}

// Export functions to global scope
window.updateSliderValue = updateSliderValue;
window.onModelChange = onModelChange;
