#%%
import numpy as np
import pandas as pd
import os
import random
import math

path = '/Users/yangqingwen/Desktop/Github/DM-Project1/inputs/kaggle-order_products__prior.csv'
df = pd.read_csv(path)
# df = df.groupby('order_id')['product_id'].apply(list)
outdir = '/Users/yangqingwen/Desktop/Github/DM-Project1/inputs'

#%%

# %%
outfilename = 'kaggle-opp-10%.txt'
transac_count = len(df['order_id'].unique())
samples = random.sample(range(1, transac_count), math.ceil(transac_count/10))
sample_df = df[df['order_id'].isin(samples)]
print('Sample length:', len(sample_df))
sample_df[:10]
#%%
# sample only 10% from the kaggle dataset
with open(os.path.join(outdir, outfilename), 'w') as f:
    df['formatted'] = df.apply(
        lambda x: f"{x['order_id']}\t{x['order_id']}\t{x['product_id']}", axis=1)
    lines = df['formatted'].tolist()
    print(lines[0])
    for line in lines:
        f.write(line)


# %%
import pandas as pd
outdir = 'inputs'
infilename = 'inputs/Groceries_dataset.csv'
outfilename = 'groceries-basket-formatted.txt'
df = pd.read_csv(infilename)
transactiondict = {}
transformed_df = df.groupby(['Member_number', 'Date'])['itemDescription'].apply(list)
#%%
with open (os.path.join(outdir, outfilename), 'w') as f:
    for rid, row in enumerate(transformed_df):
        transactiondict[rid] = row
    encoder = {}
    nextid = 0
    for k, v in transactiondict.items():
        for item in set(v):
            if item not in encoder:
                encoder[item] = nextid
                nextid += 1
    for k, v in transactiondict.items():
        v = set(v)
        assert len(v) == len(set(v))
        for item in v:
            line = f"{k}\t{k}\t{encoder[item]}\n"
            f.write(line)
# %%
