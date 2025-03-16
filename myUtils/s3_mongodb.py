import logging
import streamlit as st
from datetime import datetime
import uuid
import os
from connectors.aws_connector import S3Connector
from connectors.mongo_connector import MongoConnector


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("S3 MongoDB Utils")

# Initialize AWS S3 Connector and MongoDB Connector
if "aws_s3" not in st.session_state:
    st.session_state.aws_s3 = S3Connector()

if "db" not in st.session_state:
    st.session_state.db = MongoConnector()

def upload_pdf_to_s3_and_mongodb(uploaded_file,temp_file_path,bucket_path):
    """Handle PDF upload, S3 upload, and MongoDB metadata storage"""
    try:
        # Generate a unique S3 key
        file_name = uploaded_file.name
        file_size = uploaded_file.size
        s3_key = f"{bucket_path}/{uuid.uuid4()}_{file_name}"

        # # Save the uploaded file temporarily
        # temp_file_path = f"/tmp/{file_name}"
        # with open(temp_file_path, "wb") as f:
        #     f.write(uploaded_file.getbuffer())

        # Upload to S3
        s3_url = st.session_state.aws_s3.upload_file_to_s3(temp_file_path, s3_key)
        if not s3_url:
            st.error("Failed to upload file to S3")
            return

        # Prepare metadata for MongoDB
        metadata = {
            "file_name": file_name,
            "file_size": file_size,
            "s3_url": s3_url,
            "s3_key": s3_key,
            "uploaded_at": datetime.utcnow(),
            "metadata": {
                "content_type": uploaded_file.type,
                "original_name": file_name,
            },
        }

        # Store metadata in MongoDB
        document_id = st.session_state.db.create_document("pdf_metadata", metadata)
        logger.info(f"File uploaded successfully! Document ID: {document_id}");
        return document_id
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return ''
