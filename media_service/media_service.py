import json
import os
import io
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile
from pydantic import BaseModel
from yt_dlp import YoutubeDL
from processingNote import extract_audio, split_audio_into_chunks, extract_frames
from video_to_noteNote import video_to_note
from transcriptionNote import transcribe, get_paths
from google.cloud import vision
import httpx

# FastAPI application
app = FastAPI()
router = APIRouter()

# Define base directory
BASE_DIR = os.path.abspath("./data")
os.makedirs(BASE_DIR, exist_ok=True)

# Environment for Google Vision API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./winter-school-444512-5268af394dd0.json"

# Define the VideoRequest model
class VideoRequest(BaseModel):
    url: str
    filename: str = None

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Media Service is running."}

# Utility to communicate with the indexing service
import mimetypes
from fastapi import UploadFile, HTTPException
import httpx

# Utility to communicate with the indexing service
async def ingest_file(file: UploadFile):
    """
    Ingests a file into the indexing service.

    Args:
        file (UploadFile): The file to ingest.

    Returns:
        dict: The response from the indexing service.

    Raises:
        HTTPException: If there is an error during the ingestion process.
    """
    try:
        # Reset the file pointer to ensure the file can be read from the start
        file.file.seek(0)

        # Determine MIME type explicitly based on file extension
        content_type = "text/plain"  # Default MIME type
        if file.filename.endswith(".md"):
            content_type = "text/markdown"
        elif file.filename.endswith(".pdf"):
            content_type = "application/pdf"

        # Prepare the file payload
        files = {
            "file": (file.filename, file.file, content_type)
        }

        # Log details for debugging
        print(f"Preparing to send file to indexing service: {files}")

        # Send the file to the indexing service
        async with httpx.AsyncClient(timeout=99) as client:
            response = await client.post(
                "http://indexing-service:8001/indexing/indexing/ingest",
                files=files,
                headers={"accept": "application/json"}
            )
            # Raise an exception for HTTP errors
            response.raise_for_status()

            # Log the successful response
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")

            # Return the response data
            return response.json()

    except httpx.HTTPStatusError as http_err:
        # Log HTTP errors
        print(f"HTTP error during file ingestion: {http_err}")
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"HTTP error during file ingestion: {http_err.response.text}"
        )

    except Exception as e:
        # Log general exceptions
        print(f"Error during file ingestion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with indexing service: {e}"
        )


# Endpoint to process and index videos
@router.post("/media/process-and-index")
async def process_and_index_video(request: VideoRequest):
    try:
        paths = get_paths(BASE_DIR, request.filename or "video_file")

        # Step 1: Download the video
        print(f"Downloading video to: {paths['video_path']}")
        ydl_opts = {"format": "best", "outtmpl": paths["video_path"]}
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([request.url])

        # Ensure video exists
        if not os.path.exists(paths["video_path"]):
            raise FileNotFoundError(f"Video file not found: {paths['video_path']}")
        print(f"Video downloaded successfully: {paths['video_path']}")

        # Step 2: Preprocess the video
        extract_audio(paths["video_path"], paths["audio_path"])
        split_audio_into_chunks(paths["audio_path"], paths["audio_chunk_dir"])
        extract_frames(paths["video_path"], paths["frames_dir"])
        print("Preprocessing completed.")

        # Step 3: Transcribe the video
        dataset_path = transcribe(BASE_DIR, request.filename or "video_file")
        print(f"Transcription completed successfully. Dataset saved to: {dataset_path}")

        # Step 4: Generate notes using `video_to_note`
        print(f"Generating notes for: {request.filename}")
        video_to_note_output = video_to_note(request.filename or "video_file")
        print("Video-to-note conversion completed successfully.")

        # Step 5: Locate the generated markdown files
        output_dir = os.path.join(BASE_DIR, f"{request.filename or 'video_file'}_output")
        markdown_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(".md")]

        if not markdown_files:
            raise FileNotFoundError(f"No markdown files generated in: {output_dir}")

        # Step 6: Index the content
        for markdown_file in markdown_files:
            with open(markdown_file, "rb") as file:
                upload_file = UploadFile(filename=markdown_file, file=file)
                indexing_response = await ingest_file(upload_file)
                print(f"Indexing response for {markdown_file}: {indexing_response}")

        return {
            "message": "Video processed, notes generated, and content indexed successfully.",
            "markdown_files": markdown_files
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error during video processing: {e}")


# Endpoint to process and index images
@router.post("/media/process-and-index-image")
async def process_and_index_image(file: UploadFile):
    try:
        print(f"Processing image: {file.filename}")
        image_path = os.path.join(BASE_DIR, file.filename)
        print(f"Saving image locally at: {image_path}")

        # Save the uploaded image locally
        with open(image_path, "wb") as img_file:
            img_file.write(await file.read())
        print(f"Image saved successfully: {image_path}")

        # Extract text using Google Vision API
        client = vision.ImageAnnotatorClient()
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        print(f"Google Vision API response received: {response}")

        if response.error.message:
            raise Exception(f"Vision API Error: {response.error.message}")

        texts = response.text_annotations
        extracted_text = texts[0].description if texts else "No text found."
        print(f"Extracted text: {extracted_text}")

        # Save extracted text to a file
        text_file_path = os.path.join(BASE_DIR, f"{os.path.splitext(file.filename)[0]}_text.txt")
        with open(text_file_path, "w", encoding="utf-8") as text_file:
            text_file.write(extracted_text)
        print(f"Text file created at: {text_file_path}")

        # Index the text file
# Index the text file
        try:
            with open(text_file_path, "rb") as file:
                print(f"Opening file for indexing: {text_file_path}")
                upload_file = UploadFile(filename=text_file_path, file=file)
                print(f"Prepared UploadFile: {upload_file.filename}")
                indexing_response = await ingest_file(upload_file)
                print(f"Indexing response: {indexing_response}")
        except Exception as e:
            print(f"Error during file ingestion: {e}")
            raise HTTPException(status_code=500, detail=f"Error during file ingestion: {e}")


        return {
            "message": "Image processed and content indexed successfully.",
            "text_file": text_file_path,
            "indexing_response": indexing_response,
        }
    except Exception as e:
        print(f"Error during image processing: {e}")
        raise HTTPException(status_code=500, detail=f"Error during image processing: {e}")


# Mount the router to the FastAPI application
# FastAPI application
app.include_router(router, prefix="/media", tags=["Media"])
