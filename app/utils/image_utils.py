import base64
import io
import re
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def base64_to_image(base64_string):
    """
    Convert a base64 encoded image string to a PIL Image object
    
    Args:
        base64_string (str): Base64 encoded image string, may include the data URL prefix
        
    Returns:
        PIL.Image: The decoded image, or None if conversion fails
    """
    try:
        # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]
        
        # Decode base64 string
        image_data = base64.b64decode(base64_string)
        
        # Create PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        return image
    except Exception as e:
        logger.error(f"Error converting base64 to image: {str(e)}")
        return None

def image_to_base64(image, format='JPEG'):
    """
    Convert a PIL Image object to a base64 encoded string
    
    Args:
        image (PIL.Image): The image to convert
        format (str): Image format (default: JPEG)
        
    Returns:
        str: Base64 encoded image string with data URL prefix
    """
    try:
        # Save image to bytes buffer
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        
        # Encode bytes to base64
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Add data URL prefix
        mime_type = f"image/{format.lower()}"
        data_url = f"data:{mime_type};base64,{img_str}"
        
        return data_url
    except Exception as e:
        logger.error(f"Error converting image to base64: {str(e)}")
        return None
