import os
import tempfile
from git import Repo
from google.cloud import storage


def clone_repo(repo_url, branch):
    temp_dir = tempfile.mkdtemp()
    Repo.clone_from(repo_url, temp_dir, branch=branch)
    return temp_dir


def read_files_in_directory(directory):
    file_contents = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_contents[file_path] = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'rb') as f:
                    file_contents[file_path] = f.read()
    return file_contents


def upload_to_gcp(bucket_name, file_path, content):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.upload_from_string(content)


def save_files_to_gcp(file_contents, bucket_name):
    for file_path, content in file_contents.items():
        upload_to_gcp(bucket_name, file_path, content)
