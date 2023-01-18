import uuid


def make_custom_id():
    return str(uuid.uuid4()).replace("-", "")
