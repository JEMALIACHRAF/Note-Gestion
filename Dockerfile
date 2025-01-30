# Use the base image
FROM python-service-base:latest

# Set working directory
WORKDIR /app

# Copy all required files
COPY ./main.py ./main.py
COPY ./indexing_service/indexing_service.py ./indexing_service/indexing_service.py
COPY ./media_service/media_service.py ./media_service/media_service.py
COPY ./chat_agent_service/chat_agent_service.py ./chat_agent_service/chat_agent_service.py
COPY ./shared ./shared
COPY ./Explication.pdf ./Explication.pdf
COPY ./winter-school-444512-5268af394dd0.json ./winter-school-444512-5268af394dd0.json              
COPY ./processingNote.py ./processingNote.py
COPY ./video_to_noteNote.py ./video_to_noteNote.py
COPY ./transcriptionNote.py ./transcriptionNote.py
# Set the Google application credentials environment variable
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/winter-school-444512-5268af394dd0.json
# Expose the default port
EXPOSE 8000

# Command to run the main application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
