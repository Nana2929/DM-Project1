import logging
import csv
import time
from pathlib import Path
from collections import Counter, defaultdict
from typing import Any, List, Union, Tuple
from itertools import chain, combinations

def preprocess(input_data: List[List[str]]) -> Tuple[defaultdict, Counter]:
    """Process the input data into List[List[int]] of transactions
    Args:
        input_data (List[List[str]]): ibm format
    Returns:
        Tuple[defaultdict, Counter]:
            transactionList: List of transactions in slides
            itemCounter: count the occurrences of all items, and EXCLUDE THOSE UNDER min support count
    """
    transactionDict = defaultdict(list)
    for line in input_data:
        tid, item_id = line[0], str(line[-1])
        transactionDict[tid].append(item_id)
    transactionList = list(transactionDict.values())
    return transactionList

def powerset(s):
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


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
        [x for x in line.split()]
        #
        for line in Path(filename).read_text().splitlines()
    ]

@timer
def write_file(data: List[Tuple[Any]], filename: Union[str, Path]) -> None:
    """write_file writes the data to a csv file and
    adds a header row with `antecedent`, `consequent`, `support`, `confidence`, `lift`.

    Args:
        data (List[Tuple[Any]]): The data to write to the file
        # Tuple example:
        #  (frozenset({'15'}),
        #  frozenset({'12'}),
        #  0.10951585976627713,
        #  0.3791907514450867,
        #  1.0240543738305092)
        filename (Union[str, Path]): The filename to write to
    """
    proc_data = []
    for rule in data:
        PREC = 3
        a, c, sup, conf, lift = rule
        a, c = ' '.join(list(set(a))), ' '.join(list(set(c)))
        a = '{' + a + '}'
        c = '{' + c + '}'
        sup = round(sup, PREC)
        conf = round(conf, PREC)
        lift = round(lift, PREC)
        proc_data.append([a, c, sup, conf, lift])

    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["antecedent", "consequent",
                        "support", "confidence", "lift"])
        writer.writerows(proc_data)




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