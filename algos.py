
#%%
from typing import List, Tuple, Dict, Set
from collections import Counter, defaultdict
from itertools import chain, combinations
import trie
import importlib
from copy import deepcopy
importlib.reload(trie)
from trie import Trie
import logging


class Apriori:

    def __init__(self):
        logging.basicConfig(level = logging.INFO)
        self.logger = logging.getLogger(__name__)

    def init_support_dict(self, C1):
        self.globalSupport = defaultdict(int)
        for c, c_count in C1.items():
            self.globalSupport[frozenset(c)] = c_count

    def input_preproc(self, input_data: List[List[str]]) -> Tuple[defaultdict, Counter]:
        transactions = defaultdict(list)
        init_items = Counter()
        for line in input_data:
            tid, item_id = line[0], str(line[-1])
            transactions[tid].append(item_id)
            init_items[item_id] += 1
        return transactions, init_items

    def gen_rules(self, input_data: List[List[int]]):
        # MINSUP = args.min_sup
        # MINCONF = args.min_conf
        # MAXMERGE = args.max_merge
        MAXMERGE = 2000
        MINSUP = 0.5
        MINCONF = 0.66
        # ===================================
        self.transactions, C1 = self.input_preproc(input_data)
        self.minsup_c = int(MINSUP * len(self.transactions))
        self.minsup = MINSUP
        self.minconf = MINCONF
        self.logger.info(C1)
        L1 = [set(item) for item, count in C1.items() if count >= self.minsup_c]
        self.init_support_dict(C1)
        Lk_1 = L1

        for k in range(2, MAXMERGE):
            self.logger.info(f'L_{k-1}:{Lk_1}')
            Ck = self.join(k, Lk_1)
            self.logger.info(f'C_{k} = {Ck}')
            Ck = self.prune(k, Ck, Lk_1)
            self.logger.info(f'pruned C_{k} = {Ck}')
            Lk = self.get_support(Ck)
            self.logger.info(f'L_{k} = {Lk}')
            if Lk == []:
                break
            Lk_1 = Lk
        association_rules = self.get_rules(Lk_1)
        return association_rules

    def get_powerset(self, s):
        return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


    def get_rules(self, final_freqItemSets):
        mined_rules = []
        for m in final_freqItemSets:
            s_powerset = self.get_powerset(m)
            for p in s_powerset:
                if len(p) == 0:
                    continue
                m, p = frozenset(m), frozenset(p)
                p_support = self.globalSupport[p]
                m_support = self.globalSupport[m]
                confidence = m_support / p_support
                m_p = m.difference(p)
                if len(m_p) == 0:
                    continue
                if confidence >= self.minconf:
                    mined_rules.append((p, m_p, confidence)) # 'p -> m-p, confidence'
        return mined_rules


    def join(self, k:int, Lk_1:List[Set[str]]) -> List[Set[str]]:
        Ck = []
        tree = Trie(k)
        for l in Lk_1:
            l = sorted(list(l))
            tree.insert(l)
        for l in Lk_1:
            curl = deepcopy(l)
            l = sorted(list(l))
            prefix = l[:k-2]
            suffix = l[-1]
            candidates = tree.get_clean_children(prefix = prefix)
            for c in candidates:
                if c > suffix:
                    cloned_curl = deepcopy(curl)
                    cloned_curl.add(c)
                    Ck.append(cloned_curl)
        return Ck

    def get_support(self, itemsets:List[Set[str]]) -> List[Set[str]]:
        """Scanning DB (transactions) to recalc support for each itemset
        Args:
            itemsets (List[int]): L
        Returns:
            List[List[int]]: the itemsets with support >= min support count (minsup_c)
        """
        aboveSup = []
        for transac in self.transactions.values():
            for itemset in itemsets:
                setkey = frozenset(itemset)
                if itemset.issubset(transac):
                    self.globalSupport[setkey] += 1
        for itemset in itemsets:
            setkey = frozenset(itemset)
            if self.globalSupport[setkey] < self.minsup_c:
                continue
            aboveSup.append(itemset)
        return aboveSup

    def prune(self, k:int, Ck:List[Set[int]], Lk_1:List[Set[str]]) -> List[Set[str]]:
        pruned_Ck = []
        for c in Ck:
            subsets = chain.from_iterable(combinations(c, k))
            to_prune = False
            for subset in subsets:
                if subset not in Lk_1: # linear
                    break; to_prune = True
            if not to_prune:
                pruned_Ck.append(c)
        return pruned_Ck


#%%
algo = Apriori()
data2 = [
    [1,1,1], [1,1,3], [1,1,4],
    [2,2,2], [2,2,3], [2,2,5],
    [3,3,1], [3,3,2], [3,3,3], [3,3,5],
    [4,4,2], [4,4,5],
    [5,5,1], [5,5,3], [5,5,5],
]
rules = algo.gen_rules(data2)
print(rules)
#%%
algo = Apriori()
data = [[1,1,'A'], [1,1, 'C'], [1,1, 'D'],
        [2,2,'B'], [2,2,'C'], [2,2,'E'],
        [3,3,'A'], [3,3,'B'], [3,3,'C'], [3,3,'E'],
        [4,4,'B'], [4,4,'E']]
# self.logger.info(algo.input_preproc(data))
rules = algo.gen_rules(data)
