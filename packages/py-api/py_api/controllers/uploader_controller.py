from os import getenv, path
from shutil import copyfileobj
from tempfile import gettempdir
from typing import Any, Dict

import boto3
from dotenv import load_dotenv
from fastapi import Request, UploadFile
from fastapi.responses import JSONResponse

load_dotenv()

AWS_PUB_KEY = getenv("AWS_PUB_KEY", "")
AWS_PRIV_KEY = getenv("AWS_PRIV_KEY", "")
AWS_BUCKET_NAME = getenv("AWS_BUCKET_NAME", "")


class UploaderControllers:
    @classmethod
    def get_url_of_object(cls, location: str, bucket_name: str, url_name: str) -> str:
        return "https://s3-%s.amazonaws.com/%s/%s" % (location, bucket_name, url_name)

    @classmethod
    def upload_object(cls, file: UploadFile, file_name: str) -> Dict[str, Any] | JSONResponse:
        s3 = boto3.client(
            's3', aws_access_key_id=AWS_PUB_KEY,
            aws_secret_access_key=AWS_PRIV_KEY,
        )

        try:
            # TODO: Schedule more frequent temp dir cleanups on the server
            tmpdir = gettempdir()
            with open(path.join(tmpdir, file.filename), "wb+") as file_object:
                copyfileobj(file.file, file_object)

            saved_file = file_name + "." + file.filename.rsplit('.')[1]

            s3.upload_file(
                f'{tmpdir}/{file.filename}',
                AWS_BUCKET_NAME, saved_file, ExtraArgs={
                    'ContentType': 'image/jpeg',
                },
            )

            location = s3.get_bucket_location(Bucket=AWS_BUCKET_NAME)[
                'LocationConstraint'
            ]

            return {"message": "Upload was successful", "url": cls.get_url_of_object(location, AWS_BUCKET_NAME, saved_file)}

        # TODO: Transform in JSON response in order to pass appropriate status code
        # except NoCredentialsError:
        #     return {"message": "Process authentication failed"}

        # except FileNotFoundError:
        #     return json.dumps({"message": "File upload failed"}), 500

        except Exception as e:
            return {"message": str(e)}

    @classmethod
    def dump_objects(cls) -> Dict[str, Any]:
        session = boto3.Session(
            aws_access_key_id=AWS_PUB_KEY,
            aws_secret_access_key=AWS_PRIV_KEY,
        )
        s3 = session.resource('s3')
        client = session.client('s3')
        bucket = s3.Bucket(AWS_BUCKET_NAME)
        location = client.get_bucket_location(Bucket=AWS_BUCKET_NAME)[
            'LocationConstraint'
        ]

        objects = []

        for obj in bucket.objects.all():
            objects.append(
                cls.get_url_of_object(
                    location, AWS_BUCKET_NAME, obj.key,
                ),
            )

        return {'objects': objects}