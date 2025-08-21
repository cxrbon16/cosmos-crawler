import os
from huggingface_hub import HfApi

def upload_file(file_path, repo_id):
    """
    Uploads a file to a Hugging Face repository.

    Args:
        file_path (str): The path to the file to upload.
        repo_id (str): The ID of the repository to upload to.
    """
    api = HfApi()
    api.upload_file(
        path_or_fileobj=file_path,
        path_in_repo=os.path.basename(file_path),
        repo_id=repo_id,
        repo_type="dataset"
    )
    print(f"Successfully uploaded {file_path} to {repo_id}")

def delete_file(file_path):
    """
    Deletes a file.

    Args:
        file_path (str): The path to the file to delete.
    """
    os.remove(file_path)
    print(f"Successfully deleted {file_path}")
