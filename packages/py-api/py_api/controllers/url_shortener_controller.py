from typing import Dict, List

from fastapi.responses import JSONResponse
from py_api.database import su_col
from py_api.models import ShortenedURL
from py_api.utilities.decorators import handle_exception
from py_api.utilities.parsers import has_prohibited_characters


class UrlShortenerController:

    @classmethod
    def fetch_shortened_urls(cls) -> Dict[str, List[Dict[str, str]]]:
        projection = {"_id": 0}
        cursor = su_col.find({}, projection)
        shortened_urls = [doc for doc in cursor]

        return {"urls": shortened_urls}

    @classmethod
    def delete_shortened_url(cls, endpoint: str) -> Dict[str, str] | JSONResponse:
        cursor = su_col.find_one_and_delete({"endpoint": endpoint})

        if cursor:
            return {"message": "Endpoint has been deleted!"}
        else:
            return JSONResponse(content={"message": "Endpoint wasn't found!"}, status_code=404)

    @classmethod
    @handle_exception
    def upsert_shortened_url(cls, body: ShortenedURL) -> Dict[str, str] | JSONResponse:
        dumped_body = body.model_dump()
        prohibited_chars = "'\";/:!@#$%\\[]^*()_-+{}=?.,§~`"

        if has_prohibited_characters(dumped_body["endpoint"], prohibited_chars):
            return JSONResponse(content={"message": f"Provided endpoint includes a probited character - {prohibited_chars}"}, status_code=400)

        su_col.find_one_and_update(
            filter={"endpoint": dumped_body["endpoint"]},
            update={"$set": dumped_body},
            upsert=True,
        )

        # By the time we've reached this point, all data's been verified
        # and since this is an upsert request, it will always go through even
        # when the document is not actually being updated.

        # If something goes wrong, it will probably result in a runtime exception
        # which is handled by the exception handler middleware.

        return {"message": "Shortened url has been successfully created / updated!"}
