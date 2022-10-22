"""
=================================

TESTING SCRIPT

=================================
"""
#%%
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
import pandas as pd
from sympy import re
from utils import read_file, timer, preprocess
# ==========My Own Packages============
import fptree
# import importlib
# importlib.reload(fptree)
from fptree import *
from apriori import *

filepath = '/Users/yangqingwen/Desktop/Github/DM-Project1/inputs/target.txt'
# filepath = '/Users/yangqingwen/Downloads/IBM2021.txt'

data = read_file(
    filepath)
transactions = preprocess(data)

#%%
# =========== My Apriori ===============
@timer
def myApriori(MINSUP, MINCONF):
    global myapriori
    myapriori= Apriori(transactions, minsup = MINSUP, minconf = MINCONF)
    apPatterns = myapriori.gen_freq_patterns()
    print(f'My Freqsets length: {len(apPatterns)}')
    apRules = myapriori.get_rules(apPatterns)
    print(f'My Rules length: {len(apRules)}')
    return apRules, apPatterns

# myapriori= Apriori(transactions, minsup = 0.1, minconf = 0.1)
# apPatterns = set(apPatterns)

#%%
# =========== My FPGrowth ===============
@timer
def myFP(MINSUP, MINCONF):
    global mainTree
    mainTree = makeTree(transactions, min_support_ratio = MINSUP)
    freqPatternDict = mineTree(mainTree)
    fpPatterns = flatten(freqPatternDict)
    fpRules = getAssociationRules(transactions, fpPatterns, minconf = MINCONF)
    print(f'My Freqsets length: {len(fpPatterns)}')
    print(f'My Rules length: {len(fpRules)}')
    return fpRules, fpPatterns


#%%
# =========== Mlxtend Apriori ===============
from mlxtend.frequent_patterns import fpgrowth, apriori, association_rules
@timer
def LibApriori(MINSUP, MINCONF):
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df = pd.DataFrame(te_ary, columns=te.columns_)
    freqsets = apriori(df, min_support=MINSUP)
    LibRules = association_rules(freqsets, metric="confidence", min_threshold=MINCONF)
    print(f'Lib FreqSets Size: {len(freqsets)}')
    print(f'Lib Rules length: {len(LibRules)}')

# %%
# =========== Mlxtend FpGrowth ===============
@timer
def LibFP(MINSUP, MINCONF):
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions)
    df = pd.DataFrame(te_ary, columns=te.columns_)
    freqsets = fpgrowth(df, min_support=MINSUP, use_colnames=True)
    librules = association_rules(freqsets, metric="confidence", min_threshold=MINCONF)
    print(f'Lib FreqSets Size: {len(freqsets)}')
    print(f'Lib Rules length: {len(librules)}')
    return librules, freqsets


#%%

# %%
minsup = 0.1
rulesizes = []
confs = []
for i in range(9):
    minconf = 0.1 + i*0.1
    aprules, appatterns = myApriori(MINSUP = minsup, MINCONF=minconf)
    rulesizes.append(len(aprules))
    confs.append(minconf)
#%%
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="darkgrid")
ax = sns.lineplot(confs,rulesizes)
ax.set(title='Rule Size Tendency with minsup = 0.1')
ax.set(xlabel='minconf', ylabel='rule size')
plt.show()
#%%
fixed_conf_rulesizes = []
fixed_conf_freqp = []
sups = []
minconf = 0.1
for i in range(9):
    minsup = 0.1 + i*0.1
    aprules, appatterns = myApriori(MINSUP = minsup, MINCONF=minconf)
    fixed_conf_rulesizes.append(len(aprules))
    fixed_conf_freqp.append(len(appatterns))
    sups.append(minsup)
#%%
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="darkgrid")
ax = sns.lineplot(sups,fixed_conf_rulesizes)
ax.set(title='Rule Size Tendency with minconf = 0.1')
ax.set(xlabel='minsup', ylabel='rule size')
plt.show()






# %%

