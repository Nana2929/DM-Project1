"""
=================================

TESTING SCRIPT

=================================
"""
#%%
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
import pandas as pd
from utils import read_file, timer
# ==========My Own Packages============
import fptree
import importlib
importlib.reload(fptree)
from fptree import *
from apriori import *


MINSUP, MINCONF = 0.3, 0.3
filepath = '/Users/yangqingwen/Downloads/ibm-2022-release-testdata-1/2022-DM-release-testdata-2.data'
# filepath = '/Users/yangqingwen/Downloads/IBM2021.txt'

data = read_file(
    filepath)
transactions = preprocess(data)
#%%
# =========== My Apriori ===============
@timer
def myApriori():
    global myapriori
    myapriori= Apriori(transactions, minsup = MINSUP, minconf = MINCONF)
    apPatterns = myapriori.gen_freq_patterns()
    print(f'My Freqsets length: {len(apPatterns)}')
    apRules = myapriori.get_rules(apPatterns)
    print(f'My Rules length: {len(apRules)}')
    return apRules, apPatterns
apRules, apPatterns = myApriori()
apPatterns = set(apPatterns)

#%%
# =========== My FPGrowth ===============
@timer
def myFP():
    global mainTree
    mainTree = makeTree(transactions, min_support_ratio = MINSUP)
    freqPatternDict = mineTree(mainTree)
    fpPatterns = flatten(freqPatternDict)
    fpRules = getAssociationRules(transactions, fpPatterns, minconf = MINCONF)
    print(f'My Freqsets length: {len(fpPatterns)}')
    print(f'My Rules length: {len(fpRules)}')
    return fpRules, fpPatterns
fpRules, fpPatterns = myFP()

#%%
# =========== Mlxtend Apriori ===============
from mlxtend.frequent_patterns import fpgrowth, apriori, association_rules
@timer
def LibApriori():
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df = pd.DataFrame(te_ary, columns=te.columns_)
    freqsets = apriori(df, min_support=MINSUP)
    LibRules = association_rules(freqsets, metric="confidence", min_threshold=MINCONF)
    print(f'Lib FreqSets Size: {len(freqsets)}')
    print(f'Lib Rules length: {len(LibRules)}')
LibApriori()
# %%
# =========== Mlxtend FpGrowth ===============
@timer
def LibFP():
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df = pd.DataFrame(te_ary, columns=te.columns_)
    # global freqsets
    freqsets = fpgrowth(df, min_support=MINSUP, use_colnames=True)
    librules = association_rules(freqsets, metric="confidence", min_threshold=MINCONF)
    print(f'Lib FreqSets Size: {len(freqsets)}')
    print(f'Lib Rules length: {len(librules)}')
LibFP()




