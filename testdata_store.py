# %%
from fptree import * 
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
