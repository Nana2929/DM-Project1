# %%
from typing import List,  Dict, Optional, Union
from collections import Counter, defaultdict
from itertools import chain, combinations
from itertools import combinations
from collections import deque
import math
from utils import powerset

NODELIST = 'nodelist'
COUNT = 'count'

# 10/15 Calculate Support, Confidence, Lift
# Export the answer to compare with package
# 1. Rule Number Match 2. FreqItemSets Match

class Node:
    def __init__(self,
                 count: int,
                 item: Union[str, int] = None):
        self.item = item
        self.count = count
        self.parent = None
        self.children = {}

    def __repr__(self):
        return f'({self.item},{self.count})'


class FPtree:
    def __init__(self,
                 minsup_c: float,
                 transactions: List[List[Union[str, int]]],
                 ItemFrequency: Dict = None,):

        self.root = Node(count=0)
        self.minsup_c = minsup_c
        self.transactionList = transactions
        if not ItemFrequency:
            ItemFrequency = Counter(chain(*transactions))
        # initialize headerTable and prune the items below min support count
        self.initHeader(ItemFreq=ItemFrequency)

    def initHeader(self,
                   ItemFreq: Counter):

        self.headerTable = defaultdict(lambda: {NODELIST: [], COUNT: 0})
        for item, count in ItemFreq.items():
            if count >= self.minsup_c:
                self.headerTable[item][COUNT] = count

    def _insert(self, transaction: List[Union[str, int]],
                freq: Optional[List] = None):
        """insert a transaction into the fptree
        Args:
            The transaction needs to be stripped off the items below min support count already.
            transaction (List[Union[str, int]]):
                    (when building main FPtree) transaction ordered by count
                    (when building Conditional FPtree) a prefix path ordered by count
            freq: (Optional[List]): for each transaction's item, its item frequency
        """
        curr = self.root
        for idx, item in enumerate(transaction):
            frequency = freq[idx] if freq else 1
            if item in self.headerTable.keys():
                if item not in curr.children:
                    newNode = Node(item=item, count=frequency)
                    newNode.parent = curr
                    curr.children[item] = newNode
                    curr = newNode
                    self.headerTable[item][NODELIST].append(newNode)
                else:
                    curr.children[item].count += frequency
                    curr = curr.children[item]

    def build_tree(self,
                   isMain: bool = True,
                   freqs: List[int] = None):
        for tid, transaction in enumerate(self.transactionList):
            transaction = [
                x for x in transaction if x in self.headerTable.keys()]
            if isMain:
                transaction.sort(
                    key=lambda x: self.headerTable[x][COUNT], reverse=True)
                freq = [1 for _ in range(len(transaction))]
            else:
                # building Conditional FPTree
                freq = [freqs[tid] for _ in range(len(transaction))]

            self._insert(transaction, freq=freq)

    def build_conditional_tree(self, targetItem: int):
        prefix_paths = self._get_prefix_paths(targetItem)
        prefix_paths, prefix_path_freq = self._process_prefix_paths(
            prefix_paths)
        # init headerTable
        itemFreq = defaultdict(int)
        for path, pfreq in zip(prefix_paths, prefix_path_freq):
            for item in path:
                itemFreq[item] += pfreq

        conditional_tree = FPtree(
            self.minsup_c, transactions=prefix_paths, ItemFrequency=itemFreq)
        conditional_tree.build_tree(isMain=False, freqs=prefix_path_freq)
        return conditional_tree

    def _process_prefix_paths(self,
                        prefix_paths):
        paths = []
        freqs = []
        for path, min_count in prefix_paths:
            path = [node.item for node in path]
            paths.append(path)
            freqs.append(min_count)

        return paths, freqs

    def _get_prefix_paths(self, item: Union[str, int]):
        """Get prefix paths of an item,
           by going through all nodes representing the item and
           its 'parent'
        Args:
            item (Union[str, int]):
        Yields:
            List[Node]: a list of nodes representing the prefix path
        """
        paths = []
        for node in self.headerTable[item][NODELIST]:
            path = []
            curr = node
            while curr.item:
                path.append(curr)
                curr = curr.parent
            if len(path) > 0:
                # path nodes, min count of the path
                # the last node of the path is `item`
                paths.append((path[::-1], node.count))
        return paths

    def gen_freq_patterns(self,
                          target_item: Union[str, int]) -> Dict[frozenset, int]:
        """Generate conditional pattern bases given a target_item

        Args:
            target_item (Union[str, int]): the name/index of the target item

        Returns:
            _type_: _description_
        """

        # Meant to pass a conditional fptree
        max_cpbases = self._get_prefix_paths(target_item)

        # a target_item - oriented max cpbases
        cp_bases = defaultdict(int)
        for max_cpbase, min_count in max_cpbases:
            max_cp_prefix_base = [
                node.item for node in max_cpbase if node.item != target_item]
            max_cpbase = frozenset(max_cp_prefix_base)
            cp_bases[max_cpbase] += min_count
        # use combinations
        freq_patterns = defaultdict(int)
        for mcpb, mcpb_count in cp_bases.items():
            for fpsize in range(1, len(mcpb)+1):
                for items in combinations(mcpb, fpsize):
                    freq_pattern = [target_item] + list(items)
                    freq_pattern = frozenset(freq_pattern)
                    freq_patterns[freq_pattern] += mcpb_count
        # add the target_item itself as a freq_pattern
        freq_patterns[frozenset([target_item])
                      ] = self.headerTable[target_item][COUNT]
        return freq_patterns

    def print_tree(self):
        Q = deque([self.root])
        levels = []
        if not self.root:
            print('Empty tree.')
        while Q:
            level = []
            Qsize = len(Q)
            for _ in range(Qsize):
                root = Q.popleft()
                for c, cnode in root.children.items():
                    Q.append(cnode)
                level.append(root)
            print(*level, sep=',')
            levels.append(level)


