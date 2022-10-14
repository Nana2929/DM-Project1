#%%
import logging
from optparse import Values
from trie import Trie
from typing import List, Tuple, Dict, Set, Optional, Union
from collections import Counter, defaultdict
from itertools import chain, combinations
import importlib
from itertools import combinations
from copy import deepcopy
from collections import deque
import trie
importlib.reload(trie)


NODELIST = 'nodelist'
COUNT = 'count'


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


"""
conditional fp tree 的 input 可能會是一個path of nodes
需要init header 時可以考慮
"""


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

    def _process_prefix_paths(self, prefix_paths):
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

    def _gen_freq_patterns(self,
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
        # level-order traversal
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
        # return levels

    # def get_conditional_tree(self, mainTree: FPtree,
    #                          target_item: int, minsup_c: int):
    #     cond_pattern_bases = []
    #     cond_pattern_base_freqs = []
    #     cond_pattern_tree = FPtree(minsup_c)
    #     prefix_paths = mainTree._get_prefix_paths(target_item)
    #     for path, min_count in prefix_paths:
    #         # first initialize the headerTable
    #         path_items, path_count = [x.item for x in path], [
    #             min_count for x in path]
    #         cond_pattern_bases.append(path_items)
    #         cond_pattern_base_freqs.append(path_count)
    #         cond_pattern_tree.insert(transaction=path_items,
    #                                  freq=path_count)
    #     # add leaves

    #     return cond_pattern_bases, cond_pattern_base_freqs, cond_pattern_tree


def _input_preproc(txs):
    """DONT USE IT IN OFFICIAL VERSION"""
    transactionList = txs
    init_items = Counter(
        [item for sublist in txs for item in sublist])
    return transactionList, init_items


def input_preproc(input_data: List[List[str]]) -> Tuple[defaultdict, Counter]:
    """Process the input data into List[List[int]] of transactions
    Args:
        input_data (List[List[str]]): ibm format
    Returns:
        Tuple[defaultdict, Counter]:
            transactionList: List of transactions in slides
            itemCounter: count the occurrences of all items, and EXCLUDE THOSE UNDER min support count
    """
    transactions = defaultdict(list)
    for line in input_data:
        tid, item_id = line[0], str(line[-1])
        transactions[tid].append(item_id)
    transactionList = [None for _ in range(len(transactions))]
    for tid, values in transactions:
        transactionList[tid] = values
    return transactionList


def mine_tree(self, fptree: FPtree):
    sortedI2N = sorted(fptree.item2nodes.items(),
                       key=lambda x: x[1]['count'])
    for item, info in sortedI2N:
        cp_bases, cpb_freq, cptree = fptree.get_cond_pattern_bases(
            item, self.minsup_c)

        print(f'===== {item} =====')
        print('conditional pattern bases:', cp_bases)
        print('conditional pattern base freq:', cpb_freq)


#%%
transactions = [['milk', 'bread', 'beer'],
                ['bread', 'coffee'],
                ['bread', 'egg'],
                ['milk', 'bread', 'coffee'],
                ['milk', 'egg'],
                ['bread', 'egg'],
                ['milk', 'egg'],
                ['milk', 'bread', 'egg', 'beer'],
                ['milk', 'bread', 'egg']]
mainTree = FPtree(2, transactions, ItemFrequency=None)
mainTree.build_tree()
print(mainTree.headerTable)
print('MAIN')
mainTree.print_tree()
print(' === CONDITIONAL FP TREE beer ===')
conditional_tree = mainTree.build_conditional_tree('beer')
conditional_tree.print_tree()
beer_cpbases = conditional_tree._get_prefix_paths('beer')
beerFreqPatterns = conditional_tree._gen_freq_patterns('beer')


print(' === CONDITIONAL FP TREE coffee ===')
conditional_tree = mainTree.build_conditional_tree('coffee')
conditional_tree.print_tree()
coffeeFreqPatterns = conditional_tree._gen_freq_patterns('coffee')


print(' === CONDITIONAL FP TREE egg ===')
conditional_tree = mainTree.build_conditional_tree('egg')
conditional_tree.print_tree()


print('!!! Conditional Pattern Base !!!!')
egg_cpbases = conditional_tree._get_prefix_paths('egg')
eggFreqPatterns = conditional_tree._gen_freq_patterns('egg')


print(' === CONDITIONAL FP TREE milk ===')
conditional_tree = mainTree.build_conditional_tree('milk')
conditional_tree.print_tree()
milkFreqPatterns = conditional_tree._gen_freq_patterns('milk')

print(' === CONDITIONAL FP TREE bread ===')
conditional_tree = mainTree.build_conditional_tree('bread')
conditional_tree.print_tree()
breadFreqPatterns = conditional_tree._gen_freq_patterns('bread')

# Conditional Pattern Base Generation


# get combinations


# %%
