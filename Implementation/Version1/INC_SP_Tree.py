from queue import Queue
from BPFSP_Tree import BPFSP_Tree

class ItemEventCombination:
    def __init__(self,item,event):
        self.item = item
        self.event = event

class INC_SP_Tree:
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
        if(event_no>=len(processed_sequence)):
            return sp_tree_node
        if(item_no >= len(processed_sequence[event_no])):
            # updating to perform CETable_i operation
            return self.Insert(pass_no,sp_tree_node,processed_sequence,event_no+1,0,actual_event_no,sequence_summarizer_structure, 0, new_items)
        item = processed_sequence[event_no][item_no]
        item_event_combination = ItemEventCombination(item,actual_event_no+event_no+1)
        node = sp_tree_node.child_link.get(item_event_combination)
        if(node == None):
            sp_tree_node.child_link[item_event_combination] = INC_SP_Tree()
            sp_tree_node.child_link[item_event_combination].item = item
            sp_tree_node.child_link[item_event_combination].event_no = event_no + actual_event_no + 1
            sp_tree_node.child_link[item_event_combination].created_at = pass_no
            sp_tree_node.child_link[item_event_combination].parent_node = sp_tree_node
            sp_tree_node.child_link[item_event_combination].previous_count = 0
            sp_tree_node.child_link[item_event_combination].present_count = 0
            sp_tree_node.child_link[item_event_combination].parent_item_bitset = event_bitset
            node = sp_tree_node.child_link[item_event_combination]

        # First, mid, last updating to calculate CETable_s
        self.SequenceSummarizerSequenceExtensionUpdate(sequence_summarizer_structure, item, event_no)
        # updating the sequence summarizer table to perform CETable_i
        if(item_no>=1):
            self.SequenceSummarizerItemsetExtensionUpdate(sequence_summarizer_structure, item, event_bitset)
        #Tracking the new symbols
        if(new_items.get(item) == None):
            new_items[item]=True
        return self.Insert(pass_no, node, processed_sequence, event_no, item_no+1, actual_event_no, sequence_summarizer_structure, event_bitset | (1<<item), new_items)

    def UpdatePath(self, node, pass_no, next_link_nodes):
        if(node == None):
            return
        if(node.modified_at<pass_no):
            node.modified_at=pass_no
            node.previous_count=node.present_count
        node.present_count=node.present_count+1

        for key in next_link_nodes:
            value = node.next_link.get(key)
            if(value == None):
                node.next_link[key]=[]
            node.next_link[key].append(next_link_nodes[key])

        if(node.created_at == pass_no):
            next_link_nodes[node.item]=node
        else:
            if(next_link_nodes.get(node.item) != None):
                del next_link_nodes[node.item]
        self.UpdatePath(node.parent_node, pass_no, next_link_nodes)
        return

    def SequenceExtensionNormal(self, node_list, item, minimum_support_threshold, pass_no, current_maximum_support):
        actual_support = 0
        over_support = current_maximum_support
        new_node = ""
        next_level_nodes=[]
        failed_nodes = []
        list = []
        for i in range(0,len(node_list)):
            list = node_list[i].next_link.get(item)
            over_support = over_support - node_list[i].present_count
            if(list != None):
                for j in range(0,len(list)):
                    new_node = list[j]
                    over_support = over_support + new_node.present_count
                    if(new_node.event_no > node_list[i].event_no):
                        actual_support = actual_support + new_node.present_count
                        next_level_nodes.append(new_node)
                    else:
                        failed_nodes.append(new_node)
            if(over_support < minimum_support_threshold):
                return over_support, actual_support, next_level_nodes # not satisfied

        if(over_support < minimum_support_threshold):
            return over_support, actual_support, next_level_nodes # not satisfied

        for i in range(0,len(failed_nodes)):
            list = failed_nodes.next_link.get(item)
            if(list != None):
                for j in range(0,len(list)):
                    new_node = list[j]
                    if(new_node != None):
                        actual_support = actual_support + new_node.present_count
                        next_level_nodes.append(new_node)
        return over_support, actual_support, next_level_nodes

    def SequenceExtensionIncremental(self, node_list, item, minimum_support_threshold, pass_no, current_support):
        actual_support = current_support
        over_support = current_support
        list = []
        new_node = ""
        failed_nodes=[]
        modified_nodes=[]
        for i in range(0,len(node_list)):
            list = node_list[i].next_link.get(item)
            if(list != None):
                for j in range(0,len(list)):
                    new_node = list[j]
                    if(new_node.modified_at == pass_no):
                        over_support = over_support + new_node.present_count - new_node.previous_count
                        if(new_node.event_no>node_list[i].event_no):
                            actual_support = actual_support + new_node.present_count - new_node.previous_count
                            modified_nodes.append(new_node)
                        else:
                            failed_nodes.append(new_node)
        if(over_support < minimum_support_threshold):
            return over_support, actual_support, next_level_new_nodes, modified_nodes # Not frequent
        for i in range(0,len(failed_nodes)):
            list = failed_nodes[i].next_link.get(item)
            if(list != None):
                if(failed_nodes[i].modified_at == pass_no):
                    actual_support = actual_support + failed_nodes[i].present_count - failed_nodes[i].previous_count
                    modified_nodes.append(failed_nodes[i])
        return over_support, actual_support, modified_nodes


    def ItemsetExtensionNormal(self, node_list, item, minimum_support_threshold, pass_no, last_event_item_bitset, current_maximum_support):
        #last event item bitset - all the previous items bitset representation
        actual_support = current_maximum_support
        q = Queue()
        new_node = ""
        next_level_nodes = []
        list = []
        for i in range(0,len(node_list)):
            actual_support = actual_support - node_list[i].support
            list = node_list[i].next_link.get(item)
            for j in range(0,len(list)):
                new_node = list[j]
                actual_support = actual_support + new_node.present_count
                if(new_node.event_no == node_list[i].event_no):
                    next_level_nodes.append(new_node)
                else:
                    q.put(new_node)
            if(actual_support < minimum_support_threshold):
                return actual_support, next_level_nodes #already failed

        if(actual_support < minimum_support_threshold):
            return actual_support, next_level_nodes #already failed

        while(q.qsize()>0):
            new_node = q.get()
            actual_support = actual_support - new_node.present_count
            list = new_node.next_link.get(item)
            for i in range(0,len(list)):
                actual_support = actual_support + list[i].present_count
                if((list[i].parent_item_bitset & last_event_item_bitset) == 0):
                    next_level_nodes.append(list[i])
                else:
                    q.put(list[i])
            if(actual_support < minimum_support_threshold):
                return actual_support, next_level_nodes

        return actual_support, next_level_nodes

    def ItemsetExtensionIncremental(self, node_list, item, minimum_support_threshold, pass_no, last_event_item_bitset, current_support):
        actual_support = current_support
        list = []
        modified_nodes = []
        q=Queue()
        for i in range(0,len(node_list)):
            list = node_list[i].next_link.get(item)
            if(list != None):
                for j in range(0,len(list)):
                    if(list[j].modified_at == pass_no):
                        actual_support = actual_support + list[j].present_count - list[j].previous_count
                        if(list[j].event_no ==  node_list[i].event_no):
                            modified_nodes.append(list[j])
                        else:
                            q.put(list[j])
        if(actual_support < minimum_support_threshold):
            return actual_support, next_level_nodes #not frequent

        while(q.qsize()>0):
            new_node = q.get()
            actual_support = actual_support - new.present_count + new_node.previous_count
            list = new_node.next_link.get(item)
            for i in range(0,len(list)):
                if(list[i].modified_at == pass_no):
                    actual_support = actual_support + list[i].present_count - list[i].previous_count
                    if((list[i].parent_item_bitset & last_event_item_bitset) == 0):
                        modified_nodes.append(list[i])
                    else:
                        q.put(list[i])
            if(actual_support < minimum_support_threshold):
                return actual_support, next_level_nodes
        return actual_support, modified_nodes

    def IncrementalTreeMiner(self, modified_node_list, pattern, last_event_item_bitset, s_list, i_list, bpfsptree_node, cetables, cetablei, minimum_support_threshold, pass_no):
        actual_support, over_support = 0,0
        sequence_extended_modified_sp_tree_nodes={}
        itemset_extended_modified_sp_tree_nodes={}

        verdict = True
        for i in range(0,len(s_list)):
            verdict = True
            for j in range(0,len(len(pattern)-1)):
                if(cetables.get(pattern[len(pattern)-1][j]) != None and cetables[pattern[len(pattern)-1][j]][s_list[j]] > minimum_support_threshold):
                    continue
                else:
                    verdict = False
                    break
            if(verdict == True):
                if(bpfsptree_node.freq_seq_ex_child_nodes.get(s_list[i]) != None):
                    #already pattern in the tree , update the frequency and take decision
                    over_support, actual_support, modified_nodes =  self.SequenceExtensionIncremental(modified_node_list, s_list[i], minimum_support_threshold, pass_no, bpfsptree_node.freq_seq_ex_child_nodes[s_list[i]].support )
                    if(actual_support >= minimum_support_threshold):
                        # update the existing frequency only
                        bpfsptree_node.freq_seq_ex_child_nodes[s_list[i]].support = actual_support
                        # saving the nodes for future extension
                        sequence_extended_modified_sp_tree_nodes[s_list[i]] = modified_nodes
                    else:
                        # put the support in non frequent list
                        bpfsptree_node.non_freq_seq_ex_support[s_list[i]] = actual_support
                        # need to prune a branch
                        pass
                else:
                    #new pattern encountered
                    if(bpfsptree_node.non_freq_seq_ex_support.get(s_list[i]) != None):
                        #already calculated in the existing tree  - updating for the new part
                        over_support, actual_support, modified_nodes =  self.SequenceExtensionIncremental(modified_node_list, s_list[i], minimum_support_threshold, pass_no, bpfsptree_node.non_freq_seq_ex_support[s_list[i]])
                        if(actual_support >= minimum_support_threshold):
                            #need to remove from the non frequent part
                            del bpfsptree_node.non_freq_seq_ex_support[s_list[i]]
                            #create a new branch
                            bpfsptree_node.freq_seq_ex_child_nodes[s_list[i]] = BPFSP_Tree()
                            bpfsptree_node.freq_seq_ex_child_nodes[s_list[i]].parent_node = bpfsptree_node
                            bpfsptree_node.freq_seq_ex_child_nodes[s_list[i]].item = s_list[i]
                            bpfsptree_node.freq_seq_ex_child_nodes[s_list[i]].support = actual_support
                            # saving the nodes for future extension
                            sequence_extended_modified_sp_tree_nodes[s_list[i]] = modified_nodes

                        else:
                            #updating with the new frequency - might change or not
                            bpfsptree_node.non_freq_seq_ex_support[s_list[i]] = actual_support
                    else:
                        # completely new item
                        over_support, actual_support, next_level_nodes = self.SequenceExtensionNormal(bpfsptree_node.projection_nodes, s_list[i], minimum_support_threshold, pass_no, bpfsptree_node.support)
                        if(actual_support >= minimum_support_threshold):
                            #create a new branch
                            bpfsptree_node.freq_seq_ex_child_nodes[s_list[i]] = BPFSP_Tree()
                            bpfsptree_node.freq_seq_ex_child_nodes[s_list[i]].parent_node = bpfsptree_node
                            bpfsptree_node.freq_seq_ex_child_nodes[s_list[i]].item = s_list[i]
                            bpfsptree_node.freq_seq_ex_child_nodes[s_list[i]].support = actual_support
                            # saving the nodes for future extension
                            sequence_extended_modified_sp_tree_nodes[s_list[i]] = modified_nodes
                        else:
                            # save in the TLB
                            bpfsptree_node.non_freq_seq_ex_support[s_list[i]] = actual_support
            else:
                # Extension is not possible with this item
                if(bpfsptree_node.freq_seq_ex_child_nodes.get(s_list[i]) != None):
                    # Need to remove the pattern from the tree
                    pass
                else:
                    pass
                pass
