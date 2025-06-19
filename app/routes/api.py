from flask import Blueprint, request, jsonify, current_app
import logging
from app.services.face_service import FaceService
import base64
import re
import os
from app.utils.image_utils import base64_to_image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api = Blueprint('api', __name__, url_prefix='/api')
face_service = FaceService()

# Temporarily disabled liveness challenge route
# @api.route('/liveness-challenge', methods=['GET'])
# def get_liveness_challenge():
#     """
#     Generate a random liveness challenge for anti-spoofing verification.
#     
#     Returns a list of actions for the user to perform during verification.
#     """
#     try:
#         # Generate random liveness challenge
#         actions = face_service.generate_liveness_challenge()
#         
#         return jsonify({
#             "success": True, 
#             "actions": actions,
#             "message": "Please perform these actions in sequence for liveness verification"
#         })
#     except Exception as e:
#         logger.error(f"Error generating liveness challenge: {str(e)}")
#         return jsonify({"success": False, "message": str(e)}), 500

@api.route('/verify', methods=['POST'])
def verify_face():
    """
    Verify a face against stored embeddings with anti-spoofing.
    
    Request should contain a base64 encoded image from webcam and completed actions.
    Returns the matched IC number or "No match".
    """
    try:
        # Get image data from request
        data = request.json
        if not data or 'image_data' not in data:
            logger.error("No image data received")
            return jsonify({"success": False, "message": "No image data received"}), 400
            
        # Extract the base64 image data
        image_data = data['image_data']
        # Remove the data:image/jpeg;base64, prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
            
        # Get completed actions if provided
        actions = data.get('completed_actions', [])
        logger.info(f"Received verification with actions: {actions}")
            
        # Convert base64 to image
        image = base64_to_image(image_data)
        if image is None:
            logger.error("Invalid image data")
            return jsonify({"error": "Invalid image data"}), 400
            
        # Verify the face with anti-spoofing
        matched, ic_number, message = face_service.verify_face(image, actions=actions)
        
        logger.info(f"Verification result: matched={matched}, ic_number={ic_number}, message={message}")
        
        return jsonify({
            "success": True,
            "matched": matched,
            "ic_number": ic_number,
            "message": message
        })
            
    except Exception as e:
        logger.error(f"Error in face verification: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api.route('/register', methods=['POST'])
def register_face():
    """
    Register a face manually through API with anti-spoofing.
    
    Request should contain a base64 encoded image, IC number, and completed liveness actions.
    Returns success or error message.
    """
    try:
        logger.info("Registration request received")
        data = request.json
        if not data:
            logger.error("No JSON data received in request")
            return jsonify({"success": False, "message": "No JSON data received"}), 400
            
        logger.info(f"Request data keys: {list(data.keys())}")
        
        if 'image_data' not in data or 'ic_number' not in data:
            logger.error("Missing image_data or ic_number in request")
            return jsonify({"success": False, "message": "Missing image data or IC number"}), 400
            
        ic_number = data['ic_number']
        # Validate IC number format (simple validation)
        if not re.match(r'^\d{12}$', ic_number):
            logger.error(f"Invalid IC number format: {ic_number}")
            return jsonify({"success": False, "message": "Invalid IC number format. Must be 12 digits."}), 400
            
        # Extract the base64 image data
        image_data = data['image_data']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
            
        # Get completed actions if provided
        actions = data.get('completed_actions', [])
        logger.info(f"Received registration with actions: {actions}")
            
        # Convert base64 to image
        image = base64_to_image(image_data)
        if image is None:
            logger.error("Invalid image data")
            return jsonify({"error": "Invalid image data"}), 400
            
        # Register the face using the face_service with anti-spoofing
        success, message = face_service.register_face(image, ic_number, actions=actions)
        
        if success:
            logger.info(f"Face registered for IC: {ic_number}")
            return jsonify({"success": True, "message": message})
        else:
            logger.error(f"Error registering face: {message}")
            return jsonify({"success": False, "message": message}), 400
            
    except Exception as e:
        logger.error(f"Error in face registration: {str(e)}")
        return jsonify({"error": str(e)}), 500
