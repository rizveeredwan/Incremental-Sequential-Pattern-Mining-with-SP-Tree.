class ItemEventCombination:
    def __init__(self,item,event):
        self.item = item
        self.event = event

class INC_SP_Tree:
    def __init__(self):
        self.parent_node=None
        self.created_at = 0
        self.modified_at = 0
        self.child_link={}
        self.previous_count = 0
        self.present_count = 0

    def Insert(self, pass_no, sp_tree_node, processed_sequence,event_no,item_no,actual_event_no):
        if(event_no>=len(processed_sequence)):
            return sp_tree_node
        if(item_no >= len(processed_sequence[event_no])):
            return self.Insert(pass_no,sp_tree_node,processed_sequence,event_no+1,0,actual_event_no)
        item = processed_sequence[event_no][item_no]
        item_event_combination = ItemEventCombination(item,actual_event_no+event_no)
        node = sp_tree_node.child_link.get(item_event_combination)
        if(node == None):
            sp_tree_node.child_link[item_event_combination] = INC_SP_Tree()
            sp_tree_node.child_link[item_event_combination].created_at = pass_no
            sp_tree_node.child_link[item_event_combination].parent_node = sp_tree_node
            sp_tree_node.child_link[item_event_combination].previous_count = 0
            sp_tree_node.child_link[item_event_combination].present_count = 0
            node = sp_tree_node.child_link[item_event_combination]
        else:
            if(node.modified_at<pass_no):
                node.present_count = node.previous_count
        node.present_count = node.present_count + 1
        return self.Insert(pass_no, node, processed_sequence, event_no, item_no+1, actual_event_no)

    def UpdateModifiedPath(self,node):
        pass 
