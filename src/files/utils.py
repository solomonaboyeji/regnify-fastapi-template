import hashlib

import enum

from fastapi import UploadFile
from tempfile import SpooledTemporaryFile
from typing import BinaryIO
import uuid
import os

from src.exceptions import GeneralException


ONE_MEGA_BYTE = 1024 * 1024
ONE_KB = 1024


def format_bucket_name(owner_id: uuid.UUID):
    return str(owner_id).replace("-", "")


def prepare_file_for_http_upload(file_to_upload: UploadFile):
    """If this is a SpooledTemporaryFile, force the file to be saved to disk."""

    the_file = file_to_upload.file
    if isinstance(the_file, SpooledTemporaryFile):
        # roll over to an on-disk file regardless of its size.
        # https://docs.python.org/3/library/tempfile.html#tempfile.SpooledTemporaryFile
        # This might not be needed in python3.11
        the_file.rollover()
        the_file = the_file._file  # type: ignore

    return the_file


def meet_upload_file_limit_rule(
    the_file: BinaryIO,
    file_limit: float = float(os.getenv("MAX_SIZE_OF_A_FILE", "5.0")),
):

    max_bytes_to_read = round(file_limit * ONE_MEGA_BYTE) + 1
    max_bytes_expected = round(file_limit * ONE_MEGA_BYTE)

    if max_bytes_expected < ONE_MEGA_BYTE:
        size_chunk = f"{max_bytes_expected / ONE_KB} kb"
    else:
        size_chunk = f"{max_bytes_expected / ONE_MEGA_BYTE} mb"

    # * If the actual number of bytes are less than the max_bytes_to_read,
    # * the actual number of bytes is only read.
    if len(the_file.read(max_bytes_to_read)) > max_bytes_expected:
        seek_to_start(the_file)
        raise GeneralException(f"Your file size can not be more than {size_chunk}.")

    seek_to_start(the_file)


def seek_to_start(the_file: BinaryIO):
    if not isinstance(the_file, SpooledTemporaryFile):
        if the_file.seekable():
            the_file.seek(0)


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
