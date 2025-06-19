# Face Recognition Verification App

A Flask-based face recognition verification application that allows users to register faces and verify identities using a webcam.

## Features

- **Face Registration**: Register faces using IC numbers as identifiers
- **Face Verification**: Verify identities using webcam captures
- **Local Storage Mode**: Store face data locally by default
- **AWS S3 Support**: Option to use AWS S3 for storage
- **Responsive UI**: Modern Bootstrap-based interface with webcam integration

## Prerequisites

- Python 3.8 or higher
- Flask
- face_recognition library
- OpenCV
- Docker (optional, for containerized deployment)

## Installation

### Local Development

1. Clone the repository:
   ```
   git clone <repository-url>
   cd face_recognition
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Configure the application by editing the `.env` file:
   ```
   SECRET_KEY=your-secret-key
   USE_S3=false
   AWS_BUCKET=your-s3-bucket-name
   FACES_DIR=./faces
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Access the application in your browser at `http://localhost:2020`

### Docker Deployment

1. Build and start the Docker container:
   ```
   docker-compose up -d
   ```

2. Access the application in your browser at `http://localhost:2020`

## Usage

### Face Registration

1. Navigate to the Register page
2. Enter a valid 12-digit IC number
3. Position your face in the webcam frame
4. Click "Capture and Register"
5. The system will save your face embedding for future verification

### Face Verification

1. Navigate to the Verify page
2. Position your face in the webcam frame
3. Click "Capture and Verify"
4. The system will attempt to match your face with registered faces
5. Results will be displayed on the screen

## Directory Structure

```
face_recognition/
├── app/
│   ├── routes/          # API and view routes
│   ├── services/        # Business logic for face recognition
│   ├── static/          # CSS, JS, and images
│   ├── templates/       # HTML templates
│   └── utils/           # Utility functions
├── faces/               # Storage for face images and embeddings
├── .env                 # Environment configuration
├── app.py               # Application entry point
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
└── requirements.txt     # Python dependencies
```

## Configuration

The application can be configured using environment variables in the `.env` file:

- `SECRET_KEY`: Flask secret key for session security
- `USE_S3`: Set to "true" to use AWS S3 storage, "false" for local storage
- `AWS_BUCKET`: S3 bucket name (when USE_S3 is true)
- `FACES_DIR`: Directory for storing face data locally

## Security Considerations

- In production, ensure you set a strong SECRET_KEY
- For S3 storage, use IAM roles or environment variables for AWS credentials
- Consider implementing user authentication for the registration page
- This application stores biometric data - ensure compliance with relevant privacy regulations

## API Documentation

The application provides RESTful API endpoints for programmatic interaction with the face recognition system.

### API Endpoints

#### 1. Face Verification API

**Endpoint:** `/api/verify`

**Method:** POST

**Description:** Verifies a face against registered faces in the system.

**Request Body:**
```json
{
  "image_data": "base64_encoded_image_string"
}
```

**Response:**
```json
{
  "success": true,            // Whether the API call was successful
  "matched": true,            // Whether the face matched a registered face
  "ic_number": "123456789012", // IC number of the matched face, or null if no match
  "message": "Face verified successfully"
}
```

**Example using curl:**
```bash
curl -X POST http://localhost:2020/api/verify \
  -H "Content-Type: application/json" \
  -d '{"image_data": "data:image/jpeg;base64,/9j/4AAQ..."}'  # truncated for brevity
```

#### 2. Face Registration API

**Endpoint:** `/api/register`

**Method:** POST

**Description:** Registers a face with an IC number in the system.

**Request Body:**
```json
{
  "image_data": "base64_encoded_image_string",
  "ic_number": "123456789012"
}
```

**Response:**
```json
{
  "success": true,  // Whether the registration was successful
  "message": "Face registered successfully"
}
```

**Example using curl:**
```bash
curl -X POST http://localhost:2020/api/register \
  -H "Content-Type: application/json" \
  -d '{"image_data": "data:image/jpeg;base64,/9j/4AAQ...", "ic_number": "123456789012"}'  # truncated for brevity
```

### Error Responses

Both API endpoints return error responses in the following format when something goes wrong:

```json
{
  "success": false,
  "message": "Error message describing what went wrong"
}
```

Common error scenarios include:
- Missing or invalid parameters
- Invalid image data
- No face detected in the image
- Server errors during processing
