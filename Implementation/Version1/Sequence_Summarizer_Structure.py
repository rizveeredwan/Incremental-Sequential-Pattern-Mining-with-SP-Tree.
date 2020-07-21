# Sequence Summarizer Class
from math import log,floor

class SequenceSummarizerStructure:
    def __init__(self):
        self.sp_tree_end_node_ptr=""
        self.sequence_summarizer_table={}
        self.last_event_no=""

    def UpdateCETables(self, new_items, cetables, sequence_summarizer_structure, previous_max_event_no):
        value = ""
        for item1 in sequence_summarizer_structure.sequence_summarizer_table:
            for item2 in new_items:
                if(sequence_summarizer_structure.sequence_summarizer_table[item1][0][0]<sequence_summarizer_structure.sequence_summarizer_table[item2][0][2]):
                    if(previous_max_event_no == -1):
                        # first time the sequence appeared
                        if(cetables.get(item1) == None):
                            cetables[item1]={}
                        if(cetables[item1].get(item2) == None):
                            cetables[item1][item2]=0
                        cetables[item1][item2] = cetables[item1][item2] + 1
                    else:
                        if(sequence_summarizer_structure.sequence_summarizer_table[item2][0][1] <sequence_summarizer_structure.sequence_summarizer_table[item1][0][0]):
                            # item1 appeared in this batch
                            if(cetables.get(item1) == None):
                                cetables[item1]={}
                            if(cetables[item1].get(item2) == None):
                                cetables[item1][item2]=0
                            cetables[item1][item2] = cetables[item1][item2] + 1
        for item in new_items:
            sequence_summarizer_structure.sequence_summarizer_table[item][0][1]=sequence_summarizer_structure.sequence_summarizer_table[item][0][2]
        return

    # # DEBUG:
    def ShowSequenceSummarizerStructure(self,  sequence_summarizer_structure):
        for key in sequence_summarizer_structure.sequence_summarizer_table:
            print(key,sequence_summarizer_structure.sequence_summarizer_table[key][0],sequence_summarizer_structure.sequence_summarizer_table[key][1])
        return

    def UpdateCETablei(self, new_items, cetablei, sequence_summarizer_structure):
        result = ""
        pos = ""
        value = ""
        index = ""
        value1 = ""
        for item in new_items:
            result = sequence_summarizer_structure.sequence_summarizer_table[item][1][1] & (sequence_summarizer_structure.sequence_summarizer_table[item][1][0] ^ sequence_summarizer_structure.sequence_summarizer_table[item][1][1]) # getting the changes
            if(result != 0):
                if(cetablei.get(item) == None):
                    cetablei[item]={}
                while(result != 0):
                    value = (result & (result-1)) #LSB off
                    value1 = value
                    value = result ^ value # Got set bit
                    value = int(floor(log(value,2)))
                    if(cetablei[item].get(value) == None):
                        cetablei[item][value]=0
                    cetablei[item][value]=cetablei[item][value]+1
                    result = value1
        for item in new_items:
            sequence_summarizer_structure.sequence_summarizer_table[item][1][0] = sequence_summarizer_structure.sequence_summarizer_table[item][1][1]
            sequence_summarizer_structure.sequence_summarizer_table[item][1][1] = 0
        return
