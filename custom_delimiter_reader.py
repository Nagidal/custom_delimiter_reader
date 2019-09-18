import pathlib
import functools
import re
from typing import Iterator, Iterable, ByteString
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


def resplit(chunks_of_a_file: Iterator, split_pattern: re.Pattern) -> Iterable[ByteString]:
    """
    Reads chunks of a file one chunk at a time, 
    splits them into data rows by `split_pattern` 
    and joins partial data rows across chunk boundaries.
    borrowed from https://bugs.python.org/issue1152248#msg223491
    """
    partial_line = None
    for chunk in chunks_of_a_file:
        if partial_line:
            partial_line = b"".join((partial_line, chunk))
        else:
            partial_line = chunk
        if not chunk:
            break
        lines = split_pattern.split(partial_line)
        partial_line = lines.pop()
        yield from lines
    if partial_line:
        yield partial_line


if __name__ == "__main__":
    path_to_source_file = pathlib.Path("source.bin")
    with open(path_to_source_file, mode="rb") as file_descriptor:
        buffer_size = 8192
        sentinel = b""
        chunks = iter(functools.partial(file_descriptor.read, buffer_size), sentinel)
        data_rows_delimiter = re.compile(b"(?P<mlp_prefix>.....)(?<!ble_X)(?P<MLP>MLP)")
        lines = resplit(chunks, data_rows_delimiter)
        for line in lines:
            logger.debug(line)
