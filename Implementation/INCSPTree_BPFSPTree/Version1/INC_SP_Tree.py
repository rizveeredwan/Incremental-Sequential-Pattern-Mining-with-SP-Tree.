from queue import Queue
from BPFSP_Tree import BPFSP_Tree, RecursiveExtensionEndLinkedListPtr
from math import log, floor
from collections import deque

total_created_node_count = 0


class ItemEventCombination:
    def __init__(self,item,event):
        self.item = item
        self.event = event

class INC_SP_Tree_Node:
    def __init__(self):
        self.item = ""
        self.event_no = ""
        self.parent_node=None
        self.created_at = 0
        self.modified_at = 0
        self.child_link={}
        self.previous_count = 0
        self.present_count = 0
        self.next_link={}
        self.parent_item_bitset=0

        # DEBUG:
        self.node_id = 0

class INC_SP_Tree_Functionalities:

    def __init__(self, current_recursive_extension_end_linked_list_ptr):
        self.current_recursive_extension_end_linked_list_ptr = current_recursive_extension_end_linked_list_ptr

    def SequenceSummarizerSequenceExtensionUpdate(self, sequence_summarizer_structure, item, event_no):
        value = sequence_summarizer_structure.sequence_summarizer_table.get(item)
        if(value == None):
            sequence_summarizer_structure.sequence_summarizer_table[item]=[[],[0,0]]
            for i in range(0,3):
                sequence_summarizer_structure.sequence_summarizer_table[item][0].append(event_no)
        else:
            sequence_summarizer_structure.sequence_summarizer_table[item][0][2]=event_no
        return

    def SequenceSummarizerItemsetExtensionUpdate(self, sequence_summarizer_structure, item, event_bitset):
        sequence_summarizer_structure.sequence_summarizer_table[item][1][1] = sequence_summarizer_structure.sequence_summarizer_table[item][1][1] | event_bitset
        return

    def Insert(self, pass_no, sp_tree_node, processed_sequence, event_no, item_no, actual_event_no, sequence_summarizer_structure, event_bitset, new_items):
        global total_created_node_count

        if(event_no>=len(processed_sequence)):
            return sp_tree_node
        if(item_no >= len(processed_sequence[event_no])):
            # updating to perform CETable_i operation
            return self.Insert(pass_no,sp_tree_node,processed_sequence,event_no+1,0,actual_event_no,sequence_summarizer_structure, 0, new_items)
        item = processed_sequence[event_no][item_no]
        if(sp_tree_node.child_link.get(item) == None):
            sp_tree_node.child_link[item]={}
        node  = sp_tree_node.child_link[item].get(actual_event_no+event_no+1)
        if(node == None):
            sp_tree_node.child_link[item][actual_event_no+event_no+1] = INC_SP_Tree_Node()
            sp_tree_node.child_link[item][actual_event_no+event_no+1].item = item
            sp_tree_node.child_link[item][actual_event_no+event_no+1].event_no = event_no + actual_event_no + 1
            sp_tree_node.child_link[item][actual_event_no+event_no+1].created_at = pass_no
            sp_tree_node.child_link[item][actual_event_no+event_no+1].parent_node = sp_tree_node
            sp_tree_node.child_link[item][actual_event_no+event_no+1].previous_count = 0
            sp_tree_node.child_link[item][actual_event_no+event_no+1].present_count = 0
            sp_tree_node.child_link[item][actual_event_no+event_no+1].parent_item_bitset = event_bitset
            node = sp_tree_node.child_link[item][actual_event_no+event_no+1]
            ############## For Debug ######################
            total_created_node_count = total_created_node_count + 1
            sp_tree_node.child_link[item][actual_event_no+event_no+1].node_id = total_created_node_count

        # First, mid, last updating to calculate CETable_s
        self.SequenceSummarizerSequenceExtensionUpdate(sequence_summarizer_structure, item, event_no + actual_event_no + 1)
        # updating the sequence summarizer table to perform CETable_i
        if(item_no>=1):
            self.SequenceSummarizerItemsetExtensionUpdate(sequence_summarizer_structure, item, event_bitset)
        #Tracking the new symbols
        if(new_items.get(item) == None):
            new_items[item]=True
        return self.Insert(pass_no, node, processed_sequence, event_no, item_no+1, actual_event_no, sequence_summarizer_structure, event_bitset | (1<<item), new_items)

    def UpdatePath(self, node, pass_no, next_link_nodes, modified_nodes, addition_type, last_node_previously, last_node_found):
        if(node == None):
            return
        last_modified = node.modified_at
        if(node.modified_at<pass_no):
            node.modified_at=pass_no
            node.previous_count=node.present_count
            if(node.item != ""):
                # not taking root
                modified_nodes[node.item] = node
        else:
            # this modified node is already tracked
            if(node.item != "" and modified_nodes.get(node.item) != None):
                del modified_nodes[node.item]

        if(last_node_found == False and last_node_previously != ""):
            if(last_node_previously == node):
                last_node_found = True

        if(addition_type == True):
            # complete new addition
            node.present_count=node.present_count+1
        elif(addition_type == False):
            # just appending in the end
            if(last_node_found == True):
                pass
            elif(last_node_found == False):
                # last node not found: so need to increment for newer symbols
                node.present_count=node.present_count+1

        for key in next_link_nodes:
            value = node.next_link.get(key)
            if(value == None):
                node.next_link[key]=[]
            node.next_link[key].append(next_link_nodes[key])

        if(node.created_at == pass_no):
            if(last_modified == node.modified_at):
                # this node is created in this pass but already previously captured
                if(next_link_nodes.get(node.item) != None):
                    del next_link_nodes[node.item]
            else:
                next_link_nodes[node.item]=node
        else:
            if(next_link_nodes.get(node.item) != None):
                del next_link_nodes[node.item]
        self.UpdatePath(node.parent_node, pass_no, next_link_nodes, modified_nodes, addition_type, last_node_previously, last_node_found)
        return

    # # DEBUG:
    def PrintINCSPTree(self, node):
        print("id = ",node.node_id, "( item, event, count ) = ( ", node.item, node.event_no, node.present_count," ), parent_bitset = ",node.parent_item_bitset)
        print("previous = ",node.previous_count, "present = ",node.present_count)
        for key in node.child_link:
            for key2 in node.child_link[key]:
                self.PrintINCSPTree(node.child_link[key][key2])
        return

    def SequenceExtensionNormal(self, node_list, item, minimum_support_threshold, pass_no, current_maximum_support):
        actual_support = 0
        over_support = current_maximum_support
        new_node = ""
        next_level_nodes=[]
        failed_nodes = []
        list = []
        modified_nodes = []
        for i in range(0,len(node_list)):
            list = node_list[i].next_link.get(item)
            over_support = over_support - node_list[i].present_count
            if(list != None):
                for j in range(0,len(list)):
                    new_node = list[j]
                    over_support = over_support + new_node.present_count
                    actual_support = actual_support + new_node.present_count
                    if(new_node.event_no > node_list[i].event_no):
                        next_level_nodes.append(new_node)
                        if(new_node.modified_at == pass_no):
                            modified_nodes.append(new_node)
                    else:
                        failed_nodes.append(new_node)
            if(over_support < minimum_support_threshold):
                return over_support, actual_support, next_level_nodes, modified_nodes, False # not satisfied

        if(over_support < minimum_support_threshold):
            return over_support, actual_support, next_level_nodes, modified_nodes, False # not satisfied

        for i in range(0,len(failed_nodes)):
            actual_support = actual_support - failed_nodes[i].present_count
            list = failed_nodes[i].next_link.get(item)
            if(list != None):
                for j in range(0,len(list)):
                    new_node = list[j]
                    actual_support = actual_support + new_node.present_count
                    next_level_nodes.append(new_node)
                    if(new_node.modified_at == pass_no):
                        modified_nodes.append(new_node)
            if(actual_support < minimum_support_threshold):
                checked_all = False
                if(i == len(failed_nodes)-1):
                    checked_all=True
                return over_support, actual_support, next_level_nodes, modified_nodes, checked_all # not satisfied

        return over_support, actual_support, next_level_nodes, modified_nodes, True # satisfied

    def SequenceExtensionIncremental(self, node_list, item, minimum_support_threshold, pass_no, current_support):
        actual_support = current_support
        over_support = current_support
        list = []
        new_node = ""
        failed_nodes=[]
        modified_nodes=[]
        new_created_nodes=[]
        complete_over_support = 0
        for i in range(0,len(node_list)):
            list = node_list[i].next_link.get(item)
            if(list != None):
                for j in range(0,len(list)):
                    new_node = list[j]
                    if(new_node.modified_at == pass_no):
                        complete_over_support = complete_over_support + new_node.present_count
                        if(new_node.previous_count < new_node.present_count):
                            # this is additional support frequency
                            over_support = over_support + new_node.present_count - new_node.previous_count
                            actual_support = actual_support + new_node.present_count - new_node.previous_count
                        if(new_node.event_no>node_list[i].event_no):
                            modified_nodes.append(new_node)
                            if(new_node.created_at == pass_no):
                                new_created_nodes.append(new_node)
                        else:
                            failed_nodes.append(new_node)

        if(over_support < minimum_support_threshold):
            return over_support, actual_support, complete_over_support, new_created_nodes, modified_nodes, False # Not frequent

        for i in range(0,len(failed_nodes)):
            list = failed_nodes[i].next_link.get(item)
            if(failed_nodes[i].previous_count < failed_nodes[i].present_count):
                actual_support = actual_support - failed_nodes[i].present_count + failed_nodes[i].previous_count
            if(list != None):
                for j in range(0,len(list)):
                    if(list[j].modified_at == pass_no):
                        if(list[j].previous_count < list[j].present_count):
                            actual_support = actual_support + list[j].present_count - list[j].previous_count
                        modified_nodes.append(list[j])
                        if(list[j].created_at == pass_no):
                            new_created_nodes.append(list[j])
            if(actual_support < minimum_support_threshold):
                checked_all = False
                if(i == len(failed_nodes)-1):
                    checked_all = True
                return over_support, actual_support, complete_over_support, new_created_nodes, modified_nodes, checked_all

        return over_support, actual_support, complete_over_support, new_created_nodes , modified_nodes, True

    def SequenceExtensionForUnmodifiedPart(self, node_list, item):
        next_level_nodes = []
        failed_nodes = []
        over_support = 0
        for i in range(0,len(node_list)):
            list = node_list[i].next_link.get(item)
            if(list != None):
                for j in range(0,len(list)):
                    over_support = over_support + list[j].present_count
                    if(list[j].event_no > node_list[i].event_no):
                        next_level_nodes.append(list[j])
                    else:
                        failed_nodes.append(list[j])
        for i in range(0,len(failed_nodes)):
            list = failed_nodes[i].next_link.get(item)
            if(list != None):
                for j in range(0,len(list)):
                    next_level_nodes.append(list[j])
        return over_support, next_level_nodes

    def SequenceExtensionFromModifiedToUnmodified(self, node_list, item, pass_no):
        next_level_nodes = []
        failed_nodes = []
        over_support = 0
        for i in range(0,len(node_list)):
            list = node_list[i].next_link.get(item)
            if(list != None):
                for j in range(0,len(list)):
                    if(list[j].modified_at < pass_no):
                        over_support = over_support + list[j].present_count
                        if(list[j].event_no > node_list[i].event_no):
                            next_level_nodes.append(list[j])
                        else:
                            failed_nodes.append(list[j])
        for i in range(0,len(failed_nodes)):
            list = failed_nodes[i].next_link.get(item)
            if(list != None):
                for j in range(0,len(list)):
                    next_level_nodes.append(list[j])
        return over_support, next_level_nodes


    def ItemsetExtensionNormal(self, node_list, item, minimum_support_threshold, pass_no, last_event_item_bitset, current_maximum_support):
        #last event item bitset - all the previous items bitset representation
        actual_support = current_maximum_support
        q = Queue()
        new_node = ""
        next_level_nodes = []
        list = []
        modified_nodes = []

        for i in range(0,len(node_list)):
            actual_support = actual_support - node_list[i].present_count
            list = node_list[i].next_link.get(item)
            if(list != None):
                for j in range(0,len(list)):
                    new_node = list[j]
                    actual_support = actual_support + new_node.present_count
                    if((new_node.parent_item_bitset & last_event_item_bitset) == last_event_item_bitset):
                        next_level_nodes.append(new_node)
                        if(new_node.modified_at == pass_no):
                            modified_nodes.append(new_node)
                    else:
                        q.put(new_node)
            if(actual_support < minimum_support_threshold):
                return actual_support, next_level_nodes, modified_nodes, False # already failed

        if(actual_support < minimum_support_threshold):
            return actual_support, next_level_nodes, modified_nodes, False # already failed

        while(q.qsize()>0):
            new_node = q.get()
            actual_support = actual_support - new_node.present_count
            list = new_node.next_link.get(item)
            if(list != None):
                for i in range(0,len(list)):
                    actual_support = actual_support + list[i].present_count
                    if((list[i].parent_item_bitset & last_event_item_bitset) == last_event_item_bitset):
                        next_level_nodes.append(list[i])
                        if(list[i].modified_at == pass_no):
                            modified_nodes.append(list[i])
                    else:
                        q.put(list[i])
            if(actual_support < minimum_support_threshold):
                checked_all = False
                if(q.qsize() == 0):
                    checked_all = True
                return actual_support, next_level_nodes, modified_nodes, checked_all
        return actual_support, next_level_nodes, modified_nodes, True

    def ItemsetExtensionIncremental(self, node_list, item, minimum_support_threshold, pass_no, last_event_item_bitset, current_support):
        actual_support = current_support
        list = []
        modified_nodes = []
        new_created_nodes = []
        q=Queue()
        for i in range(0,len(node_list)):
            list = node_list[i].next_link.get(item)
            if(list != None):
                for j in range(0,len(list)):
                    if(list[j].modified_at == pass_no):
                        if(list[j].previous_count < list[j].present_count):
                            actual_support = actual_support + list[j].present_count - list[j].previous_count
                        if((list[j].parent_item_bitset & last_event_item_bitset) == last_event_item_bitset):
                            modified_nodes.append(list[j])
                            if(list[j].created_at == pass_no):
                                new_created_nodes.append(list[j])
                        else:
                            q.put(list[j])
        if(actual_support < minimum_support_threshold):
            return actual_support, modified_nodes, new_created_nodes, False # not frequent

        while(q.qsize()>0):
            new_node = q.get()
            if(new_node.previous_count < new_node.present_count):
                actual_support = actual_support - new_node.present_count + new_node.previous_count
            list = new_node.next_link.get(item)
            if(list != None):
                for i in range(0,len(list)):
                    if(list[i].modified_at == pass_no):
                        if(list[i].previous_count < list[i].present_count):
                            actual_support = actual_support + list[i].present_count - list[i].previous_count
                        if((list[i].parent_item_bitset & last_event_item_bitset) == last_event_item_bitset):
                            modified_nodes.append(list[i])
                            if(list[i].created_at == pass_no):
                                new_created_nodes.append(list[i])
                        else:
                            q.put(list[i])
            if(actual_support < minimum_support_threshold):
                checked_all = False
                if(q.qsize() == 0):
                    checked_all = True
                return actual_support, modified_nodes, new_created_nodes, checked_all # not frequent
        return actual_support, modified_nodes, new_created_nodes, True

    def ItemsetExtensionForUnmodifiedPart(self, node_list, item, last_event_item_bitset):
        next_level_nodes=[]
        q = Queue()
        for i in range(0,len(node_list)):
            list = node_list[i].next_link.get(item)
            if(list != None):
                for j in range(0,len(list)):
                    if((list[j].parent_item_bitset & last_event_item_bitset) == last_event_item_bitset):
                        next_level_nodes.append(list[j])
                    else:
                        q.put(list[j])
        new_node = ""
        while(q.qsize()>0):
            new_node = q.get()
            list = new_node.next_link.get(item)
            if(list != None):
                for i in range(0,len(list)):
                    if((list[i].parent_item_bitset & last_event_item_bitset) == last_event_item_bitset):
                        next_level_nodes.append(list[i])
                    else:
                        q.put(list[i])
        return next_level_nodes

    def ItemsetExtensionFromModifiedToUnmodified(self, node_list, item, last_event_item_bitset, pass_no):
        next_level_nodes = []
        q = Queue()
        for i in range(0,len(node_list)):
            list = node_list[i].next_link.get(item)
            if(list != None):
                for j in range(0,len(list)):
                    if(list[j].modified_at < pass_no):
                        if((list[j].parent_item_bitset & last_event_item_bitset) == last_event_item_bitset):
                            next_level_nodes.append(list[j])
                        else:
                            q.put(list[j])
        new_node = ""
        while(q.qsize()>0):
            new_node = q.get()
            list = new_node.next_link.get(item)
            if(list != None):
                for i in range(0,len(list)):
                    if((list[i].parent_item_bitset & last_event_item_bitset) == last_event_item_bitset):
                        next_level_nodes.append(list[i])
                    else:
                        q.put(list[i])
        return next_level_nodes


    def GettingUnmodifiedNodes(self, bpfsptree_node, pass_no):
        unmodified_node_list = []
        for i in range(0, len(bpfsptree_node.projection_nodes)):
            if(bpfsptree_node.projection_nodes[i].modified_at != pass_no):
                unmodified_node_list.append(bpfsptree_node.projection_nodes[i])
        return unmodified_node_list


    def AdjustRecursiveExtensionEndListPtr(self, bpfsptree_node):
        bpfsptree_node.prev.next = bpfsptree_node.next
        if(bpfsptree_node.next != None):
            bpfsptree_node.next.prev = bpfsptree_node.prev
        if(bpfsptree_node.next == None):
            # previous node is becoming the leaf node
            self.current_recursive_extension_end_linked_list_ptr = bpfsptree_node.prev
        bpfsptree_node.prev = None
        bpfsptree_node.next = None
        return

    def CreateNewRecursiveExtensionEndListPtr(self, bpfsptree_node):
        self.current_recursive_extension_end_linked_list_ptr.next = bpfsptree_node
        bpfsptree_node.prev  = self.current_recursive_extension_end_linked_list_ptr
        bpfsptree_node.next = None
        self.current_recursive_extension_end_linked_list_ptr = bpfsptree_node
        return

    def PruningBPFSPBranchFromBottom(self, bpfsptree_node, minimum_support_threshold):
        unsatisfied_node = bpfsptree_node
        while(True):
            # detecting the topmost unsatisfied_node
            if(unsatisfied_node.parent_node != None and unsatisfied_node.parent_node.support<minimum_support_threshold):
                unsatisfied_node = unsatisfied_node.parent_node
            else:
                break
        save_parent_node = unsatisfied_node.parent_node
        if(unsatisfied_node.connection_type_with_parent == True):
            del unsatisfied_node.parent_node.freq_seq_ex_child_nodes[unsatisfied_node.item]
        elif(unsatisfied_node.connection_type_with_parent == False):
            del unsatisfied_node.parent_node.freq_item_ex_child_nodes[unsatisfied_node.item]
        self.BPFSPSubTreePruning(unsatisfied_node)

        if(save_parent_node.parent_node != None and len(save_parent_node.freq_seq_ex_child_nodes) == 0 and len(save_parent_node.freq_item_ex_child_nodes) == 0):
            # A new leaf node is created
            self.CreateNewRecursiveExtensionEndListPtr(save_parent_node)
        return

    def BPFSPSubTreePruning(self, bpfsptree_node):
        for key in bpfsptree_node.freq_seq_ex_child_nodes:
            self.BPFSPSubTreePruning(bpfsptree_node.freq_seq_ex_child_nodes[key])
        del bpfsptree_node.freq_seq_ex_child_nodes
        for key in bpfsptree_node.freq_item_ex_child_nodes:
            self.BPFSPSubTreePruning(bpfsptree_node.freq_item_ex_child_nodes[key])
        del bpfsptree_node.freq_item_ex_child_nodes
        if(bpfsptree_node.prev != None):
            # it was an end node before
            bpfsptree_node.prev.next = bpfsptree_node.next
            if(bpfsptree_node.next != None):
                bpfsptree_node.next.prev = bpfsptree_node.prev
            if(bpfsptree_node.next == None):
                # it is the last node
                self.current_recursive_extension_end_linked_list_ptr = bpfsptree_node.prev
                # current update korsi
        del bpfsptree_node
        return

    def GettingFirstItem(self, item_bitset):
        item = item_bitset ^ (item_bitset-1)
        item = int(floor(log(item,2)))
        return item

    def ReturnNodeCalculatedSupport(self, bpfsptree_node):
        support = 0
        for i in range(0,len(bpfsptree_node.projection_nodes)):
            support = support + bpfsptree_node.projection_nodes[i].present_count
        return support

    def CheckingIfMergedNodeInTotalNodes(self, bpfsptree_node, modified_node_list):
        pass_no = modified_node_list[0].modified_at
        for i in range(0,len(modified_node_list)):
            if(modified_node_list[i] in bpfsptree_node.projection_nodes):
                continue
            else:
                return False
        for i in range(0,len(bpfsptree_node.projection_nodes)):
            if(bpfsptree_node.projection_nodes[i].modified_at == pass_no):
                if(bpfsptree_node.projection_nodes[i] in modified_node_list):
                    continue
                else:
                    return False
        return True

    def IncrementalTreeMiner(self, modified_node_list, pattern, last_event_item_bitset, s_list, i_list, bpfsptree_node, cetables, cetablei, minimum_support_threshold, pass_no):

        actual_support, over_support,over_support1, complete_over_support = 0,0,0,0
        sequence_extended_modified_sp_tree_nodes={}
        itemset_extended_modified_sp_tree_nodes={}

        # The nodes which were not modified - getting on demand
        unmodified_node_list = []
        unmodified_node_list_calculated=False

        verdict = True
        modified_nodes = []
        new_created_nodes = []
        unmodified_nodes = []
        checked_all = False

        # heuristically what i list items  can not extend found from s list
        heuristic_s_list_wise_i_list_pruning = {}

        # sequence extension
        new_s_list = 0
        i_list_from_s_list = 0
        while s_list > 0 :
            symbol = self.GettingFirstItem(s_list)
            s_list = s_list & (s_list-1)
            verdict = True
            for j in range(0,len(pattern[len(pattern)-1])):
                if(cetables.get(pattern[len(pattern)-1][j]) == None or cetables[pattern[len(pattern)-1][j]].get(symbol) == None or cetables[pattern[len(pattern)-1][j]][symbol] < minimum_support_threshold):
                    # CEtables violation
                    verdict = False
                    break

            if(verdict == True):
                if(bpfsptree_node.freq_seq_ex_child_nodes.get(symbol) != None):
                    # already pattern in the tree , update the frequency and take decision
                    over_support, actual_support, complete_over_support, new_created_nodes, modified_nodes, checked_all  =  self.SequenceExtensionIncremental(modified_node_list, symbol, minimum_support_threshold, pass_no, bpfsptree_node.freq_seq_ex_child_nodes[symbol].support )

                    if(actual_support >= minimum_support_threshold):
                        # previously frequent and again frequent
                        # update the existing frequency only
                        bpfsptree_node.freq_seq_ex_child_nodes[symbol].support = actual_support
                        # saving the nodes for future extension
                        if(len(modified_nodes)>0):
                            sequence_extended_modified_sp_tree_nodes[symbol] = modified_nodes
                            new_s_list = new_s_list | (1<<symbol)

                        # saving the newly created nodes in the BPFSP Tree
                        for j in range(0,len(new_created_nodes)):
                            bpfsptree_node.freq_seq_ex_child_nodes[symbol].projection_nodes.append(new_created_nodes[j])
                        # completed all the works

                    else:
                        # put the support in non frequent list
                        if(checked_all == True):
                            bpfsptree_node.non_freq_seq_ex_support[symbol] = actual_support
                        # need to prune a branch
                        self.BPFSPSubTreePruning(bpfsptree_node.freq_seq_ex_child_nodes[symbol])
                        #print("pruning call disi(se): ",bpfsptree_node.freq_seq_ex_child_nodes[symbol])
                        del bpfsptree_node.freq_seq_ex_child_nodes[symbol]
                        # completed all the works
                else:
                    # new pattern for which no branch in BPFSP Tree encountered
                    if(bpfsptree_node.non_freq_seq_ex_support.get(symbol) != None):

                        # already have the previous frequency in the existing tree  - updating for the new part
                        over_support, actual_support, complete_over_support, new_created_nodes, modified_nodes, checked_all =  self.SequenceExtensionIncremental(modified_node_list, symbol, minimum_support_threshold, pass_no, bpfsptree_node.non_freq_seq_ex_support[symbol])

                        if(actual_support >= minimum_support_threshold):
                            # need to remove from the non frequent part
                            del bpfsptree_node.non_freq_seq_ex_support[symbol]

                            # create a new branch
                            bpfsptree_node.freq_seq_ex_child_nodes[symbol] = BPFSP_Tree()
                            bpfsptree_node.freq_seq_ex_child_nodes[symbol].connection_type_with_parent = True # Sequence extension
                            bpfsptree_node.freq_seq_ex_child_nodes[symbol].parent_node = bpfsptree_node
                            bpfsptree_node.freq_seq_ex_child_nodes[symbol].item = symbol
                            bpfsptree_node.freq_seq_ex_child_nodes[symbol].support = actual_support

                            # getting the previous unmodified nodes from the parent node's unmodifed nodes
                            if(unmodified_node_list_calculated == False):
                                # if unmodified_node_list not calculate first calculate it
                                unmodified_node_list = self.GettingUnmodifiedNodes(bpfsptree_node, pass_no)
                                unmodified_node_list_calculated = True
                            over_support1, unmodified_nodes_for_extension = self.SequenceExtensionForUnmodifiedPart(unmodified_node_list, symbol)

                            # saving the projection unmodified nodes in BPFSP Tree
                            for j in range(0, len(unmodified_nodes_for_extension)):
                                bpfsptree_node.freq_seq_ex_child_nodes[symbol].projection_nodes.append(unmodified_nodes_for_extension[j])

                            # getting the unmodified nodes from parent node's modified section
                            over_support2, unmodified_nodes_for_extension = self.SequenceExtensionFromModifiedToUnmodified(modified_node_list, symbol, pass_no)

                            # saving the projection unmodified nodes from modified nodes in BPFSP Tree
                            for j in range(0,len(unmodified_nodes_for_extension)):
                                bpfsptree_node.freq_seq_ex_child_nodes[symbol].projection_nodes.append(unmodified_nodes_for_extension[j])

                            # saving the projection new nodes in in BPFSP Tree
                            for j in range(0, len(modified_nodes)):
                                bpfsptree_node.freq_seq_ex_child_nodes[symbol].projection_nodes.append(modified_nodes[j])

                            # saving the modified nodes for future extension
                            sequence_extended_modified_sp_tree_nodes[symbol] = modified_nodes
                            new_s_list = new_s_list | (1<<symbol)

                            # as we have complete over support
                            # over support from (modified to modified),(unmodified to unmodified),(modified to unmodified)
                            over_support = complete_over_support + over_support1 + over_support2
                            if(over_support < minimum_support_threshold):
                                # heuristic i list pruning applied
                                heuristic_s_list_wise_i_list_pruning[symbol] = True

                            # completed all the works

                        else:
                            # updating with the new frequency - might change or not (still non frequent)
                            if(checked_all == True):
                                bpfsptree_node.non_freq_seq_ex_support[symbol] = actual_support
                            else:
                                del bpfsptree_node.non_freq_seq_ex_support[symbol]
                            # completed all the works
                    else:
                        # completely new item
                        over_support, actual_support, next_level_nodes, modified_nodes, checked_all = self.SequenceExtensionNormal(bpfsptree_node.projection_nodes, symbol, minimum_support_threshold, pass_no, bpfsptree_node.support)

                        if(actual_support >= minimum_support_threshold):

                            # create a new branch
                            bpfsptree_node.freq_seq_ex_child_nodes[symbol] = BPFSP_Tree()
                            bpfsptree_node.freq_seq_ex_child_nodes[symbol].parent_node = bpfsptree_node
                            bpfsptree_node.freq_seq_ex_child_nodes[symbol].item = symbol
                            bpfsptree_node.freq_seq_ex_child_nodes[symbol].connection_type_with_parent = True # Sequence extension
                            bpfsptree_node.freq_seq_ex_child_nodes[symbol].support = actual_support
                            bpfsptree_node.freq_seq_ex_child_nodes[symbol].projection_nodes = next_level_nodes

                            # saving the nodes for future extension
                            sequence_extended_modified_sp_tree_nodes[symbol] = modified_nodes
                            new_s_list = new_s_list | 1<<symbol

                            # calculated over complete tree - valid over support
                            if(over_support < minimum_support_threshold):
                                heuristic_s_list_wise_i_list_pruning[symbol] = True

                            # completed all the works
                        else:
                            # save in the TLB
                            if(checked_all == True):
                                bpfsptree_node.non_freq_seq_ex_support[symbol] = actual_support
                            # completed all the works
            else:
                # Extension is not possible with this item
                if(bpfsptree_node.freq_seq_ex_child_nodes.get(symbol) != None):
                    # Need to remove the pattern from the tree
                    self.BPFSPSubTreePruning(bpfsptree_node.freq_seq_ex_child_nodes[symbol])
                    #print("Pruning call disi(se): ",bpfsptree_node.freq_seq_ex_child_nodes[symbol])
                    del bpfsptree_node.freq_seq_ex_child_nodes[symbol]
                    # completed all the works
                else:
                    # not in the tree
                    if(bpfsptree_node.non_freq_seq_ex_support.get(symbol) != None):
                        # in the TLB
                        # removing from there
                        del bpfsptree_node.non_freq_seq_ex_support[symbol]
                        # there was also a way not doing now: checking if there was modification beneath it
                        # completed all the works
                    else:
                        # not in the TLB also
                        # completed all the works
                        pass

        # item set extension
        new_i_list = 0
        while i_list>0:

            symbol = self.GettingFirstItem(i_list)
            i_list = i_list & (i_list-1)

            # heuristic i list checking
            if(heuristic_s_list_wise_i_list_pruning.get(symbol) == None):
                # cetable i pruning
                verdict = True
                for j in range(0,len(pattern[len(pattern)-1])):
                    if(symbol <= pattern[len(pattern)-1][j] or cetablei.get(pattern[len(pattern)-1][j]) == None or cetablei[pattern[len(pattern)-1][j]].get(symbol) == None or  cetablei[pattern[len(pattern)-1][j]][symbol] < minimum_support_threshold):
                        verdict = False
                        break
                if(verdict == True):
                    # need to check for itemset extension
                    if(bpfsptree_node.freq_item_ex_child_nodes.get(symbol) != None):
                        # already in the frequent pattern tree
                        actual_support, modified_nodes, new_created_nodes, checked_all = self.ItemsetExtensionIncremental(modified_node_list, symbol, minimum_support_threshold, pass_no, last_event_item_bitset, bpfsptree_node.freq_item_ex_child_nodes[symbol].support)
                        if(actual_support >= minimum_support_threshold):
                            # already frequent. Update the new frequency
                            bpfsptree_node.freq_item_ex_child_nodes[symbol].support = actual_support
                            # keeping the modified nodes for further extension
                            if(len(modified_nodes) > 0):
                                itemset_extended_modified_sp_tree_nodes[symbol]= modified_nodes
                                new_i_list = new_i_list | (1<<symbol)

                            # updating the BPFSP Tree with new nodes
                            for j in range(0,len(new_created_nodes)):
                                bpfsptree_node.freq_item_ex_child_nodes[symbol].projection_nodes.append(new_created_nodes[j])
                            # completed all the works
                        else:
                            # a frequent pattern became infrequent
                            # update in the TLB
                            if(checked_all == True):
                                bpfsptree_node.non_freq_item_ex_support[symbol] = actual_support
                            # pruning a subtree
                            self.BPFSPSubTreePruning(bpfsptree_node.freq_item_ex_child_nodes[symbol])
                            #print("Pruning call disi: ", bpfsptree_node.freq_item_ex_child_nodes[symbol])
                            del bpfsptree_node.freq_item_ex_child_nodes[symbol]

                            # completed all the works
                    else:
                        # not in the frequent pattern tree
                        if(bpfsptree_node.non_freq_item_ex_support.get(symbol) != None):
                            # it is in the TLB
                            actual_support, modified_nodes, new_created_nodes, checked_all = self.ItemsetExtensionIncremental(modified_node_list, symbol, minimum_support_threshold, pass_no, last_event_item_bitset, bpfsptree_node.non_freq_item_ex_support[symbol])

                            if(actual_support >= minimum_support_threshold):
                                # previously non frequent was in TLB getting frequent now
                                del bpfsptree_node.non_freq_item_ex_support[symbol]

                                # creating a new BPFSP Tree node
                                bpfsptree_node.freq_item_ex_child_nodes[symbol] = BPFSP_Tree()
                                bpfsptree_node.freq_item_ex_child_nodes[symbol].parent_node = bpfsptree_node
                                bpfsptree_node.freq_item_ex_child_nodes[symbol].item = symbol
                                bpfsptree_node.freq_item_ex_child_nodes[symbol].support = actual_support
                                bpfsptree_node.freq_item_ex_child_nodes[symbol].connection_type_with_parent = False # Itemset extension

                                # getting the previous unmodified nodes from the parent node's unmodifed nodes
                                if(unmodified_node_list_calculated == False):
                                    # if unmodified_node_list not calculate first calculate it
                                    unmodified_node_list = self.GettingUnmodifiedNodes(bpfsptree_node, pass_no)
                                    unmodified_node_list_calculated = True

                                unmodified_nodes = self.ItemsetExtensionForUnmodifiedPart(unmodified_node_list, symbol, last_event_item_bitset)


                                # saving the previous unmodified nodes
                                for j in range(0,len(unmodified_nodes)):
                                    bpfsptree_node.freq_item_ex_child_nodes[symbol].projection_nodes.append(unmodified_nodes[j])

                                # getting the unmodified nodes from the modified nodes
                                unmodified_nodes = self.ItemsetExtensionFromModifiedToUnmodified(modified_node_list, symbol, last_event_item_bitset, pass_no)

                                for j in range(0,len(unmodified_nodes)):
                                    bpfsptree_node.freq_item_ex_child_nodes[symbol].projection_nodes.append(unmodified_nodes[j])

                                # saving the new nodes
                                for j in range(0, len(modified_nodes)):
                                    bpfsptree_node.freq_item_ex_child_nodes[symbol].projection_nodes.append(modified_nodes[j])

                                # saving the modified nodes for future extension
                                itemset_extended_modified_sp_tree_nodes[symbol] = modified_nodes
                                new_i_list = new_i_list | (1<<symbol)

                                # completed all the works
                            else:
                                # previously was infrequent, still infrequent, update in TLB with new frequency
                                if(checked_all == True):
                                    bpfsptree_node.non_freq_item_ex_support[symbol] = actual_support
                                else:
                                    # the support is not properly calculated
                                    del bpfsptree_node.non_freq_item_ex_support[symbol]
                                # completd all the works
                        else:
                            # it is not in the TB
                            actual_support, next_level_nodes, modified_nodes, checked_all = self.ItemsetExtensionNormal(bpfsptree_node.projection_nodes, symbol, minimum_support_threshold, pass_no, last_event_item_bitset, bpfsptree_node.support)

                            if( actual_support >= minimum_support_threshold):
                                # creating a new BPFSP Tree node
                                bpfsptree_node.freq_item_ex_child_nodes[symbol] = BPFSP_Tree()
                                bpfsptree_node.freq_item_ex_child_nodes[symbol].parent_node = bpfsptree_node
                                bpfsptree_node.freq_item_ex_child_nodes[symbol].item = symbol
                                bpfsptree_node.freq_item_ex_child_nodes[symbol].support = actual_support
                                bpfsptree_node.freq_item_ex_child_nodes[symbol].projection_nodes = next_level_nodes
                                bpfsptree_node.freq_item_ex_child_nodes[symbol].connection_type_with_parent = False # Itemset extension

                                #saving the nodes for further extension
                                itemset_extended_modified_sp_tree_nodes[symbol] = modified_nodes
                                new_i_list = new_i_list | (1<<symbol)

                            else:
                                if(checked_all == True):
                                    bpfsptree_node.non_freq_item_ex_support[symbol] = actual_support
                else:
                    # no need to check for itemset extension
                    if(bpfsptree_node.freq_item_ex_child_nodes.get(symbol) != None):
                        # need to prune a subtree from BPFSP Tree
                        self.BPFSPSubTreePruning(bpfsptree_node.freq_item_ex_child_nodes[symbol])
                        #print("Pruning call disi: ", bpfsptree_node.freq_item_ex_child_nodes[symbol])
                        del bpfsptree_node.freq_item_ex_child_nodes[symbol]
                        # completed all the works
                    else:
                        if(bpfsptree_node.non_freq_item_ex_support.get(symbol) != None):
                            del bpfsptree_node.non_freq_item_ex_support[symbol]
                            # completed all the works
                        else:
                            # non frequent, non in TLB also, nothing to do
                            # completed all the works
                            pass
        if(len(bpfsptree_node.freq_seq_ex_child_nodes) > 0 or len(bpfsptree_node.freq_item_ex_child_nodes) > 0):
            # this node is not end of recursive extension
            if(bpfsptree_node.prev != None):
                # it was an end previously - need to remove it
                self.AdjustRecursiveExtensionEndListPtr(bpfsptree_node)
                # completed all the works
        else:
            # this is the end of recursive extension
            if(bpfsptree_node.prev == None):
                # need to create the end linked list pointer
                self.CreateNewRecursiveExtensionEndListPtr(bpfsptree_node)
                # completed all the works

        # Recursive Extension
        # sequence Extension

        i_list_from_s_list = new_s_list
        for key in sequence_extended_modified_sp_tree_nodes:
            while i_list_from_s_list>0:
                value = self.GettingFirstItem(i_list_from_s_list)
                if(value > key):
                    break
                i_list_from_s_list = i_list_from_s_list & (i_list_from_s_list-1)
            pattern.append([key])
            self.IncrementalTreeMiner(sequence_extended_modified_sp_tree_nodes[key], pattern, 1<<key, new_s_list, i_list_from_s_list, bpfsptree_node.freq_seq_ex_child_nodes[key], cetables, cetablei, minimum_support_threshold, pass_no)
            del pattern[len(pattern)-1]
        # itemset extension
        sz = len(pattern[len(pattern)-1])
        for key in itemset_extended_modified_sp_tree_nodes:
            while new_i_list > 0:
                value = self.GettingFirstItem(new_i_list)
                if(value > key):
                    break
                new_i_list = new_i_list & (new_i_list-1)
            pattern[len(pattern)-1].append(key)
            self.IncrementalTreeMiner(itemset_extended_modified_sp_tree_nodes[key], pattern, last_event_item_bitset | 1<< key, new_s_list, new_i_list, bpfsptree_node.freq_item_ex_child_nodes[key], cetables, cetablei, minimum_support_threshold, pass_no)
            del pattern[len(pattern)-1][sz]
        return

    def PrintRecursiveLinks(self,bpfsptree_node):
        temp = bpfsptree_node
        print("item = ", bpfsptree_node.item, bpfsptree_node, temp.prev,temp.next)
        if(bpfsptree_node.parent_node != ""):
            print("parent = ",bpfsptree_node.parent_node.item)
        while(temp != None):
            temp = temp.prev
            if(temp == None or temp.parent_node == ""):
                break
            else:
                print("prev item ",temp.item, "parent item ",temp.parent_node.item,temp,temp.prev,temp.next)
                if(temp.parent_node != "" and temp.parent_node.parent_node != "" and temp.parent_node.parent_node != ""  ):
                    print("parent parent  = ",temp.parent_node.parent_node.item)
        temp = bpfsptree_node
        while(temp != None):
            temp = temp.next
            if(temp == None):
                break
            else:
                print("next item = ",temp.item, "parent item ",temp.parent_node.item)

    def InitiateRemovingFromBottom(self, recursive_extension_end_linked_list_ptr, minimum_support_threshold):
        # the root starter will be sent: so start from the next
        save_previous = ""
        while True:
            recursive_extension_end_linked_list_ptr = recursive_extension_end_linked_list_ptr.next
            if(recursive_extension_end_linked_list_ptr == None):
                break # completed all the checking
            if(recursive_extension_end_linked_list_ptr.support < minimum_support_threshold):
                save_previous = recursive_extension_end_linked_list_ptr.prev
                self.PruningBPFSPBranchFromBottom(recursive_extension_end_linked_list_ptr, minimum_support_threshold)
                recursive_extension_end_linked_list_ptr = save_previous
        return
    def PrintNodeList(self,node_list):
        for i in range(0,len(node_list)):
            print("node id = ",node_list[i].node_id," support = ",node_list[i].present_count)
            self.PrintNextLink(node_list[i])
    def PrintNextLink(self,node):
        for key in node.next_link:
            print("key = ",key)
            for i in range(0,len(node.next_link[key])):
                print(node.next_link[key][i].node_id)
            print()
