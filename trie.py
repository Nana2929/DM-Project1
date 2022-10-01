
#%%
from typing import Optional, Dict, List

class TrieNode:
    def __init__(self, item_id:Optional[int] = None):
        self.children = {}
        self.item_id = item_id
    def __repr__(self):
        return f"TrieNode({self.item_id}, {self.children})"

class Trie:

    def __init__(self, k:int):
        self.root = TrieNode()
        self.k = k
        self.isize = k - 1
        self.plen = k - 2

    def insert(self, itemset:List[int]) -> None:
        """Insert itemset of Lk-1 in to the trie,
        each itemset is in length of k-1 in iteration k  of aprior
        Args:
            itemset (List[int]): itemset in Lk-1
        """
        assert len(itemset) == self.isize
        node = self.root
        itemset.sort()
        for item in itemset:
            if item not in node.children:
                node.children[item] = TrieNode(item)
            node = node.children[item]

    def get_children(self, prefix: List[int]) -> Dict:
        """get children based on itemset prefix
            prefix is in length of k-2 in iteration k of apriori
        Args:
            prefix (List[int]): a subset of the itemset (prefix)
        Returns:
            Dict: children; the children of the prefix;
            itemsets can be transformed back as prefix.union(c) for c in children
        """
        assert len(prefix) == self.plen
        node = self.root
        prefix.sort()
        for p in prefix:
            node = node.children[p]
        return node

    def get_clean_children(self, prefix):
        """Remove TrieNode structure from children list
        """
        node = self.get_children(prefix)
        return [c for c in node.children.keys()]
# t = Trie(k = 4)
# t.insert([1,2,3])
# t.insert([1,2,4])
# t.insert([2,3,5])
# t.insert([2,4,8])
# t.insert([2,3,11])
# c1 = t.get_clean_children(prefix = [1,2])
# print(c1)
# c2 = t.get_clean_children(prefix = [2,3])
# print(c2)

# %%
