// Face registration logic with anti-spoofing

document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('captureBtn');
    const icInput = document.getElementById('icNumber');
    const spinner = document.getElementById('spinner');
    const resultContainer = document.getElementById('resultContainer');
    const resultAlert = document.getElementById('resultAlert');
    const livenessContainer = document.getElementById('livenessContainer');
    const livenessInstructions = document.getElementById('livenessInstructions');
    const actionsList = document.getElementById('actionsList');
    const completeActionBtn = document.getElementById('completeActionBtn');
    
    // Liveness challenge state (temporarily disabled)
    let currentLivenessActions = [];
    let currentActionIndex = 0;
    let completedActions = [];Index = 0;
    
    // Get user media (webcam)
    async function startWebcam() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: 'user' }, 
                audio: false 
            });
            video.srcObject = stream;
        } catch (err) {
            console.error('Error accessing webcam:', err);
            alert('Error accessing webcam. Please ensure your camera is connected and you have granted permission.');
        }
    }
    
    // Get liveness challenge from server
    async function getLivenessChallenge() {
        try {
            const response = await fetch('/api/liveness-challenge');
            const data = await response.json();
            
            if (data.success && data.actions && data.actions.length > 0) {
                return data.actions;
            } else {
                console.error('Failed to get liveness challenge:', data.message);
                return null;
            }
        } catch (err) {
            console.error('Error getting liveness challenge:', err);
            return null;
        }
    }
    
    // Display liveness challenge to user
    function displayLivenessChallenge(actions) {
        // Clear previous actions
        actionsList.innerHTML = '';
        
        // Display each action as a list item
        actions.forEach(action => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.dataset.action = action;
            
            // Format action for display
            const displayAction = action.replace('_', ' ');
            li.textContent = displayAction.charAt(0).toUpperCase() + displayAction.slice(1);
            
            actionsList.appendChild(li);
        });
        
        // Show the first action as active
        if (actionsList.children.length > 0) {
            actionsList.children[0].classList.add('active', 'fw-bold');
        }
        
        // Show liveness container
        livenessContainer.classList.remove('d-none');
        livenessInstructions.textContent = 'Please complete the following actions to verify you are a real person:';
    }
    
    // Validate IC number
    function validateIC(ic) {
        // Simple validation - must be at least 3 characters
        return ic && ic.length >= 3;
    }
    
    // Capture image from webcam
    function captureImage() {
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert to base64
        return canvas.toDataURL('image/jpeg');
    }
    
    // Handle liveness challenge actions
    function handleLivenessAction() {
        if (currentActionIndex < currentLivenessActions.length) {
            // Mark current action as completed
            const actionItem = actionsList.children[currentActionIndex];
            actionItem.classList.remove('active');
            actionItem.classList.add('list-group-item-success');
            
            // Store completed action
            completedActions.push(currentLivenessActions[currentActionIndex]);
            
            // Move to next action
            currentActionIndex++;
            
            if (currentActionIndex < currentLivenessActions.length) {
                // Highlight next action
                actionsList.children[currentActionIndex].classList.add('active', 'fw-bold');
            } else {
                // All actions completed
                livenessInstructions.textContent = 'All actions completed! Click capture to proceed.';
                completeActionBtn.classList.add('d-none');
                captureBtn.disabled = false;
            }
        }
    }
    
    // Send image and IC to API for registration with anti-spoofing
    async function registerFace(imageData, icNumber) {
        try {
            console.log('Registering face with IC:', icNumber);
            console.log('Image data length:', imageData.length);
            console.log('Completed actions:', completedActions);
            
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image_data: imageData,
                    ic_number: icNumber,
                    completed_actions: completedActions
                })
            });
            
            console.log('Registration response status:', response.status);
            const jsonResponse = await response.json();
            console.log('Registration API response:', jsonResponse);
            
            return jsonResponse;
        } catch (err) {
            console.error('Error registering face:', err);
            return { 
                success: false, 
                message: 'Network error occurred during registration: ' + err.message 
            };
        }
    }
    
    // Update button state based on input validity
    function updateButtonState() {
        const icValue = icInput.value.trim();
        captureBtn.disabled = !validateIC(icValue);
    }
    
    // Input validation
    icInput.addEventListener('input', updateButtonState);
    
    // Initial button state
    updateButtonState();
    
    // Start liveness challenge process
    async function startLivenessChallenge() {
        // Liveness challenge temporarily disabled
        return true;
    }
    
    // Handle complete action button click
    completeActionBtn.addEventListener('click', function() {
        handleLivenessAction();
    });
    
    // Handle capture button click
    console.log('Setting up click event for captureBtn');
    captureBtn.addEventListener('click', async function() {
        console.log('Capture button clicked');
        const icValue = icInput.value.trim();
        console.log('IC value:', icValue);
        
        if (!validateIC(icValue)) {
            console.log('IC validation failed');
            alert('Please enter a valid IC number');
            return;
        }
        console.log('IC validation passed');
        
        // Liveness challenge temporarily disabled
        // Proceed directly with capture
        // Show loading spinner
        captureBtn.disabled = true;
        spinner.classList.remove('d-none');
        resultContainer.classList.add('d-none');
        livenessContainer.classList.add('d-none');
        
        // Capture image
        const imageData = captureImage();
        
        // Send to API for registration with anti-spoofing data
        const result = await registerFace(imageData, icValue);
        
        // Display result
        if (result.success) {
            resultAlert.className = 'alert alert-success';
            resultAlert.textContent = 'Registration successful!';
        } else {
            resultAlert.className = 'alert alert-danger';
            resultAlert.textContent = result.message || 'Registration failed. Please try again.';
            
            // If failed due to anti-spoofing, restart challenge
            if (result.message && result.message.includes('Anti-spoofing')) {
                // Reset for a new attempt
                setTimeout(() => {
                    // Reset liveness state
                    currentLivenessActions = [];
                    completedActions = [];
                    currentActionIndex = 0;
                    startLivenessChallenge();
                }, 3000);
            }
        }
        
        // Show result and reset state
        resultContainer.classList.remove('d-none');
        spinner.classList.add('d-none');
        captureBtn.disabled = !validateIC(icValue);
    });
    
    // Start webcam when page loads
    startWebcam();
    
    // Initialize UI elements
    if (!livenessContainer) {
        console.error('Liveness container not found! Make sure to add it to your HTML');
    }
    
    if (!completeActionBtn) {
        console.error('Complete action button not found! Make sure to add it to your HTML');
    }
});
