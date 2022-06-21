from google.cloud import storage
import os


def send_object_to_storage(filename, path):
    storage_client = storage.Client.from_service_account_json('./credentials/credentials.json')
    bucket = storage_client.get_bucket("kas-audio")
    blob = bucket.blob(filename)
    blob.upload_from_filename(path)

 