def makeTree(transactions: List[List[Union[str, int]]],
             min_support_ratio: float):
    minsup_count = math.ceil(len(transactions) * min_support_ratio)
    mainTree = FPtree(minsup_c=minsup_count,
                      transactions=transactions,
                      ItemFrequency=None)
    mainTree.build_tree()
    return mainTree


def mineTree(mainTree: FPtree):
    headerTable = mainTree.headerTable
    sorted_headerTable = sorted(
        headerTable.items(), key=lambda x: x[1][COUNT], reverse=True)
    Item2FreqBases = {}
    for item, _ in sorted_headerTable:
        conditional_tree = mainTree.build_conditional_tree(item)
        item_frequent_patterns = conditional_tree.gen_freq_patterns(item)
        N = len(mainTree.transactionList)
        item_frequent_patterns = {
            k: v/N for k, v in item_frequent_patterns.items() if v >= mainTree.minsup_c}
        if item_frequent_patterns:
            Item2FreqBases[item] = item_frequent_patterns
    return Item2FreqBases

def flatten(freqPatterns:Dict):
    return [(fzset, fzscount) for item in freqPatterns for fzset,fzscount in freqPatterns[item].items()]

def getSupport(target_itemset,
            transactionList):
    count = 0
    for transaction in transactionList:
        itemset = frozenset(transaction)
        if target_itemset.issubset(itemset):
            count += 1
    return count

def getAssociationRules(transactionList,
                        final_freqItemSets: Dict[frozenset, int],
                        minconf:float):
    mined_rules = []
    global globalSupportDict
    globalSupportDict = dict()
    for m, m_support_ratio in final_freqItemSets:
        m = frozenset(m)
        s_powerset = powerset(m)
        for p in s_powerset:
            p = frozenset(p)
            if len(p) == 0:
                continue
            m_p = m.difference(p)

            p_support = globalSupportDict[p] if p in globalSupportDict \
                else getSupport(p, transactionList)
            m_p_support = globalSupportDict[m_p] if m_p in globalSupportDict \
                else getSupport(m_p, transactionList)
            globalSupportDict[p] = p_support
            globalSupportDict[m_p] = m_p_support
            confidence = m_support_ratio*len(transactionList) / p_support
            support = m_support_ratio
            lift = confidence / (m_p_support/len(transactionList))
            if len(m_p) == 0:
                continue
            if confidence >= minconf:
                mined_rules.append((p, m_p, support, confidence, lift)) # 'p -> m-p, s, c, l'
    return mined_rules