import hashlib

import enum
import uuid


def format_bucket_name(owner_id: uuid.UUID):
    return str(owner_id).replace("-", "")


def hash_file(filename):
    """ "This function returns the SHA-1 hash
    of the file passed into it"""

    # make a hash object
    h = hashlib.sha1()

    # open file for reading in binary mode
    with open(filename, "rb") as file:

        # loop till the end of the file
        chunk = 0
        while chunk != b"":
            # read only 1024 bytes at a time
            chunk = file.read(1024)
            h.update(chunk)

    # return the hex representation of digest
    return h.hexdigest()


def hash_bytes(bytes_in):
    """ "This function returns the SHA-1 hash
    of the file passed into it"""

    # make a hash object
    h = hashlib.sha1()
    h.update(bytes_in)
    return h.hexdigest()


class S3FileData:
    file_name: str
    original_file_name: str
    bucket_name: str

    def __init__(
        self, file_name: str, original_file_name: str, bucket_name: str
    ) -> None:
        self.file_name = file_name
        self.original_file_name = original_file_name
        self.bucket_name = bucket_name


class BackendStorageOption(enum.Enum):
    MINIO_STORAGE: str = "MINIO_STORAGE"  # type: ignore
    GOOGLE_STORAGE: str = "GOOGLE_STORAGE"  # type: ignore


def make_custom_id():
    return str(uuid.uuid4()).replace("-", "")
