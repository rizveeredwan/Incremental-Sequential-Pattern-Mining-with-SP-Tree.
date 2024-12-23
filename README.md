# Incremental-Sequential-Pattern-Mining-with-SP-Tree.
A novel technique to mine sequential patterns from incremental sequential database using SP-Tree. The code can be found in .\implementation\INCSPTree_BPFSPTree\version5 folder. The code begins from Main.py file. The dataset format is given below. 

"""
10
1 0 -1 1 -1
2 2 3 -1 0 -1 4 5 6 -1
3 0 6 7 -1
4 0 -1 4 6 -1 1 -1
5 1 -1 2 -1
6 0 -1 1 2 -1
7 0 -1 1 2 3 -1
8 4 6 -1
9 5 -1 8 -1
10 7 8 -1
"""
- First value denotes the number of transactions
- Each line denotes a transaction, multi-itemed event is considered, each event's ending is denoted with -1 value, all the events are ordered. 
- Sample of the dataset can be found in .\Implementation\Dataset\Dataset2 folder. in1.txt, in2.txt, ..., denotes incremental database addition 
