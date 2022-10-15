#%%
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
from efficient_apriori import apriori
import pandas as pd
from typing import List, Tuple, Dict, Optional, Union
from collections import Counter, defaultdict
from itertools import chain, combinations
from itertools import combinations
from collections import deque
from utils import read_file


# base (3.8.12)
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

#%%
filepath = '/Users/yangqingwen/Downloads/ibm-2022-release-testdata-1/2022-DM-release-testdata-2.data'
data = read_file(
    filepath)

# transactions = [['milk', 'bread', 'beer'],
#                 ['bread', 'coffee'],
#                 ['bread', 'egg'],
#                 ['milk', 'bread', 'coffee'],
#                 ['milk', 'egg'],
#                 ['bread', 'egg'],
#                 ['milk', 'egg'],
#                 ['milk', 'bread', 'egg', 'beer'],
#                 ['milk', 'bread', 'egg']]
transactions = preprocess(data)

MINCONF = 0.1; MINSUP = 0.1
#%%
# APRIORI
import os, psutil
process = psutil.Process(os.getpid())

import time
st =  time.time()
freq_itemsets, rules = apriori(transactions, min_support=MINSUP, min_confidence=MINCONF)
end =  time.time()
print(len(rules), end - st)  # [{eggs} -> {bacon}, {soup} -> {bacon}]
print(process.memory_info().rss)
# for size, itemsets in freq_itemsets.items():
#     print(f'freq itemset size: {size}')
#     for itemset, itemset_count in itemsets.items():
#         print(itemset, itemset_count)


# %%
# FPTREE
process = psutil.Process(os.getpid())
st =  time.time()
te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df = pd.DataFrame(te_ary, columns=te.columns_)
freqsets = fpgrowth(df, min_support=MINSUP, use_colnames=True)
rules = association_rules(freqsets, metric="confidence", min_threshold=MINCONF)
end =  time.time()
print(len(rules), end - st)
print(process.memory_info().rss)

# %%
