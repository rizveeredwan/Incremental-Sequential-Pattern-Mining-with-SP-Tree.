#Bi directional projection based frequent sequential pattern tree
class BPFSP_Tree:
    def __init__(self):
        self.parent_node=""
        self.item=""
        self.support=0

        self.projection_nodes=[]

        self.freq_seq_ex_child_nodes={}
        self.freq_item_ex_child_nodes={}

        self.non_freq_seq_ex_support={}
        self.non_freq_item_ex_support={}
