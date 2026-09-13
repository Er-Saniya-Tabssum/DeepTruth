# DeepTruth — AI-Generated Image & Deepfake Detection Platform

DeepTruth is an AI-powered media forensics platform designed to analyze images and identify whether they are likely to be **AI-generated, manipulated, or authentic**.

The platform provides a web-based interface where users can upload an image, submit it for analysis, and receive an AI-generated prediction along with confidence information and analysis status.

DeepTruth is built using a modern full-stack architecture with a React frontend, FastAPI backend, asynchronous background workers, database-backed analysis tracking, and machine-learning inference providers.

---

## Table of Contents

* [Project Overview](#project-overview)
* [Problem Statement](#problem-statement)
* [Key Features](#key-features)
* [How DeepTruth Works](#how-deeptruth-works)
* [System Architecture](#system-architecture)
* [Project Workflow](#project-workflow)
* [Technology Stack](#technology-stack)
* [Project Structure](#project-structure)
* [Machine Learning Models](#machine-learning-models)
* [Inference Providers](#inference-providers)
* [Backend Architecture](#backend-architecture)
* [Frontend Architecture](#frontend-architecture)
* [Database and Migrations](#database-and-migrations)
* [API Overview](#api-overview)
* [Local Installation](#local-installation)
* [Environment Configuration](#environment-configuration)
* [Running the Project](#running-the-project)
* [Testing the Application](#testing-the-application)
* [Docker Support](#docker-support)
* [Deployment Considerations](#deployment-considerations)
* [Security Considerations](#security-considerations)
* [Limitations](#limitations)
* [Future Improvements](#future-improvements)
* [Learning Outcomes](#learning-outcomes)
* [License](#license)

---

## Project Overview

DeepTruth helps users analyze digital images and understand whether the content may have been generated or manipulated using artificial intelligence.

With the growth of generative AI tools, it has become increasingly difficult to distinguish between:

* Real photographs
* AI-generated images
* Deepfake images
* Face-swapped images
* Digitally manipulated images
* Images modified using generative editing tools

DeepTruth provides a centralized platform for image analysis by combining:

1. Image upload
2. Backend validation
3. Asynchronous analysis processing
4. Machine-learning inference
5. Result storage
6. Result retrieval through APIs
7. User-friendly frontend visualization

The application separates the web request layer from the machine-learning processing layer. This makes the system more scalable and prevents long-running inference tasks from blocking the API server.

---

## Problem Statement

AI-generated and manipulated images are becoming more realistic. Traditional visual inspection is often insufficient to identify whether an image is authentic.

Users, content moderators, journalists, researchers, and digital investigators may need to answer questions such as:

* Is this image AI-generated?
* Is this image likely to be real?
* Has this image been manipulated?
* How confident is the model in its prediction?
* When was the image analyzed?
* What model was used for the analysis?

DeepTruth attempts to solve this problem by providing an automated image-analysis workflow.

The platform does not claim to provide absolute proof of authenticity. Instead, it provides a machine-learning-based prediction that should be interpreted as an analytical signal.

---

## Key Features

### 1. Image Upload

Users can upload an image through the React-based frontend.

The backend validates the uploaded file before accepting it for analysis.

Supported image formats depend on the configured backend validation and image-processing libraries.

Typical supported formats include:

* JPG
* JPEG
* PNG
* WEBP

---

### 2. Asynchronous Image Analysis

Image analysis can be computationally expensive, especially when machine-learning models are involved.

Instead of processing the image completely inside the upload request, DeepTruth uses a background worker architecture.

The workflow is:

1. User uploads an image.
2. Backend stores the image.
3. Backend creates an analysis record.
4. Backend returns an analysis ID.
5. Worker picks up the pending analysis.
6. Worker executes the selected inference provider.
7. Worker stores the prediction.
8. Frontend retrieves and displays the result.

This architecture improves responsiveness and allows the worker to process tasks independently.

---

### 3. Analysis Status Tracking

Each analysis moves through different states.

Typical states include:

* `PENDING`
* `PROCESSING`
* `COMPLETED`
* `FAILED`

The frontend can use the analysis ID to check the current status of the job.

---

### 4. Multiple Inference Providers

DeepTruth supports different inference providers.

The current architecture allows the application to switch between:

* A production-style Hugging Face image detector
* The project's original custom Keras CNN model

This provider-based design makes the machine-learning layer replaceable and easier to extend.

---

### 5. Model Selection

The analysis request can specify which model provider should be used.

For example:

* Production detector
* Original custom CNN model

This makes it possible to compare different models and evaluate their predictions.

---

### 6. Database-Backed Results

DeepTruth stores analysis information in a database.

The database can contain:

* Analysis ID
* Uploaded file information
* Analysis status
* Selected model provider
* Prediction result
* Confidence score
* Error information
* Creation timestamp
* Completion timestamp

Database migrations are managed using Alembic.

---

### 7. React Frontend

The frontend provides a simple interface for:

* Uploading images
* Starting analysis
* Tracking analysis status
* Displaying model results
* Showing errors and processing states

The frontend is built with React and Vite.

---

### 8. FastAPI Backend

The backend is built using FastAPI.

FastAPI provides:

* REST APIs
* Request validation
* File upload handling
* API documentation
* CORS configuration
* Integration with database services
* Integration with background workers

---

## How DeepTruth Works

At a high level, DeepTruth follows this process:

```text
User
 |
 | Upload Image
 v
React Frontend
 |
 | HTTP API Request
 v
FastAPI Backend
 |
 | Validate and Store Image
 v
Database
 |
 | Create Pending Analysis
 v
Background Worker
 |
 | Select Inference Provider
 v
Machine Learning Model
 |
 | Generate Prediction
 v
Database
 |
 | Return Result
 v
React Frontend
 |
 v
User Sees Analysis Result
```

---

## System Architecture

```text
+-----------------------------+
|        React Frontend       |
|       Vite + TypeScript     |
+-------------+---------------+
              |
              | REST API
              v
+-----------------------------+
|        FastAPI Backend      |
|                             |
| - Upload API                |
| - Analysis API              |
| - Validation                |
| - Database Operations       |
| - Job Creation              |
+-------------+---------------+
              |
              +----------------------+
              |                      |
              v                      v
+----------------------+   +----------------------+
|      Database        |   |   Background Worker   |
|                      |   |                      |
| - Analysis Records   |   | - Fetch Pending Jobs |
| - Status             |   | - Run Model          |
| - Predictions        |   | - Save Results       |
+----------------------+   +----------+-----------+
                                     |
                                     v
                           +----------------------+
                           | Inference Provider   |
                           +----------+-----------+
                                      |
                     +----------------+----------------+
                     |                                 |
                     v                                 v
          +----------------------+          +----------------------+
          | Hugging Face Model   |          | Original Keras CNN   |
          | Production Provider  |          | Experimental Provider|
          +----------------------+          +----------------------+
```

---

## Project Workflow

### Step 1: User Uploads an Image

The user selects an image from the frontend.

The frontend sends the image to the backend using a multipart HTTP request.

---

### Step 2: Backend Validates the Image

The backend checks:

* Whether a file was provided
* Whether the file type is allowed
* Whether the file can be processed
* Whether the upload satisfies configured limits

Invalid files are rejected before analysis.

---

### Step 3: Image is Stored

The backend stores the uploaded image in the configured upload directory.

The database stores metadata about the image and its analysis request.

---

### Step 4: Analysis Job is Created

The backend creates an analysis record with an initial status such as:

```text
PENDING
```

The API returns an analysis identifier.

The frontend uses this identifier to track progress.

---

### Step 5: Worker Picks Up the Job

The background worker continuously checks for pending analysis jobs.

When it finds a job, it changes the status to:

```text
PROCESSING
```

The worker then loads the required image and selected model provider.

---

### Step 6: Model Performs Inference

The selected model analyzes the image.

The model may produce:

* Predicted class
* Probability
* Confidence score
* Label
* Additional model metadata

The exact meaning of the result depends on the model and its training.

---

### Step 7: Result is Stored

The worker saves the prediction in the database.

If processing succeeds, the status becomes:

```text
COMPLETED
```

If an exception occurs, the status becomes:

```text
FAILED
```

The error information can be stored for debugging and user feedback.

---

### Step 8: Frontend Displays the Result

The frontend retrieves the latest analysis information and displays:

* Analysis status
* Prediction
* Confidence
* Selected model
* Error details, if any

---

## Technology Stack

### Frontend

| Technology       | Purpose                                    |
| ---------------- | ------------------------------------------ |
| React            | Building the user interface                |
| TypeScript       | Type-safe frontend development             |
| Vite             | Frontend development server and build tool |
| CSS              | Styling and layout                         |
| Fetch/API Client | Communication with FastAPI backend         |

---

### Backend

| Technology    | Purpose                                    |
| ------------- | ------------------------------------------ |
| Python        | Main backend and ML programming language   |
| FastAPI       | REST API framework                         |
| Uvicorn       | ASGI application server                    |
| Pydantic      | Request and response validation            |
| SQLAlchemy    | Database interaction                       |
| Alembic       | Database migrations                        |
| Python-dotenv | Environment variable loading               |
| Pillow/OpenCV | Image processing                           |
| Requests      | Communication with external model services |

---

### Machine Learning

| Technology       | Purpose                                  |
| ---------------- | ---------------------------------------- |
| TensorFlow/Keras | Loading and running the custom CNN model |
| Hugging Face     | Accessing image detection models         |
| NumPy            | Numerical operations                     |
| PIL/OpenCV       | Image preprocessing                      |

---

### Database

The project supports database-backed analysis tracking.

For local development, SQLite can be used.

For production, a managed PostgreSQL database is recommended.

---

### DevOps and Deployment

| Technology     | Purpose                            |
| -------------- | ---------------------------------- |
| Git            | Version control                    |
| GitHub         | Source-code hosting                |
| Docker         | Containerization                   |
| Docker Compose | Running multiple services locally  |
| Nginx          | Serving the frontend in production |
| Alembic        | Database schema management         |

---

## Project Structure

```text
DeepTruth/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── worker_runner.py
│   │   ├── worker.py
│   │   ├── inference.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── config.py
│   │   └── ...
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.ts
│   ├── nginx.conf
│   └── Dockerfile
│
├── migrations/
│   └── versions/
│
├── models/
│   └── custom_cnn/
│       └── deeptruth_cnn.h5
│
├── uploads/
│
├── alembic.ini
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Machine Learning Models

DeepTruth supports multiple model implementations.

### 1. Hugging Face Image Detector

The Hugging Face provider uses a pre-trained image-detection model.

This provider is intended to be the main production-style inference option.

Advantages:

* Uses a pre-trained model
* Easier to replace or upgrade
* Can be hosted separately
* Avoids committing large model files to GitHub
* Can be integrated with external inference services

The configured model is:

```text
capcheck/ai-image-detection
```

The model's output should be interpreted according to the model's own labels and documentation.

---

### 2. Original Keras CNN Model

The project also contains the original custom Keras CNN model:

```text
models/custom_cnn/deeptruth_cnn.h5
```

This model is loaded using TensorFlow/Keras.

The original CNN provider is useful for:

* Experimental testing
* Comparing model outputs
* Studying custom model integration
* Understanding local inference
* Future model evaluation

The custom model should be treated carefully because the meaning of its labels depends on the dataset and training configuration.

A model prediction is not automatically proof that an image is fake or real.

---

## Inference Providers

DeepTruth uses a provider-based inference architecture.

Instead of tightly coupling the worker to one model, the worker selects an inference provider.

Conceptually:

```python
provider = create_inference_provider(model_provider)
result = provider.predict(image_path)
```

This design provides several benefits:

* Easy model replacement
* Cleaner code organization
* Better testing
* Easier experimentation
* Support for multiple model backends
* Reduced coupling between worker and model implementation

### Supported Provider Types

#### Production Provider

```text
PRODUCTION
```

Uses the Hugging Face image detector.

#### Custom Model Provider

```text
MY_MODEL
```

Uses the original Keras CNN model.

---

## Backend Architecture

### FastAPI Application

The FastAPI application is responsible for:

* Starting the web server
* Registering API routes
* Handling upload requests
* Validating request data
* Creating analysis jobs
* Returning analysis status
* Returning analysis results
* Configuring CORS

The application is started using Uvicorn.

---

### Worker Runner

The worker runner starts the background processing system.

Run it using:

```powershell
python -m backend.app.worker_runner
```

The worker is responsible for:

1. Fetching pending jobs
2. Updating job status
3. Loading the image
4. Selecting the model provider
5. Running inference
6. Saving results
7. Handling failures

The worker should run in a separate terminal or separate production service.

---

### Database Layer

The database layer manages:

* Database connection
* Sessions
* Analysis records
* Model selection
* Prediction storage
* Status updates

SQLAlchemy is used to interact with the database.

---

### Migration Layer

Alembic manages database schema changes.

Useful commands:

```powershell
alembic -c ".\alembic.ini" current
```

Show migration heads:

```powershell
alembic -c ".\alembic.ini" heads
```

Apply migrations:

```powershell
alembic -c ".\alembic.ini" upgrade head
```

---

## Frontend Architecture

The frontend is built using React and Vite.

Its responsibilities include:

* Rendering the user interface
* Handling image selection
* Sending upload requests
* Displaying loading states
* Polling or retrieving analysis status
* Showing the final prediction
* Displaying backend errors

The frontend communicates with the backend through the configured API base URL.

Example environment variable:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Database and Migrations

During development, SQLite can be used because it is simple and requires no separate database server.

For production, PostgreSQL is recommended because it provides:

* Better concurrency
* Stronger reliability
* Better scalability
* Production-grade database management
* Compatibility with managed hosting services

Before starting the backend, run:

```powershell
alembic -c ".\alembic.ini" upgrade head
```

The project currently uses Alembic migrations to maintain database schema consistency.

---

## API Overview

The exact routes may depend on the current backend implementation.

The main API responsibilities are:

### Health Check

Used to verify whether the backend is running.

Example:

```http
GET /health
```

---

### Image Upload

Used to upload an image for analysis.

Example concept:

```http
POST /analyses
Content-Type: multipart/form-data
```

The request may include:

* Image file
* Model provider
* User consent or analysis options

---

### Analysis Status

Used to retrieve the current state of an analysis.

Example concept:

```http
GET /analyses/{analysis_id}
```

Possible response states:

```text
PENDING
PROCESSING
COMPLETED
FAILED
```

---

### Analysis Result

The result may include information such as:

```json
{
  "analysis_id": "example-id",
  "status": "COMPLETED",
  "prediction": "AI_GENERATED",
  "confidence": 0.92,
  "model_provider": "PRODUCTION"
}
```

The actual response fields depend on the current backend schema.

---

## Local Installation

### Prerequisites

Install the following software:

* Python 3.11 or compatible Python version
* Node.js
* npm
* Git
* Optional: Docker Desktop
* Optional: PostgreSQL for production-like development

---

### Clone the Repository

```powershell
git clone https://github.com/YOUR_USERNAME/DeepTruth.git
cd DeepTruth
```

---

## Backend Setup

### 1. Create a Virtual Environment

```powershell
python -m venv .venv
```

---

### 2. Activate the Virtual Environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run PowerShell as an appropriate user and configure the execution policy according to your system policy.

---

### 3. Install Backend Dependencies

```powershell
pip install --upgrade pip
pip install -r backend/requirements.txt
```

---

### 4. Create Environment File

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and update the required values.

---

### 5. Run Database Migrations

```powershell
alembic -c ".\alembic.ini" upgrade head
```

---

## Frontend Setup

Open a separate terminal.

Move into the frontend directory:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

---

## Environment Configuration

Create a `.env` file in the project root.

Example:

```env
# Application
APP_ENV=development
DEEPTRUTH_MODE=real

# Backend
HOST=127.0.0.1
PORT=8000

# Database
DATABASE_URL=sqlite:///./dev.db

# Security
SECRET_KEY=replace-this-with-a-long-random-secret

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Inference
INFERENCE_MODE=REAL
MODEL_PROVIDER=PRODUCTION
MODEL_ID=capcheck/ai-image-detection
MODEL_PATH=.\models\custom_cnn\deeptruth_cnn.h5
MODEL_DEVICE=auto
```

Do not commit the real `.env` file to GitHub.

---

## Running the Project

DeepTruth requires multiple processes during local development.

### Terminal 1: Start the Backend

From the project root:

```powershell
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend should be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation is usually available at:

```text
http://127.0.0.1:8000/docs
```

---

### Terminal 2: Start the Worker

Activate the virtual environment if required:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run:

```powershell
python -m backend.app.worker_runner
```

Keep this terminal running because the worker processes uploaded analysis jobs.

---

### Terminal 3: Start the Frontend

Move to the frontend directory:

```powershell
cd frontend
```

Run:

```powershell
npm run dev
```

The frontend should be available at:

```text
http://localhost:3000/
```

---

## Testing the Application

### 1. Open the Frontend

Open:

```text
http://localhost:3000/
```

---

### 2. Upload an Image

Select a valid image from your computer.

---

### 3. Submit the Image

Start the analysis from the frontend.

---

### 4. Check the Backend

The backend terminal should show the incoming request.

---

### 5. Check the Worker

The worker terminal should show that it picked up the pending job.

---

### 6. View the Result

After inference completes, the frontend should display the analysis result.

---

## Useful Development Commands

### Check Git Status

```powershell
git status
```

---

### Start Backend

```powershell
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

---

### Start Worker

```powershell
python -m backend.app.worker_runner
```

---

### Start Frontend

```powershell
cd frontend
npm run dev
```

---

### Build Frontend

```powershell
cd frontend
npm run build
```

---

### Run Frontend Preview

```powershell
cd frontend
npm run preview
```

---

### Check Database Migration

```powershell
alembic -c ".\alembic.ini" current
```

---

### Apply Database Migration

```powershell
alembic -c ".\alembic.ini" upgrade head
```

---

## Docker Support

DeepTruth contains Docker configuration for the backend and frontend.

### Build and Start Services

From the project root:

```powershell
docker compose up --build
```

The backend and frontend containers can be started using Docker Compose.

---

### Stop Services

```powershell
docker compose down
```

---

### Rebuild Services

```powershell
docker compose build --no-cache
```

---

### Important Docker Note

The current Docker configuration is primarily suitable for development and initial experimentation.

Before production deployment, update:

* Secret keys
* CORS origins
* Database configuration
* Model configuration
* Upload storage
* Worker process configuration
* Health checks
* Logging
* Resource limits

---

## Deployment Considerations

DeepTruth contains machine-learning inference and background processing. Therefore, deployment requires more than simply hosting the frontend.

### Frontend Deployment

The React frontend can be built using:

```powershell
npm run build
```

The generated files are placed in the `dist` directory.

The frontend can be served using:

* Nginx
* Docker
* Static hosting platforms
* Cloud storage hosting
* CDN-based hosting

---

### Backend Deployment

The FastAPI backend can be started using:

```powershell
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

For production, use:

* A production ASGI server configuration
* HTTPS
* Environment-based configuration
* Proper CORS settings
* Managed database
* Centralized logs

---

### Worker Deployment

The worker must run continuously.

Starting only the FastAPI backend is not enough because the worker is responsible for processing analysis jobs.

The worker should be deployed as:

* A separate service
* A separate container
* A background process
* A dedicated worker instance

Example:

```powershell
python -m backend.app.worker_runner
```

---

### Database Deployment

SQLite is suitable for local development but is not ideal for production workloads.

For production, use PostgreSQL or another managed database.

---

### File Storage

Uploaded files should not depend only on a temporary local filesystem.

Production deployments should use persistent storage such as:

* S3-compatible object storage
* Cloud storage buckets
* Persistent volumes
* Managed file storage

---

### Model Deployment

The custom model file:

```text
deeptruth_cnn.h5
```

is large and should not normally be committed directly to GitHub.

The `.gitignore` file excludes large model files such as:

```text
*.h5
*.pt
*.pth
*.onnx
```

Production alternatives include:

* Downloading the model during deployment
* Mounting the model through persistent storage
* Hosting the model separately
* Using a Hugging Face model
* Using a model registry
* Using an object-storage bucket

---

## Security Considerations

### 1. Do Not Commit Secrets

Never commit:

* `.env`
* API keys
* Database passwords
* Secret keys
* Access tokens
* Cloud credentials

Use `.env.example` for safe configuration templates.

---

### 2. Validate Uploaded Files

Uploaded files should be checked for:

* File extension
* MIME type
* File size
* Valid image format
* Malicious or malformed content

---

### 3. Limit Upload Size

Large uploads can consume server resources.

The backend should enforce reasonable file-size limits.

---

### 4. Configure CORS Carefully

During development, localhost origins may be allowed.

In production, only trusted frontend domains should be allowed.

---

### 5. Protect Analysis Data

Analysis records and uploaded images may contain sensitive information.

Production systems should consider:

* Authentication
* Authorization
* Data retention policies
* Secure file access
* Encryption
* Audit logs

---

### 6. Do Not Treat Predictions as Absolute Truth

AI detectors can produce:

* False positives
* False negatives
* Incorrect confidence values
* Different results for unseen image types

The application should clearly communicate that predictions are probabilistic.

---

## Limitations

DeepTruth is an AI-assisted detection platform and has several limitations.

### Model Accuracy

The model may not correctly identify every AI-generated or manipulated image.

---

### Dataset Bias

Model performance depends on the data used during training.

If the training data does not represent modern generation techniques, performance may decrease.

---

### New Generation Models

Generative AI technology evolves quickly.

A detector trained on older images may struggle with images created by newer models.

---

### Image Compression

Compression, resizing, screenshots, and social-media processing can affect model predictions.

---

### False Positives and False Negatives

A real image may be classified as AI-generated.

An AI-generated image may be classified as real.

---

### Experimental Custom CNN

The original Keras CNN model should be considered experimental until it has been evaluated on a reliable and representative validation dataset.

---

## Future Improvements

### 1. User Authentication

Add:

* Signup
* Login
* JWT authentication
* Role-based access
* User-specific analysis history

---

### 2. Better Model Evaluation

Add:

* Accuracy
* Precision
* Recall
* F1-score
* ROC-AUC
* Confusion matrix
* Benchmark datasets

---

### 3. Explainable AI

Provide explanations such as:

* Important image regions
* Heatmaps
* Grad-CAM visualizations
* Model reasoning indicators
* Artifact analysis

---

### 4. Video Deepfake Detection

Extend the platform to support:

* Video uploads
* Frame extraction
* Face detection
* Frame-level predictions
* Temporal consistency analysis
* Audio-video synchronization analysis

---

### 5. Face-Swap Detection

Add specialized face manipulation detection for:

* Face swaps
* Face reenactment
* Face morphing
* Synthetic identities

---

### 6. Advanced Image Forensics

Add:

* Metadata extraction
* EXIF analysis
* Error-level analysis
* JPEG quantization analysis
* Noise pattern analysis
* Compression artifact analysis
* Reverse image search integration

---

### 7. Scalable Job Queue

Replace the basic worker mechanism with:

* Redis
* Celery
* RQ
* RabbitMQ
* Kafka

This would support higher workloads and better job management.

---

### 8. Cloud Storage

Use object storage for:

* Uploaded images
* Processed images
* Model files
* Analysis reports

---

### 9. Production Monitoring

Add:

* Structured logs
* Error tracking
* Metrics
* Health checks
* Model latency tracking
* Worker failure monitoring
* Database monitoring

---

### 10. Model Versioning

Store:

* Model name
* Model version
* Provider
* Inference timestamp
* Prediction
* Confidence
* Preprocessing version

This improves reproducibility and auditability.

---

## Learning Outcomes

This project demonstrates practical knowledge of:

* Full-stack web development
* React application development
* TypeScript
* REST API design
* FastAPI
* Python backend development
* File upload handling
* Asynchronous job processing
* Background workers
* SQLAlchemy
* Database migrations
* Alembic
* TensorFlow/Keras
* Hugging Face model integration
* Image preprocessing
* Machine-learning inference
* Docker
* Nginx
* Git and GitHub
* Environment configuration
* Production deployment planning
* AI model limitations
* Software architecture

---

## Why This Project Is Important

DeepTruth combines software engineering and artificial intelligence in a real-world application.

It demonstrates how to build a complete AI product rather than only training a model in a notebook.

The project includes:

* User interface
* Backend APIs
* Database
* Background processing
* Machine-learning inference
* Model provider abstraction
* Deployment configuration
* Security and scalability considerations

This makes DeepTruth a practical demonstration of full-stack engineering, backend development, machine learning integration, and system design.

---

## Important Disclaimer

DeepTruth provides AI-based predictions and should not be considered a definitive authenticity verification system.

The results may be affected by:

* Image quality
* Compression
* Model limitations
* Dataset bias
* New generation techniques
* Image transformations

The output should be used as an analytical aid and not as the sole basis for legal, financial, journalistic, or other high-impact decisions.

---

## License

This project is intended for educational, research, and experimental purposes.

Add an appropriate open-source license before publicly distributing the project.

For example:

* MIT License
* Apache License 2.0
* GNU GPLv3
