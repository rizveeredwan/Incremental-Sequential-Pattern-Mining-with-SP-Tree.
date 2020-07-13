import sys
from math import log,floor

from INC_SP_Tree import INC_SP_Tree
from BPFSP_Tree import BPFSP_Tree
from Sequence_Summarizer_Structure import SequenceSummarizerStructure

class Main:
    def __init__(self):
        self.new_input=0
        self.seq_sum_dict={}
        self.pass_no = 0
        self.inc_sp_tree_root = INC_SP_Tree()
        self.cetables={}
        self.cetablei={}

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
        for i in range(0,self.new_input):
            line = input()
            sid, processed_sequence = self.ProcessSequence(line)
            value = self.seq_sum_dict.get(sid)
            new_items.clear()
            if(value == None):
                #new sequence
                self.seq_sum_dict[sid] = SequenceSummarizerStructure()
                end_sp_tree_node = self.inc_sp_tree_root.Insert(self.pass_no, self.inc_sp_tree_root, processed_sequence, 0, 0, 0, self.seq_sum_dict[sid], 0, new_items)
                self.seq_sum_dict[sid].sp_tree_end_node_ptr = end_sp_tree_node
                self.seq_sum_dict[sid].UpdateCETables(new_items, self.cetables, self.seq_sum_dict[sid], -1)
                self.seq_sum_dict[sid].last_event_no = len(processed_sequence)-1
            else:
                #old sequence
                end_sp_tree_node = self.inc_sp_tree_root.Insert(self.pass_no, value.sp_tree_end_node_ptr , processed_sequence, 0, 0, value.last_event_no+1, value, 0, new_items)
                value.sp_tree_end_node_ptr = end_sp_tree_node
                value.UpdateCETablei(new_items, self.cetablei, value)
                value.last_event_no = value.last_event_no + len(processed_sequence)
        print("completed")


sys.stdin = open('input.txt','r')
#sys.stdout = open('output.txt','w')

main = Main()
main.DatabaseInput()

"""
value = 1<<65789
bit_position = int(floor(log(value,2)))
print(bit_position)
"""

#value  = 1<<100000
#print(value)
#print(value - 1)
