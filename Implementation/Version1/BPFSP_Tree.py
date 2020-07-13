#Bi directional projection based frequent sequential pattern tree
class BPFSP_Tree:
    def __init__(self):
        self.parent_node=""
        self.item=""
        self.sp_tree_node_list=[]
        self.frequency=0
        self.seq_ex={}
        self.item_ex={}
    
