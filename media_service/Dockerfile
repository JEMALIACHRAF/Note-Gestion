# Use the custom base image
FROM python-service-base:latest

# Install FFmpeg and other system dependencies
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy service-specific files
COPY media_service/media_service.py ./media_service.py
COPY processingNote.py ./processingNote.py
COPY video_to_noteNote.py ./video_to_noteNote.py
COPY transcriptionNote.py ./transcriptionNote.py
COPY shared/vector_index_utils.py ./shared/vector_index_utils.py
COPY Explication.pdf ./Explication.pdf
COPY winter-school-444512-5268af394dd0.json ./winter-school-444512-5268af394dd0.json              

# Set the Google application credentials environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/winter-school-444512-5268af394dd0.json

# Install curl
RUN apt-get update && apt-get install -y curl

# Copy the requirements file
COPY media_service/requirements.txt ./requirements.txt
# Install Python dependencies
RUN pip install -r requirements.txt


# Expose the service's port
EXPOSE 8002

# Run the service
CMD ["uvicorn", "media_service:app", "--host", "0.0.0.0", "--port", "8002"]
