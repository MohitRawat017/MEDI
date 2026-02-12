import os 
import shutil
from fastapi import UploadFile # for handling file uploads
import tempfile # for creating temporary directories

UPLOAD_DIR = "./uploaded_pdfs"

def save_uploaded_files(files: list[UploadFile]) -> list[str]: # we are returning a list of file paths where the uploaded files are saved ! 
    os.makedirs(UPLOAD_DIR, exist_ok=True) # create the upload directory if it doesn't exist
    file_paths = [] 

    for file in files: 
        temp_path = os.path.join(UPLOAD_DIR, file.filename) # create a path for the uploaded file
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f) # save the uploaded file to the temp path
        file_paths.append(temp_path) # add the file path to the list

    return file_paths