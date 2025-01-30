# Use the custom base image
FROM python-service-base:latest

# Set the working directory
WORKDIR /app

# Copy service-specific files
COPY indexing_service/indexing_service.py ./indexing_service.py
COPY shared/vector_index_utils.py ./shared/vector_index_utils.py
COPY Explication.pdf ./Explication.pdf

# Copy and install dependencies
COPY indexing_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt 



# Expose the service's port
EXPOSE 8001

# Run the service
CMD ["uvicorn", "indexing_service:app", "--host", "0.0.0.0", "--port", "8001"]
