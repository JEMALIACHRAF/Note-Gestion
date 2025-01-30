# Use the custom base image
FROM python-service-base:latest

# Set the working directory
WORKDIR /app

# Copy service-specific files
COPY chat_agent_service/chat_agent_service.py ./chat_agent_service.py
COPY shared/vector_index_utils.py ./shared/vector_index_utils.py

# Copy Explication.pdf
COPY Explication.pdf ./Explication.pdf

# Copy and install dependencies
COPY chat_agent_service/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt



# Expose the service's port
EXPOSE 8003

# Run the service
CMD ["uvicorn", "chat_agent_service:app", "--host", "0.0.0.0", "--port", "8003"]
