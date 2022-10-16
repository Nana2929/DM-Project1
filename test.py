"""
=================================

TESTING

=================================
"""
#%%
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
import pandas as pd
from utils import read_file, timer
# my fpgrowth algorithm
from fptree import *


# 2022 testdata
filepath = '/Users/yangqingwen/Downloads/ibm-2022-release-testdata-1/2022-DM-release-testdata-2.data'
data = read_file(
    filepath)
transactions = preprocess(data)
MINSUP, MINCONF = 0.1, 0.1
@timer
def getMyRules():
    global mainTree
    mainTree = makeTree(transactions, min_support_ratio = MINSUP)
    freqPatternDict = mineTree(mainTree)
    freqPatterns = flatten(freqPatternDict)
    MyRules = getAssociationRules(transactions, freqPatterns, minconf = MINCONF)
    return MyRules, freqPatterns
MyRules, MySets = getMyRules()

@timer
def runLibFP(transactions):
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df = pd.DataFrame(te_ary, columns=te.columns_)
    # global freqsets
    freqsets = fpgrowth(df, min_support=MINSUP, use_colnames=True)
    rules = association_rules(freqsets, metric="confidence", min_threshold=MINCONF)
    return rules, freqsets
LibRules, LibSets = runLibFP(transactions)

print(f'MINCONF: {MINCONF}, MINSUP: {MINSUP}')
print('============MINE===========')
print('rules:', len(MyRules))
print('sets:', len(MySets))
print('===========MLXTEND============')
print('rules:', len(LibRules))
print('sets:', len(LibSets))


# %%

