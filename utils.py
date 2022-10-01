import logging
import csv
import time
from pathlib import Path
from typing import Any, List, Union

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        print(f"Running {func.__name__} ...", end='\r')
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} Done in {end - start:.2f} seconds")
        return result
    return wrapper

@timer
def read_file(filename: Union[str, Path]) -> List[List[int]]:
    """read_file

    Args:
        filename (Union[str, Path]): The filename to read

    Returns:
        List[List[int]]: The data in the file
    """
    return [
        [int(x) for x in line.split()]
        for line in Path(filename).read_text().splitlines()
    ]

@timer
def write_file(data: List[List[Any]], filename: Union[str, Path]) -> None:
    """write_file writes the data to a csv file and
    adds a header row with `relationship`, `support`, `confidence`, `lift`.

    Args:
        data (List[List[Any]]): The data to write to the file
        filename (Union[str, Path]): The filename to write to
    """
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["relationship", "support", "confidence", "lift"])
        writer.writerows(data)


def setup_logger():
    l = logging.getLogger('l')

    log_dir: Path = Path(__file__).parent / "logs"

    # create log directory if not exists
    log_dir.mkdir(parents=True, exist_ok=True)

    # set log file name
    log_file_name = f"{time.strftime('%Y%m%d_%H%M%S')}.log"

    l.setLevel(logging.DEBUG)

    fileHandler = logging.FileHandler(
        filename=log_dir / log_file_name,
        mode='w'
    )
    streamHandler = logging.StreamHandler()

    allFormatter = logging.Formatter(
        "%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s: %(message)s"
    )

    fileHandler.setFormatter(allFormatter)
    fileHandler.setLevel(logging.INFO)

    streamHandler.setFormatter(allFormatter)
    streamHandler.setLevel(logging.INFO)

    l.addHandler(streamHandler)
    l.addHandler(fileHandler)

    return l

l = setup_logger()