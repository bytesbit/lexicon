import base64
import datetime
import hashlib
import json
import mimetypes
from enum import Enum
from typing import Any, Dict, Type
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

import yaml
from rest_framework.utils import encoders
from rest_framework.utils.serializer_helpers import ReturnDict


def hash_hex(value):
    """
    Returns MD5 hash in hexadecimal form. This hash is fixed size of 32
    characters. MD5 is not secure hashing algorithm, so don't use this hash
    at sensitive places.

    :param value: string or bytes
    :return: hash string
    """
    if not isinstance(value, bytes):
        value = json.dumps(value).encode("utf-8")
    # deepcode ignore insecureHash: we are not using at sensitive places
    return hashlib.md5(value).hexdigest()  # nosec


def to_cs_str(arr):
    assert isinstance(arr, (list, tuple)), "argument should be list or tuple"
    return ",".join(list(map(str, arr)))


def to_pretty_str(arr, sep=",", last_sep="or"):
    if len(arr) >= 2:
        arr = [str(item) for item in arr]
        return f"{sep} ".join(arr[:-1]) + " " + last_sep + " " + arr[-1]
    return str(arr[0])


def to_safe_str(value, safe_length=30, suffix=None):
    value = str(value)
    safe_length = int(safe_length)
    if not suffix:
        suffix = ""
    return value[:safe_length] + suffix if len(value) > safe_length else value


def to_choices(enum_cls: Type[Enum]):
    return [(attr.value, attr.name) for attr in enum_cls]


def build_url(url, path_params=None, query_params=None):
    """Given a URL, set or replace a path and query parameters and return the
    modified URL.

    >>> build_url('https://example.com?foo=bar&biz=baz', query_params={'foo',
    ... 'stuff'})
    'https://example.com?foo=stuff&biz=baz'

    """
    url_no_qs, _, query_string = str(url).partition("?")
    try:
        url_no_qs = str(url_no_qs).format(**(path_params or {}))
    except KeyError as e:
        raise Exception("Missing %s key in path_params" % str(e)) from None
    try:
        query_string = str(query_string).format(**(query_params or {}))
    except KeyError as e:
        raise Exception("Missing %s key in query_params" % str(e)) from None
    scheme, netloc, path, _, fragment = urlsplit(url_no_qs)
    query_params = {**(query_params or {}), **parse_qs(query_string)}
    new_query_string = urlencode(query_params, doseq=True)
    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


def bytes_to_mb(bytes_):
    return float(bytes_) / (1024 * 1024)


def encode_dict_to_base64(data: Dict[str, Any]) -> str:
    """base64 encode given dict"""
    encoded_data = json.dumps(data, sort_keys=True).encode()
    return base64.b64encode(encoded_data)


def get_content_type_for_ext(ext):
    """
    Get the content type for a given file extension.

    Args:
        ext (str): The file extension.

    Returns:
        str: The content type associated with the extension, or None if not found.

    """
    # Ensure extension starts with a dot (i.e., ".") character
    if not ext.startswith("."):
        ext = f".{ext}"

    return mimetypes.types_map.get(ext)


def convert_to_kebab_case(word):
    """
    Convert a word to kebab case.

    Args:
        word (str): The word to convert.

    Returns:
        str: The kebab case version of the word.

    """
    return word.lower().replace(" ", "-").replace("_", "-")


def to_bool(value):
    """
    Convert a value to a boolean.

    Args:
        value: The value to be converted.

    Returns:
        bool: The boolean representation of the value.

    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value = value.lower()
        if value in ("false", "no", "0"):
            return False
        elif value in ("true", "yes", "1"):
            return True

    return False


def is_file_like_obj(value) -> bool:
    """
     Check if the given value is a file-like object.

    Args:
        value: The value to be checked.

    Returns:
        bool: True if the value is a file-like object, False otherwise.
    """
    return hasattr(value, "read") and hasattr(value, "write")


def format_date(date):
    """
    Converts a date string to the "day Month Year" format.

    Args:
        date (object | str): The date object or string in the format "dd-mm-yyyy".

    Returns:
        str: The formatted date string in the format "Day Month Year".
    """
    if isinstance(date, datetime.date):
        date = date.strftime("%d-%m-%Y")
    date_obj = datetime.datetime.strptime(date, "%d-%m-%Y")
    formatted_date = date_obj.strftime("%d %B %Y")
    return formatted_date


def validate_yaml_string(input_string):
    """
    Validates the YAML string by attempting to load each line separately and collects any errors.

    Args:
        input_string (str): The YAML string to validate.

    Returns:
        list: A list of error messages, if any, in the format "Line <line_number>: <error_message>".
              If the YAML data is valid, an empty list is returned.
    """
    errors = []

    try:
        lines = input_string.strip().split("\n")
        for line_num, line in enumerate(lines, start=1):
            try:
                yaml.safe_load(line)
            except yaml.YAMLError as e:
                error_message = str(e)
                errors.append(f"Line {line_num + 1}: {error_message}")

    except Exception:
        errors.append("Invalid YAML data")

    return errors


def returndict_to_dict(returndict):
    """
    Convert a ReturnDict object to a standard Python dictionary.

    This function takes a ReturnDict object, checks its type, and then
    converts it into a standard Python dictionary.

    Args:
        returndict (ReturnDict): The ReturnDict object to be converted.

    Returns:
        dict: A standard Python dictionary containing the same key-value pairs
        as the original ReturnDict.
    """
    assert isinstance(returndict, ReturnDict), (
        '"returndict" should be an ' 'instance of "ReturnDict" class'
    )
    return json.loads(json.dumps(returndict, cls=encoders.JSONEncoder))


def convert_to_base64(string: str) -> str:
    """
    Convert a given string to its base64-encoded representation.

    Args:
        string (str): The string to encode.

    Returns:
        str: The base64-encoded representation of the input string.

    Example:
        >>> convert_to_base64("hello")
        'aGVsbG8='
    """
    encoded_bytes = base64.b64encode(string.encode("utf-8"))
    encoded_str = encoded_bytes.decode("utf-8")
    return encoded_str
