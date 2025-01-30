from fastapi import FastAPI, APIRouter, UploadFile, HTTPException
from shared.vector_index_utils import get_or_create_index
from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.schema import Document
import os
import logging
import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

vector_index = None  # Global vector index


def save_file_locally(file: UploadFile) -> str:
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    counter = 1
    while os.path.exists(file_path):
        file_path = os.path.join(
            UPLOAD_DIR,
            f"{os.path.splitext(file.filename)[0]}_{counter}{os.path.splitext(file.filename)[1]}"
        )
        counter += 1
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_path


def get_file_metadata(file_path: str) -> dict:
    return {
        "file_name": os.path.basename(file_path),
        "file_path": file_path,
        "file_type": f"application/{os.path.splitext(file_path)[1][1:]}",
        "file_size": os.path.getsize(file_path),
        "creation_date": datetime.datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d"),
        "last_modified_date": datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d"),
    }


def process_pdf(file_path: str):
    docs = SimpleDirectoryReader(input_files=[file_path]).load_data()
    metadata = get_file_metadata(file_path)
    return [Document(text=doc.text, metadata=metadata) for doc in docs]


def process_text_or_markdown(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    metadata = get_file_metadata(file_path)
    return [Document(text=content, metadata=metadata)]


@router.post("/indexing/ingest")
async def ingest_file(file: UploadFile):
    global vector_index
    try:
        allowed_extensions = [".pdf", ".txt", ".md"]
        file_extension = os.path.splitext(file.filename)[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}. Allowed types: {', '.join(allowed_extensions)}",
            )

        file_path = save_file_locally(file)
        logger.info(f"File saved locally at {file_path}")

        if file_extension == ".pdf":
            docs = process_pdf(file_path)
        elif file_extension in [".txt", ".md"]:
            docs = process_text_or_markdown(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        logger.info(f"Loaded {len(docs)} document(s) from {file.filename}")

        vector_index = get_or_create_index()
        text_splitter = SentenceWindowNodeParser.from_defaults(
            window_size=3,
            window_metadata_key="window",
            original_text_metadata_key="original_text",
        )
        pipeline = IngestionPipeline(transformations=[text_splitter])
        nodes = pipeline.run(documents=docs)
        vector_index.insert_nodes(nodes)
        logger.info(f"Nodes successfully inserted into vector index.")

        return {"message": f"File {file.filename} ingested successfully."}
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        raise HTTPException(status_code=500, detail=f"Error during ingestion: {e}")


@router.get("/documents")
async def get_documents():
    global vector_index
    try:
        if vector_index is None:
            vector_index = get_or_create_index()

        documents = vector_index.docstore.docs
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found.")

        return [
            {
                "id": doc_id,
                "metadata": doc.metadata
            }
            for doc_id, doc in documents.items()
        ]
    except Exception as e:
        logger.error(f"Error fetching documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching documents: {e}")


app = FastAPI()
app.include_router(router, prefix="/indexing", tags=["Indexing"])
