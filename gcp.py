#!/usr/bin/env python
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

#GCP
print("Establishing connection to GCP servers")
cred = credentials.Certificate('gcp_serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
	'storageBucket': 'bucketLink'
})
bucket = storage.bucket()
print("Connection Established to",bucket)

def download_db():
	print("Downloading Database")
	blobs = bucket.list_blobs(prefix="DB/")
	for blob in blobs:
		print(blob.name)
		blob.download_to_filename(blob.name)
	print("Database download completed")


def upload_file(blob_dest,file_dest):
	blob = bucket.blob(blob_dest)
	blob.upload_from_filename(file_dest)
	print(
		"File {} uploaded to {}.".format(
			file_dest, blob_dest
		)
	)

