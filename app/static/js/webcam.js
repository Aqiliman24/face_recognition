// Webcam access and face verification logic with anti-spoofing

document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('captureBtn');
    const spinner = document.getElementById('spinner');
    const resultContainer = document.getElementById('resultContainer');
    const resultAlert = document.getElementById('resultAlert');
    const verificationStatus = document.getElementById('verificationStatus');
    const icNumber = document.getElementById('icNumber');
    const livenessContainer = document.getElementById('livenessContainer');
    const livenessInstructions = document.getElementById('livenessInstructions');
    const actionsList = document.getElementById('actionsList');
    const completeActionBtn = document.getElementById('completeActionBtn');
    
    // Liveness challenge state (temporarily disabled)
    let currentLivenessActions = [];
    let completedActions = [];
    let currentActionIndex = 0;
    
    // Get user media (webcam)
    async function startWebcam() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: 'user' }, 
                audio: false 
            });
            video.srcObject = stream;
            captureBtn.disabled = false;
        } catch (err) {
            console.error('Error accessing webcam:', err);
            alert('Error accessing webcam. Please ensure your camera is connected and you have granted permission.');
        }
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
    
    // Get liveness challenge from server
    async function getLivenessChallenge() {
        try {
            console.log('Fetching liveness challenge from server...');
            const response = await fetch('/api/liveness-challenge');
            console.log('Liveness challenge response status:', response.status);
            
            const data = await response.json();
            console.log('Liveness challenge data:', data);
            
            if (data.success && data.actions && data.actions.length > 0) {
                console.log('Successfully received liveness actions:', data.actions);
                return data.actions;
            } else {
                console.error('Failed to get liveness challenge:', data.message || 'Unknown error');
                alert('Failed to get liveness challenge: ' + (data.message || 'Unknown error'));
                return null;
            }
        } catch (err) {
            console.error('Error getting liveness challenge:', err);
            alert('Error getting liveness challenge: ' + err.message);
            return null;
        }
    }
    
    // Display liveness challenge to user
    function displayLivenessChallenge(actions) {
        console.log('Displaying liveness challenge with actions:', actions);
        
        if (!livenessContainer) {
            console.error('Liveness container element not found');
            alert('Error: Liveness container element not found. Anti-spoofing may not work properly.');
            return;
        }
        
        if (!actionsList) {
            console.error('Actions list element not found');
            alert('Error: Actions list element not found. Anti-spoofing may not work properly.');
            return;
        }
        
        // Clear previous actions
        actionsList.innerHTML = '';
        console.log('Cleared previous actions list');
        
        // Display each action as a list item
        actions.forEach((action, index) => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.dataset.action = action;
            
            // Format action for display
            const displayAction = action.replace('_', ' ');
            li.textContent = displayAction.charAt(0).toUpperCase() + displayAction.slice(1);
            
            actionsList.appendChild(li);
            console.log(`Added action ${index + 1}: ${action}`);
        });
        
        // Show the first action as active
        if (actionsList.children.length > 0) {
            actionsList.children[0].classList.add('active', 'fw-bold');
            console.log('Set first action as active');
        }
        
        // Show liveness container
        livenessContainer.classList.remove('d-none');
        livenessInstructions.textContent = 'Please complete the following actions to verify you are a real person:';
        console.log('Liveness container displayed');
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
    
    // Send image to API for verification with anti-spoofing
    async function verifyFace(imageData) {
        try {
            console.log('Sending verification request with completed actions:', completedActions);
            
            const requestData = {
                image_data: imageData,
                completed_actions: completedActions
            };
            
            console.log('Request payload:', JSON.stringify(requestData).substring(0, 100) + '...');
            
            const response = await fetch('/api/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            console.log('Verification response status:', response.status);
            
            const result = await response.json();
            console.log('Verification result:', result);
            
            return result;
        } catch (err) {
            console.error('Error verifying face:', err);
            alert('Error during verification: ' + err.message);
            return { 
                success: false, 
                matched: false, 
                message: 'Network error occurred during verification: ' + err.message 
            };
        }
    }
    
    // Start liveness challenge process
    async function startLivenessChallenge() {
        // Liveness challenge temporarily disabled
        console.log('Liveness challenge disabled');
        return true;
    }
    
    // Handle complete action button click
    if (completeActionBtn) {
        completeActionBtn.addEventListener('click', function() {
            handleLivenessAction();
        });
    }
    
    // Handle capture button click
    captureBtn.addEventListener('click', async function() {
        // Liveness challenge temporarily disabled
        // Proceed directly with capture
        // Show loading spinner
        captureBtn.disabled = true;
        spinner.classList.remove('d-none');
        resultContainer.classList.add('d-none');
        if (livenessContainer) {
            livenessContainer.classList.add('d-none');
        }
        
        // Capture image
        const imageData = captureImage();
        
        // Send to API for verification with anti-spoofing data
        const result = await verifyFace(imageData);
        
        // Display result
        if (result.success) {
            if (result.matched) {
                resultAlert.className = 'alert alert-success';
                resultAlert.textContent = 'Verification successful!';
                verificationStatus.textContent = 'Matched';
                icNumber.textContent = result.ic_number;
            } else {
                resultAlert.className = 'alert alert-warning';
                resultAlert.textContent = result.message || 'No matching face found.';
                verificationStatus.textContent = 'Not Matched';
                icNumber.textContent = '-';
                
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
        } else {
            resultAlert.className = 'alert alert-danger';
            resultAlert.textContent = result.message || 'Verification failed. Please try again.';
            verificationStatus.textContent = 'Error';
            icNumber.textContent = '-';
        }
        
        // Show result and reset state
        resultContainer.classList.remove('d-none');
        spinner.classList.add('d-none');
        captureBtn.disabled = false;
    });
    
    // Start webcam when page loads
    startWebcam();
    
    // Check if we have liveness elements
    if (!livenessContainer || !actionsList || !completeActionBtn || !livenessInstructions) {
        console.warn('Some liveness detection UI elements are missing. Adding them dynamically.');
        
        // Create liveness container if it doesn't exist
        if (!livenessContainer) {
            // Create liveness container dynamically if not in HTML
            livenessContainer = document.createElement('div');
            livenessContainer.id = 'livenessContainer';
            livenessContainer.className = 'card mb-4 d-none';
            
            const cardHeader = document.createElement('div');
            cardHeader.className = 'card-header bg-info text-white';
            cardHeader.innerHTML = '<h5 class="mb-0">Anti-Spoofing Check</h5>';
            
            const cardBody = document.createElement('div');
            cardBody.className = 'card-body';
            
            livenessInstructions = document.createElement('p');
            livenessInstructions.id = 'livenessInstructions';
            livenessInstructions.className = 'text-center mb-3';
            livenessInstructions.textContent = 'Please complete the following actions to verify you are a real person:';
            
            actionsList = document.createElement('ul');
            actionsList.id = 'actionsList';
            actionsList.className = 'list-group mb-3';
            
            const buttonContainer = document.createElement('div');
            buttonContainer.className = 'text-center';
            
            completeActionBtn = document.createElement('button');
            completeActionBtn.id = 'completeActionBtn';
            completeActionBtn.className = 'btn btn-primary';
            completeActionBtn.innerHTML = '<i class="bi bi-check me-2"></i> I\'ve completed this action';
            completeActionBtn.addEventListener('click', handleLivenessAction);
            
            buttonContainer.appendChild(completeActionBtn);
            cardBody.appendChild(livenessInstructions);
            cardBody.appendChild(actionsList);
            cardBody.appendChild(buttonContainer);
            
            livenessContainer.appendChild(cardHeader);
            livenessContainer.appendChild(cardBody);
            
            // Insert before the result container
            const parentElement = resultContainer.parentElement;
            parentElement.insertBefore(livenessContainer, resultContainer);
        }
    }
});
