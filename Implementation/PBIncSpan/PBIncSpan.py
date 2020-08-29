from PBIncSpanTree import PrefixTree
from math import ceil
import sys

class PBIncSpan:
    def __init__(self, percentage_threshold):
        self.D_prime = {}
        self.LDB = {}
        self.previous_dump = {}
        self.percentage_threshold = percentage_threshold
        self.root = PrefixTree()

    def ReadDB(self, file_name):
        self.LDB.clear()
        self.previous_dump.clear()
        with open(file_name, 'r') as file:
            lines = file.readlines()
            for i in range(0,len(lines)):
                sid, processed_sequence = self.ProcessSequence(lines[i])
                if(self.D_prime.get(sid) == None):
                    self.D_prime[sid] = processed_sequence
                    self.LDB[sid] = processed_sequence
                    self.root.pseudo_projection.append([sid,""])
                    self.root.frequency = len(self.root.pseudo_projection)
                else:
                    self.previous_dump[sid] = []
                    for j in range(0,len(self.D_prime[sid])):
                        self.previous_dump[sid].append(self.D_prime[sid][j])
                    for j in range(0,len(processed_sequence)):
                        self.D_prime[sid].append(processed_sequence[j])
                    self.LDB[sid] = self.D_prime[sid]
        return

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

    def TwoEventMatching(self, event1,event2):
        if(len(event1) == 0):
            return True
        ptr1, ptr2 = 0,0
        while(True):
            if(ptr1 >= len(event1)):
                return True # event1 in event2
            if(ptr2>=len(event2)):
                return False
            if(event2[ptr2] > event1[ptr1]):
                return False
            if(event1[ptr1] == event2[ptr2]):
                ptr1=ptr1+1
            ptr2=ptr2+1


    def ScanningTheDBToGetFrequency(self, pseudo_projection, last_event_items):
        item_count = {}
        for i in range(0,len(pseudo_projection)):
            if(pseudo_projection[i][1] == ""):
                event_no = 0
            else:
                event_no = pseudo_projection[i][1]
            temp_dict = {}
            for j in range(event_no,len(self.D_prime[pseudo_projection[i][0]])):
                # same event count
                verdict = self.TwoEventMatching(last_event_items, self.D_prime[pseudo_projection[i][0]][j])
                if(verdict == True and len(last_event_items)>0):
                    for k in range(0,len(self.D_prime[pseudo_projection[i][0]][j])):
                        if(self.D_prime[pseudo_projection[i][0]][j][k] > last_event_items[len(last_event_items)-1]):
                            temp_dict['_'+str(self.D_prime[pseudo_projection[i][0]][j][k])] = True
                if(j>event_no or len(last_event_items) == 0):
                    for k in range(0,len(self.D_prime[pseudo_projection[i][0]][j])):
                        temp_dict[str(self.D_prime[pseudo_projection[i][0]][j][k])] = True
            for key in temp_dict:
                if(item_count.get(key) == None):
                    item_count[key] = 0
                item_count[key] = item_count[key] + 1
        return item_count

    def ScanningTheDBToGetProjection(self,pseudo_projection, item, last_event_items, type):
        next_pseudo_projection=[]
        for i in range(0,len(pseudo_projection)):
            if(pseudo_projection[i][1] == ""):
                event_no = -1
            else:
                event_no = pseudo_projection[i][1]
            if(type == 0):
                # sequence extension
                for j in range(event_no+1, len(self.D_prime[pseudo_projection[i][0]])):
                    if(item in self.D_prime[pseudo_projection[i][0]][j]):
                        next_pseudo_projection.append([pseudo_projection[i][0],j])
                        break
            elif(type == 1):
                for j in range(event_no, len(self.D_prime[pseudo_projection[i][0]])):
                    if(item in self.D_prime[pseudo_projection[i][0]][j] and self.TwoEventMatching(last_event_items, self.D_prime[pseudo_projection[i][0]][j]) == True):
                        next_pseudo_projection.append([pseudo_projection[i][0],j])
                        break
        return next_pseudo_projection

    def WidthPruning(self, node):
        for i in range(0,len(node.pseudo_projection)):
            if(self.LDB.get(node.pseudo_projection[i][0]) != None):
                return False
        return True

    def ExtractingTheModifiedProjections(self, node):
        projections = []
        for i in range(0, len(node.pseudo_projection)):
            if(self.LDB.get(node.pseudo_projection[i][0]) != None):
                projections.append(node.pseudo_projection[i])
        return projections

    def ReturnFrequentItemset(self, temp, minimum_support_threshold):
        ies = {}
        for key in temp:
            if(temp[key] >= minimum_support_threshold):
                ies[key] = temp[key]
        return ies

    def GettingTheIESP(self, pseudo_projection_in_ldb):
        iesp = {}
        for i in range(0,len(pseudo_projection_in_ldb)):
            event_no = pseudo_projection_in_ldb[i][1]
            sid = pseudo_projection_in_ldb[i][0]
            if(self.previous_dump.get(sid) != None):
                event_no = max(event_no,len(self.previous_dump[sid]))
            for j in range(event_no,len(self.D_prime[sid])):
                for k in range(0,len(self.D_prime[sid][j])):
                    iesp[self.D_prime[sid][j][k]] = True
        return iesp

    def DepthPruning(self, parent_node, node, last_event_items):
        pseudo_projection_in_ldb = self.ExtractingTheModifiedProjections(node)
        iesp = self.GettingTheIESP(pseudo_projection_in_ldb)
        for key in parent_node.seq_child_nodes:
            if(parent_node.seq_child_nodes[key].item in iesp):
                return False
        for key in parent_node.it_child_nodes:
            if(parent_node.it_child_nodes[key].item in iesp):
                return False
        return True

    def RecursiveMining(self, pattern, parent_node, node, minimum_support_threshold, Flag):
        width_pruning = self.WidthPruning(node)
        if(width_pruning == True):
            return

        depth_pruning = True
        if(Flag == False):
            depth_pruning = self.DepthPruning(parent_node, node, pattern[len(pattern)-1])
            if(depth_pruning == True):
                return
        new_Flag = False
        items = self.ScanningTheDBToGetFrequency(node.pseudo_projection, pattern[len(pattern)-1])
        fis = self.ReturnFrequentItemset(items, minimum_support_threshold)
        for item in fis:
            symbol = item.split('_')
            if(len(symbol) == 1):
                # sequence extension
                if(node.seq_child_nodes.get(int(symbol[0])) == None):
                    node.seq_child_nodes[int(symbol[0])] = PrefixTree()
                    node.seq_child_nodes[int(symbol[0])].item = int(symbol[0])
                    new_Flag = True
                node.seq_child_nodes[int(symbol[0])].pseudo_projection = self.ScanningTheDBToGetProjection(node.pseudo_projection, int(symbol[0]), pattern[len(pattern)-1], 0)
                node.seq_child_nodes[int(symbol[0])].frequency = len(node.seq_child_nodes[int(symbol[0])].pseudo_projection)
            elif(len(symbol) == 2):
                # itemset extension
                if(node.it_child_nodes.get(int(symbol[1])) == None):
                    node.it_child_nodes[int(symbol[1])] = PrefixTree()
                    node.it_child_nodes[int(symbol[1])].item = int(symbol[1])
                    new_Flag = True
                node.it_child_nodes[int(symbol[1])].pseudo_projection = self.ScanningTheDBToGetProjection(node.pseudo_projection, int(symbol[1]), pattern[len(pattern)-1], 1)
                node.it_child_nodes[int(symbol[1])].frequency = len(node.it_child_nodes[int(symbol[1])].pseudo_projection)

        for item in fis:
            symbol = item.split('_')
            if(len(symbol) == 1):
                pattern.append([int(symbol[0])])
                self.RecursiveMining(pattern, node, node.seq_child_nodes[int(symbol[0])], minimum_support_threshold, new_Flag)
                del pattern[len(pattern)-1]
            elif(len(symbol) == 2):
                pattern[len(pattern)-1].append(int(symbol[1]))
                self.RecursiveMining(pattern, node, node.it_child_nodes[int(symbol[1])], minimum_support_threshold, new_Flag)
                v = len(pattern[len(pattern)-1])
                del pattern[len(pattern)-1][v-1]

    def Mining(self):
        minimum_support_threshold = int(ceil(self.percentage_threshold * len(self.D_prime)/100.0))
        items = self.ScanningTheDBToGetFrequency(self.root.pseudo_projection, [])
        fis = self.ReturnFrequentItemset(items, minimum_support_threshold)
        if (len(fis)==0):
            return
        Flag=False
        for item in fis:
            if(self.root.seq_child_nodes.get(int(item)) == None):
                self.root.seq_child_nodes[int(item)] = PrefixTree()
                self.root.seq_child_nodes[int(item)].item = int(item)
                Flag = True
            self.root.seq_child_nodes[int(item)].pseudo_projection = self.ScanningTheDBToGetProjection(self.root.pseudo_projection, int(item), [], 0)
            self.root.seq_child_nodes[int(item)].frequency = len(self.root.seq_child_nodes[int(item)].pseudo_projection)
        for item in fis:
            self.RecursiveMining([[int(item)]], self.root, self.root.seq_child_nodes[int(item)], minimum_support_threshold, Flag)
        self.PruneRedundantPatterns(self.root, minimum_support_threshold)
        self.WritePatterns([],self.root, minimum_support_threshold)

    def PruneRedundantPatterns(self, node, minimum_support_threshold):
        redundant_item = []
        for item in node.seq_child_nodes:
            if(node.seq_child_nodes[item].frequency < minimum_support_threshold):
                self.PruneRedundantPatterns(node.seq_child_nodes[item], minimum_support_threshold)
                redundant_item.append(item)

        for key in redundant_item:
            del node.seq_child_nodes[key]

        redundant_item.clear()

        for item in node.it_child_nodes:
            if(node.it_child_nodes[item].frequency < minimum_support_threshold):
                redundant_item.append(item)
                self.PruneRedundantPatterns(node.it_child_nodes[item], minimum_support_threshold)

        for key in redundant_item:
            del node.it_child_nodes[key]

        if(node.frequency < minimum_support_threshold):
            del node
        return
    def WritePatterns(self, pattern, node, minimum_support_threshold):
        p = pattern.copy()
        save = []
        for item in node.seq_child_nodes:
            if(node.seq_child_nodes[item].frequency < minimum_support_threshold):
                self.PruneRedundantPatterns(node.seq_child_nodes[item], minimum_support_threshold)
                save.append(item)
            else:
                p.append([item])
                print(p)
                print(node.seq_child_nodes[item].frequency)
                self.WritePatterns(p,node.seq_child_nodes[item], minimum_support_threshold)
                p.pop()

        for item in save:
            del node.seq_child_nodes[item]
        save.clear()
        for item in node.it_child_nodes:
            if(node.it_child_nodes[item].frequency < minimum_support_threshold):
                self.PruneRedundantPatterns(node.it_child_nodes[item], minimum_support_threshold)
                save.append(item)
            else:
                p[len(p)-1].append(item)
                print(p)
                print(node.it_child_nodes[item].frequency)
                self.WritePatterns(p,node.it_child_nodes[item], minimum_support_threshold)
                p[len(p)-1].pop()
        for item in save:
            del node.it_child_nodes[item]
        del save

def ReadMetadata(file_name):
    with open(file_name,'r') as file:
        lines = file.readlines()
        percentage_threshold = float(lines[0].strip())
        iteration_count = int(lines[1].strip())
    return percentage_threshold, iteration_count


directory = 'E:\Research\Incremental-Sequential-Pattern-Mining\Incremental-Sequential-Pattern-Mining-with-SP-Tree\Implementation\Dataset\Bible'
percentage_threshold, iteration_count = ReadMetadata(directory+'\metadata.txt')
pbincspan = PBIncSpan(percentage_threshold)
for i in range(1,iteration_count+1):
    input_file_name = directory+'/in'+str(i)+'.txt'
    output_file_name = './Output/pbincspan-out'+str(i)+'.txt'
    pbincspan.ReadDB(input_file_name)
    sys.stdout = open(output_file_name,'w')
    pbincspan.Mining()
