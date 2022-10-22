
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
        """Insert sorted itemset of Lk-1 in to the trie,
        each itemset is in length of k-1 in iteration k of apriori
        Args:
            itemset (List[int]): itemset in Lk-1; sorted
        """
        assert len(itemset) == self.isize
        node = self.root
        for item in itemset:
            if item not in node.children:
                node.children[item] = TrieNode(item)
            node = node.children[item]

    def get_children(self, prefix: List[int]) -> Dict:
        """get children based on sorted itemset prefix
            prefix's length is k-2 in iteration k of apriori
        Args:
            prefix (List[int]): a subset of the itemset (prefix); sorted
        Returns:
            Dict: children; the children of the prefix;
            itemsets can be transformed back as prefix.union(c) for c in children
        """
        assert len(prefix) == self.plen
        node = self.root
        for p in prefix: # traverse down th prefix path
            node = node.children[p]
        return node

    def get_clean_children(self, prefix):
        """Remove TrieNode structure from children list
        """
        node = self.get_children(prefix)
        return [c for c in node.children.keys()]
