"""
The entry point of the program

First of all, you don't have to follow the structure of this file,
but please make sure that: (1)we can run your code by running this file,
(2)it can generate the output files, and (3)it can accept the command line arguments.

Please implement the `apriori` and `fp_growth` functions in
the `my_cool_algorithms.py` file (or any module name you prefer).

The `input_data` is a list of lists of integers. Each inner list
is in the form of [transaction_id, transaction_id, item_id].
For example, the following input data contains 2 transactions,
transaction 1 contains 2 items 9192, 31651;
transaction 2 contains 2 items 26134, 57515.

[
    [1, 1, 9192],
    [1, 1, 31651],
    [2, 2, 26134],
    [2, 2, 57515],
]


The `a` is a `Namespace` object that contains the following attributes:
    - dataset: the name of the dataset
    - min_sup: the minimum support
    - min_conf: the minimum confidence
you can access them by `a.dataset`, `a.min_sup`, `a.min_conf`.
"""
#%%
from pathlib import Path
from typing import List
import utils
from utils import l, timer
from utils import preprocess
import config
import args
# ==========My Own Packages============
import fptree
from fptree import *
from apriori import *

@timer
def myApriori(transactions, args):
    myapriori = Apriori(transactions,
                        minsup=args.min_sup,
                        minconf=args.min_conf)
    apPatterns = myapriori.gen_freq_patterns()
    apRules = myapriori.get_rules(apPatterns)

    return apRules, apPatterns

@timer
def myFP(transactions, args):
    mainTree = makeTree(transactions, min_support_ratio=args.min_sup)
    freqPatternDict = mineTree(mainTree)
    fpPatterns = flatten(freqPatternDict)
    fpRules = getAssociationRules(
        transactions, fpPatterns, minconf=args.min_conf)
    return fpRules, fpPatterns

def main():
    # Parse command line arguments
    a = args.parse_args()
    l.info(f"Arguments: {a}")
    # Load dataset, the below io handles ibm dataset
    input_data: List[List[str]] = utils.read_file(config.IN_DIR / a.dataset)
    transactions = preprocess(input_data)
    filename = Path(a.dataset).stem



    apRules, apPatterns = myApriori(transactions, a)
    fpRules, fpPatterns = myFP(transactions, a)


    l.info(f'minsup = {a.min_sup}, minconf = {a.min_conf}')
    l.info(f'========Apriori=========')
    l.info(f'Freqset Size: {len(apPatterns)}')
    l.info(f'Rules Num: {len(apRules)}')
    l.info(f'========FPGrowth=========')
    l.info(f'Freqset Size: {len(fpPatterns)}')
    l.info(f'Rules Num: {len(fpRules)}')
    utils.write_file(
        data=apRules,
        filename=config.OUT_DIR / f"{filename}-apriori.csv"
    )
    utils.write_file(
        data=fpRules,
        filename=config.OUT_DIR / f"{filename}-fp_growth.csv"
    )
if __name__ == "__main__":
    main()
# %%
