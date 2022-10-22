

import logging
from typing import List, Set, Union, FrozenSet
from collections import Counter, defaultdict
from copy import deepcopy
from utils import powerset
import itertools
from trie import Trie
import math

class Apriori:
    def __init__(self,
                transactions: List[List[Union[int, str]]],
                minsup:float,
                minconf:float):
        logging.basicConfig(level=logging.INFO)

        self.transactionList = transactions
        self.MINSUP = minsup
        self.MINCONF = minconf
        self.minsup_c = math.ceil(self.MINSUP * len(self.transactionList))
        self.logger = logging.getLogger(__name__)

    def getC1(self) -> Counter:
        flattened_items = []
        for transac in self.transactionList:
            for item in transac:
                flattened_items.append(item)
        return Counter(flattened_items)

    def init_support_dict(self, C1):
        self.globalSupport = defaultdict(int)
        for c, c_count in C1.items():
            self.globalSupport[frozenset([c])] = c_count

    def gen_freq_patterns(self):
        MAXMERGE = 2000
        # ===================================
        C1 = self.getC1()
        self.init_support_dict(C1)
        L1 = [frozenset([item])
              for item, count in C1.items() if count >= self.minsup_c]
        FreqItemSets = []
        FreqItemSets.extend(L1)
        Lk_1 = L1
        for k in range(2, MAXMERGE):

            Ck = self.join(k, Lk_1)
            self.logger.info(f'[size] C_{k} = {len(Ck)}')
            pruned_Ck = self.prune(k, Ck, Lk_1)
            self.logger.info(f'[size] pruned C_{k} = {len(pruned_Ck)}')
            Lk = self.get_above_support(k, pruned_Ck)
            self.logger.info(f'[size] L_{k} = {len(Lk)}')

            if len(Lk) == 0:
                break
            Lk_1 = Lk
            FreqItemSets.extend(Lk)

        return FreqItemSets

    def prune(self, k:int,
        Ck:Set[FrozenSet[int]],
        Lk_1:Set[FrozenSet[int]]) -> Set[FrozenSet[str]]:
        pruned_Ck = set()
        for c in Ck:

            keep_set = True
            # check if all (k-1) subsets in the current candidate `c` appears in the Lk-1
            c_subsets = itertools.combinations(c, k-1)
            for subset in c_subsets:
                subset = frozenset(subset)
                if subset not in Lk_1:
                    keep_set = False; break
            if keep_set:
                pruned_Ck.add(c)
        return pruned_Ck

    def join(self, k:int, Lk_1:Set[FrozenSet[str]]) -> Set[FrozenSet[str]]:
        Ck = set()
        sorted_Lk_1 = {}
        tree = Trie(k)

        for l in Lk_1:
            sl = sorted(list(l))
            tree.insert(sl)
            sorted_Lk_1[l] = sl

        for l in Lk_1:
            sortedl = sorted_Lk_1[l]
            prefix = sortedl[:k-2]
            suffix = sortedl[-1]
            assert prefix + [suffix] == sortedl
            candidates = tree.get_clean_children(prefix = prefix)
            for c in candidates:
                if c != suffix:
                    cloned_l = set(deepcopy(l))
                    cloned_l.add(c)
                    assert len(cloned_l) == k
                    Ck.add(frozenset(cloned_l))
        return Ck

    def get_above_support(self,
                k:int,
                itemsets:Set[FrozenSet[str]]) -> Set[FrozenSet[str]]:
        """Scanning DB (transactions) to recalc support for each itemset
        Args:
            itemsets (List[int]): L
        Returns:
            List[List[int]]: the itemsets with support >= min support count (minsup_c)
        """
        Lk = set()
        for transac in self.transactionList:
            for itemset in itemsets:
                transac = frozenset(transac)
                if itemset.issubset(transac) and len(itemset) == k:
                    self.globalSupport[itemset] += 1


        for itemset in itemsets:
            if self.globalSupport[itemset] >= self.minsup_c:
                Lk.add(itemset)
        return Lk

    def get_rules(self, final_freqItemSets):
        mined_rules = []
        for m in final_freqItemSets:
            global m_powerset
            m_powerset = powerset(m)
            for p in m_powerset:
                if len(p) == 0:
                    continue
                p = frozenset(p)
                p_support = self.globalSupport[p]
                m_support = self.globalSupport[m]
                m_p = m.difference(p)
                m_p_support =self.globalSupport[m_p]
                support = m_support/len(self.transactionList)
                confidence = m_support / p_support
                if len(m_p) == 0:
                    continue
                lift = confidence/(m_p_support/len(self.transactionList))
                if confidence >= self.MINCONF:
                    mined_rules.append((p, m_p, support, confidence, lift)) # 'p -> m-p, confidence'
        return mined_rules
