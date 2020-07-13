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
