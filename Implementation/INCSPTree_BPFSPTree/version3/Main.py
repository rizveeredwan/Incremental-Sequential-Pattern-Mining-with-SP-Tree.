import sys
import os
import psutil
from math import log, floor, ceil
from collections import deque
from time import process_time

from INC_SP_Tree import INC_SP_Tree_Node
from INC_SP_Tree import INC_SP_Tree_Functionalities

from BPFSP_Tree import BPFSP_Tree
from Sequence_Summarizer_Structure import SequenceSummarizerStructure

class Main:
    def __init__(self):
        self.new_input=0
        self.seq_sum_dict={}
        self.pass_no = 0
        self.inc_sp_tree_root = INC_SP_Tree_Node()
        self.head_recursive_extension_end_linked_list_ptr = BPFSP_Tree()
        self.current_recursive_extension_end_linked_list_ptr = self.head_recursive_extension_end_linked_list_ptr
        self.inc_sp_tree_functionalities = INC_SP_Tree_Functionalities(self.current_recursive_extension_end_linked_list_ptr)
        self.cetables={}
        self.cetablei={}
        self.single_item_freq_table = {}
        self.complete_set_of_modified_nodes={}
        self.total_database_size = 0
        self.percentage_threshold = 0 # percentage threshold upong will minimum support threshold will vary
        self.minimum_support_threshold_previous = 0
        self.bpfsptree_root = BPFSP_Tree()
        self.complete_set_of_new_created_nodes = {}

        self.iteration_count_input = 0 # number of iterations
        self.start_time = process_time() # for calculation of time


    def ProcessSequence(self,line):
        line = line.strip().split(' ')
        sid = int(line[0])
        value = -1
        event_list = []
        processed_sequence = []
        for j in range(1,len(line)):
            value = int(line[j])
            if(value == -1):
                processed_sequence.append(event_list)
                event_list=[]
            else:
                event_list.append(value)
        return sid,processed_sequence

    def DatabaseInput(self):
        self.new_input = int(input())
        line = ""
        sid = -1
        processed_sequence = []
        value = ""
        self.pass_no=self.pass_no+1
        new_items={}
        modified_nodes = {}
        self.complete_set_of_modified_nodes.clear()
        self.complete_set_of_new_created_nodes.clear()
        addition_type = ""
        last_node_previously = ""
        for i in range(0,self.new_input):
            line = input()
            sid, processed_sequence = self.ProcessSequence(line)
            value = self.seq_sum_dict.get(sid)
            new_items.clear()
            count_flag = 0
            addition_type = False
            if(value == None):
                #new sequence
                self.total_database_size = self.total_database_size + 1
                self.seq_sum_dict[sid] = SequenceSummarizerStructure()
                self.seq_sum_dict[sid].sp_tree_end_node_ptr = self.inc_sp_tree_root
                self.seq_sum_dict[sid].last_event_no = -1
                value = self.seq_sum_dict[sid]
                addition_type = True
                last_node_previously = ""
            else:
                addition_type = False # appending
                last_node_previously = self.seq_sum_dict[sid].sp_tree_end_node_ptr


            end_sp_tree_node = self.inc_sp_tree_functionalities.Insert(self.pass_no, value.sp_tree_end_node_ptr , processed_sequence, 0, 0, value.last_event_no, value, 0, new_items)
            value.sp_tree_end_node_ptr = end_sp_tree_node
            value.UpdateCETables(new_items, self.cetables, value, value.last_event_no)
            value.UpdateCETablei(new_items, self.cetablei, value)
            value.last_event_no = value.last_event_no + len(processed_sequence)
            modified_nodes.clear()
            self.inc_sp_tree_functionalities.UpdatePath(end_sp_tree_node, self.pass_no, {}, modified_nodes, addition_type, last_node_previously, False)
            for key in modified_nodes:
                if(self.complete_set_of_modified_nodes.get(key) == None):
                    self.complete_set_of_modified_nodes[key] = []
                self.complete_set_of_modified_nodes[key].append(modified_nodes[key])
                if(modified_nodes[key].created_at == self.pass_no):
                    # newly created nodes
                    if(self.complete_set_of_new_created_nodes.get(key) == None):
                        self.complete_set_of_new_created_nodes[key]=[]
                    self.complete_set_of_new_created_nodes[key].append(modified_nodes[key])

    def MakingSList(self, item, minimum_support_threshold):
        s_list = 0
        if(self.cetables.get(item) == None):
            return s_list
        for key in self.cetables[item]:
            if(self.cetables[item][key] >= minimum_support_threshold):
                s_list = s_list | 1 << key
        return s_list

    def MakingIList(self, item, minimum_support_threshold):
        i_list = 0
        if(self.cetablei.get(item) == None):
            return i_list
        for key in self.cetablei[item]:
            if(key > item and self.cetablei[item][key] >= minimum_support_threshold):
                i_list = i_list | 1 << key
        return i_list

    def CreatingNodeFromBPFSPTree(self, item, actual_support, projection_nodes, pass_no):
        self.bpfsptree_root.freq_seq_ex_child_nodes[item] = BPFSP_Tree()
        self.bpfsptree_root.freq_seq_ex_child_nodes[item].parent_node = self.bpfsptree_root
        self.bpfsptree_root.freq_seq_ex_child_nodes[item].item = item
        self.bpfsptree_root.freq_seq_ex_child_nodes[item].support = actual_support
        self.bpfsptree_root.freq_seq_ex_child_nodes[item].connection_type_with_parent = True
        self.bpfsptree_root.freq_seq_ex_child_nodes[item].projection_nodes = projection_nodes

        if(pass_no > 1):
            # It was not created in the first pass, so nodes might exist beside of modified nodes
            # need to take all sorts of nodes
            for node in self.inc_sp_tree_root.next_link[item]:
                if(node.modified_at < pass_no):
                    self.bpfsptree_root.freq_seq_ex_child_nodes[item].projection_nodes.append(node)
        return

    def UpdatingABPFSPTreeNode(self, item, actual_support, new_created_nodes):
        self.bpfsptree_root.freq_seq_ex_child_nodes[item].support = actual_support
        for node in new_created_nodes:
            self.bpfsptree_root.freq_seq_ex_child_nodes[item].projection_nodes.append(node)
        return

    def InitiateCompleteMining(self):

        # root node contains complete frequency
        self.bpfsptree_root.support = self.total_database_size

        for key in self.complete_set_of_modified_nodes:
            if(self.single_item_freq_table.get(key) == None):
                self.single_item_freq_table[key] = 0
            for i in range(0, len(self.complete_set_of_modified_nodes[key])):
                if(self.complete_set_of_modified_nodes[key][i].previous_count < self.complete_set_of_modified_nodes[key][i].present_count):
                    self.single_item_freq_table[key] = self.single_item_freq_table[key] + self.complete_set_of_modified_nodes[key][i].present_count - self.complete_set_of_modified_nodes[key][i].previous_count
        minimum_support_threshold = int(ceil((self.percentage_threshold * self.total_database_size)/(100.0)))

        for key in self.complete_set_of_modified_nodes:
            if(self.single_item_freq_table[key]>= minimum_support_threshold):
                # some updates: somes frequency will increase and some will fail
                # updating the recursive extension end linked list pointer
                s_list = self.MakingSList(key, minimum_support_threshold)
                i_list = self.MakingIList(key, minimum_support_threshold)

                if(self.bpfsptree_root.freq_seq_ex_child_nodes.get(key) == None):
                    # this pattern was not frequent previously
                    self.CreatingNodeFromBPFSPTree(key, self.single_item_freq_table[key], self.complete_set_of_modified_nodes[key], self.pass_no)
                else:
                    # was already frequent previously
                    # might need to add newly created nodes
                    if(self.complete_set_of_new_created_nodes.get(key) != None):
                        self.UpdatingABPFSPTreeNode(key, self.single_item_freq_table[key], self.complete_set_of_new_created_nodes[key])
                    else:
                        self.UpdatingABPFSPTreeNode(key, self.single_item_freq_table[key], [])

                self.inc_sp_tree_functionalities.IncrementalTreeMiner(self.complete_set_of_modified_nodes[key], [[key]], 1<<key, s_list, i_list, self.bpfsptree_root.freq_seq_ex_child_nodes[key], self.cetables, self.cetablei, minimum_support_threshold, self.pass_no, minimum_support_threshold - self.minimum_support_threshold_previous)
                # completed all the works
            else:
                # A complete branch prune
                if(self.bpfsptree_root.freq_seq_ex_child_nodes.get(key) != None):
                    # already it is in the frequent pattern tree
                    # need to remove it
                    self.inc_sp_tree_functionalities.BPFSPSubTreePruning(self.bpfsptree_root.freq_seq_ex_child_nodes[key])
                    del self.bpfsptree_root.freq_seq_ex_child_nodes[key]
                    # completed all the works
        if(self.pass_no > 1):
            # need to see which big patterns got infrequent
            self.inc_sp_tree_functionalities.InitiateRemovingFromBottom(self.head_recursive_extension_end_linked_list_ptr, minimum_support_threshold)
            # completed all the works
        # updating the minimum support threshold
        self.minimum_support_threshold_previous = minimum_support_threshold
        # Printing the bi directional projection pointer based frequent sequential pattern tree
        #print("Printing Tree")
        #self.inc_sp_tree_functionalities.PrintINCSPTree(self.inc_sp_tree_root)
        self.PrintBPFSPTree(self.bpfsptree_root,[])

    def MemoryUsage(self):
        process = psutil.Process(os.getpid())
        current_memory = (process.memory_info().rss/(1024.0*1024.0)) # in bytes
        print(current_memory, " MB")

    def CPUTime(self):
        current_time = process_time()
        print("elapsed time = ",current_time - self.start_time)
        self.start_time = current_time

    def ReadPercentageThresholdAndIterationCount(self, file_name):
        with open(file_name, 'r') as file:
            lines = file.readlines()
            self.percentage_threshold = float(lines[0].strip())
            self.iteration_count_input = int(lines[1].strip())
        return

    # # DEBUG:
    def PrintCETable(self):
        print("CETABLE S")
        for key in self.cetables:
            print("item = ",key)
            for key1 in self.cetables[key]:
                print("(",key1,self.cetables[key][key1],")")
        print("CETABLE I")
        for key in self.cetablei:
            print("item = ",key)
            for key1 in self.cetablei[key]:
                print("(",key1,self.cetablei[key][key1],")")
    def PrintBPFSPTree(self, bpfsptree_node, pattern):
        if(len(pattern)>0):
            print(pattern)
            print(bpfsptree_node.support)
        for key in bpfsptree_node.freq_seq_ex_child_nodes:
            pattern.append([key])
            self.PrintBPFSPTree(bpfsptree_node.freq_seq_ex_child_nodes[key], pattern)
            del pattern[len(pattern)-1]
        sz = ""
        if(len(pattern) > 0):
            sz = len(pattern[len(pattern)-1])
        for key in bpfsptree_node.freq_item_ex_child_nodes:
            pattern[len(pattern)-1].append(key)
            self.PrintBPFSPTree(bpfsptree_node.freq_item_ex_child_nodes[key], pattern)
            del pattern[len(pattern)-1][sz]
        return




directory = 'E:\Research\Incremental-Sequential-Pattern-Mining\Incremental-Sequential-Pattern-Mining-with-SP-Tree\Implementation\Dataset\Dataset17'

main = Main()
# read percentage threshold and iteration count
main.ReadPercentageThresholdAndIterationCount(directory+'\metadata.txt')

# pass will start with 1
input_file_name = ''
#sys.stdout = open(directory+'\debug'+'.txt','w')
for i in range(1,main.iteration_count_input+1):
    input_file_name = directory+'\in'+str(i)+'.txt'
    sys.stdin = open(input_file_name,'r')
    sys.stdout = open(directory+'\out'+str(i)+'.txt','w')
    # INC SP Tree build complete
    main.DatabaseInput()
    # Now need to mine
    main.InitiateCompleteMining()
    # printing process time

#main.CPUTime()
#main.MemoryUsage()
