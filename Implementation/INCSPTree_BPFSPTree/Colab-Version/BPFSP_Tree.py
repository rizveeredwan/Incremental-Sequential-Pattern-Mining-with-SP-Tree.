#Bi directional projection based frequent sequential pattern tree
class BPFSP_Tree:
    def __init__(self):
        self.parent_node=""
        self.item=""
        self.support=0
        self.connection_type_with_parent = None

        self.projection_nodes=[]

        self.freq_seq_ex_child_nodes={}
        self.freq_item_ex_child_nodes={}

        self.non_freq_seq_ex_support={}
        self.non_freq_item_ex_support={}

        self.prev = None
        self.next = None
        # self.recursive_extension_end_linked_list_ptr=None
