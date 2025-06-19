import os
import pickle
import face_recognition
import numpy as np
from PIL import Image
import io
import logging
import cv2
import random
from pathlib import Path
from scipy.ndimage import variance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceService:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
        else:
            self.faces_dir = './faces'
            self.use_s3 = False
            self.aws_bucket = None
            self.liveness_threshold = 0.8  # Default threshold for liveness detection
            self.texture_threshold = 25.0  # Default threshold for texture analysis
            
    def init_app(self, app):
        self.faces_dir = app.config['FACES_DIR']
        self.use_s3 = app.config['USE_S3']
        self.aws_bucket = app.config['AWS_BUCKET'] if self.use_s3 else None
        self.liveness_threshold = app.config.get('LIVENESS_THRESHOLD', 0.8)
        self.texture_threshold = app.config.get('TEXTURE_THRESHOLD', 25.0)
        
        # Create faces directory if it doesn't exist
        os.makedirs(self.faces_dir, exist_ok=True)
        
        if self.use_s3:
            try:
                import boto3
                self.s3 = boto3.resource('s3')
            except ImportError:
                logger.error("boto3 is required for S3 storage but it's not installed")
                self.use_s3 = False
                
    def _get_embedding_path(self, ic_number):
        return os.path.join(self.faces_dir, f"{ic_number}.pkl")
    
    def _get_image_path(self, ic_number, img_index=0):
        return os.path.join(self.faces_dir, ic_number, f"{img_index}.jpg")
    
    def _save_local_embedding(self, embedding, ic_number):
        """Save face embedding to local file system"""
        embedding_path = self._get_embedding_path(ic_number)
        with open(embedding_path, 'wb') as f:
            pickle.dump(embedding, f)
        return embedding_path
    
    def _save_s3_embedding(self, embedding, ic_number):
        """Save face embedding to S3"""
        embedding_path = f"embeddings/{ic_number}.pkl"
        
        # Serialize the embedding
        pickle_bytes = pickle.dumps(embedding)
        
        # Upload to S3
        self.s3.Bucket(self.aws_bucket).put_object(
            Key=embedding_path,
            Body=pickle_bytes
        )
        return embedding_path
    
    def _load_local_embedding(self, ic_number):
        """Load face embedding from local file system"""
        embedding_path = self._get_embedding_path(ic_number)
        if not os.path.exists(embedding_path):
            return None
        
        with open(embedding_path, 'rb') as f:
            return pickle.load(f)
    
    def _load_s3_embedding(self, ic_number):
        """Load face embedding from S3"""
        embedding_path = f"embeddings/{ic_number}.pkl"
        
        try:
            # Download from S3
            obj = self.s3.Bucket(self.aws_bucket).Object(embedding_path).get()
            pickle_bytes = obj['Body'].read()
            
            # Deserialize the embedding
            return pickle.loads(pickle_bytes)
        except Exception as e:
            logger.error(f"Error loading embedding from S3: {str(e)}")
            return None
    
    def save_embedding(self, embedding, ic_number):
        """Save face embedding to storage (local or S3)"""
        if self.use_s3:
            return self._save_s3_embedding(embedding, ic_number)
        else:
            return self._save_local_embedding(embedding, ic_number)
    
    def load_embedding(self, ic_number):
        """Load face embedding from storage (local or S3)"""
        if self.use_s3:
            return self._load_s3_embedding(ic_number)
        else:
            return self._load_local_embedding(ic_number)
    
    def _save_local_image(self, img, ic_number, img_index=0):
        """Save face image to local file system"""
        # Create directory for this IC number if it doesn't exist
        ic_dir = os.path.join(self.faces_dir, ic_number)
        os.makedirs(ic_dir, exist_ok=True)
        
        # Save the image
        img_path = self._get_image_path(ic_number, img_index)
        img.save(img_path)
        return img_path
    
    def _save_s3_image(self, img, ic_number, img_index=0):
        """Save face image to S3"""
        img_path = f"images/{ic_number}/{img_index}.jpg"
        
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Upload to S3
        self.s3.Bucket(self.aws_bucket).put_object(
            Key=img_path,
            Body=img_byte_arr,
            ContentType='image/jpeg'
        )
        return img_path
    
    def save_image(self, img, ic_number, img_index=0):
        """Save face image to storage (local or S3)"""
        if self.use_s3:
            return self._save_s3_image(img, ic_number, img_index)
        else:
            return self._save_local_image(img, ic_number, img_index)
    
    def get_face_encoding(self, image):
        """Extract face encoding from image"""
        # Convert PIL Image to numpy array
        img_array = np.array(image)
        
        # Detect faces in the image
        face_locations = face_recognition.face_locations(img_array)
        
        if not face_locations:
            logger.warning("No faces detected in the image")
            return None, None
        
        # Use the first face found
        face_encodings = face_recognition.face_encodings(img_array, face_locations)
        
        if not face_encodings:
            logger.warning("Could not extract face encodings")
            return None, None
        
        return face_encodings[0], face_locations[0]
    
    def check_liveness(self, image, actions=None):
        """Check if the face is from a live person using action verification"""
        # This is a simplified implementation that assumes the actions were verified client-side
        # In a production environment, you'd implement more sophisticated checks
        if actions is not None and len(actions) > 0:
            # If actions were requested and completed, consider it live
            # The actual verification of actions would be more complex in production
            return True, "Liveness confirmed through action verification"
        
        # If no actions provided, perform basic anti-spoofing analysis
        return self.analyze_image_for_spoofing(image)
    
    def analyze_image_for_spoofing(self, image):
        """Analyze the image for signs of spoofing using texture analysis"""
        # Convert PIL Image to OpenCV format for analysis
        img_array = np.array(image)
        img_cv = img_array[:, :, ::-1].copy()  # RGB to BGR for OpenCV
        
        # Convert to grayscale for texture analysis
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Extract face location
        _, face_location = self.get_face_encoding(image)
        if face_location is None:
            return False, "No face detected for spoofing analysis"
        
        # Extract face region
        top, right, bottom, left = face_location
        face_region = gray[top:bottom, left:right]
        
        # Perform texture analysis (simplified)
        # Calculate local binary pattern or other texture features
        # Here we use a simple variance of laplacian for edge detection
        if face_region.size == 0:
            return False, "Invalid face region for analysis"
        
        # Calculate variance of laplacian for blur detection
        laplacian = cv2.Laplacian(face_region, cv2.CV_64F)
        var = laplacian.var()
        
        # Calculate local variance as a simple texture measure
        texture_score = variance(face_region)
        
        logger.info(f"Anti-spoofing scores: var_laplacian={var}, texture_score={texture_score}")
        
        # Check if the image is too blurry (potential printed photo)
        if var < 100:
            return False, "Image too blurry, possible spoofing attempt"
        
        # Check texture patterns (higher values typically indicate real faces)
        if texture_score < self.texture_threshold:
            return False, "Unusual texture patterns detected, possible spoofing attempt"
        
        return True, "Image passed anti-spoofing checks"
    
    def register_face(self, image, ic_number, actions=None):
        """Register a face with its IC number with anti-spoofing checks"""
        # First check liveness/anti-spoofing
        is_live, liveness_message = self.check_liveness(image, actions)
        if not is_live:
            return False, f"Anti-spoofing check failed: {liveness_message}"
        
        # Extract face encoding
        face_encoding, _ = self.get_face_encoding(image)
        
        if face_encoding is None:
            return False, "No face detected in the image"
        
        # Save face encoding
        try:
            self.save_embedding(face_encoding, ic_number)
            self.save_image(image, ic_number)
            logger.info(f"Face registered for IC: {ic_number}")
            return True, "Face registered successfully"
        except Exception as e:
            logger.error(f"Error registering face: {str(e)}")
            return False, f"Error registering face: {str(e)}"
    
    def verify_face(self, image, tolerance=0.6, actions=None):
        """Verify a face against registered faces with anti-spoofing"""
        # First check liveness/anti-spoofing
        is_live, liveness_message = self.check_liveness(image, actions)
        if not is_live:
            return False, None, f"Anti-spoofing check failed: {liveness_message}"
        
        # Extract face encoding
        face_encoding, _ = self.get_face_encoding(image)
        
        if face_encoding is None:
            return False, None, "No face detected in the image"
        
        # List all .pkl files in the faces directory
        if self.use_s3:
            # For S3, this would require listing objects, which is more complex
            # For simplicity, assume we have a list of registered ICs
            # In a real application, you'd maintain a database of registered users
            return False, None, "S3 verification not implemented yet"
        else:
            # List all .pkl files in local storage
            embeddings_path = Path(self.faces_dir)
            embedding_files = list(embeddings_path.glob("*.pkl"))
            
            if not embedding_files:
                return False, None, "No registered faces to compare with"
            
            # Compare with all registered faces
            best_match = None
            best_distance = float('inf')
            
            for embedding_file in embedding_files:
                ic_number = embedding_file.stem  # Get filename without extension
                stored_encoding = self.load_embedding(ic_number)
                
                if stored_encoding is not None:
                    # Calculate face distance
                    face_distances = face_recognition.face_distance([stored_encoding], face_encoding)
                    distance = face_distances[0]
                    
                    if distance < best_distance:
                        best_distance = distance
                        best_match = ic_number
            
            # Check if the best match is good enough
            if best_match and best_distance <= tolerance:
                logger.info(f"Face verified as IC: {best_match} (distance: {best_distance})")
                return True, best_match, f"Face verified successfully"
        
        # Check if the best match is good enough
        if best_match and best_distance <= tolerance:
            logger.info(f"Face verified as IC: {best_match} (distance: {best_distance})")
            return True, best_match, f"Face verified successfully"
        else:
            logger.info(f"Face verification failed. Best distance: {best_distance}")
            return False, None, "No matching face found"


def generate_liveness_challenge(self):
    """
    Generate a random liveness challenge sequence for facial authentication.
    
    This function creates a randomized sequence of actions that a user must perform
    to prove they are a real person (liveness detection) and not a photo or recording.
    
    Available actions:
    - blink: User must blink their eyes
    - smile: User must show a smiling expression
    - turn_head_left: User must turn their head to the left
    - turn_head_right: User must turn their head to the right
    - nod: User must nod their head up and down
    
    Returns:
        list: A list containing 1-2 randomly selected actions from the available actions list
    """
    # Define all possible liveness check actions
    actions = ["blink", "smile", "turn_head_left", "turn_head_right", "nod"]
    
    # Randomly select 1-2 actions to make the challenge unpredictable
    # This helps prevent replay attacks while keeping the process user-friendly
    num_actions = random.randint(1, 2)
    
    # Use random.sample to ensure no action is repeated
    selected_actions = random.sample(actions, num_actions)
    
    return selected_actions
