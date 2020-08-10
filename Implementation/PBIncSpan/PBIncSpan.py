from PBIncSpanTree import PrefixTree

class PBIncSpan:
    def __init__(self, percentage_threshold):
        self.D_prime = {}
        self.LDB = {}
        self.previous_dump = {}
        self.percentage_threshold = self.percentage_threshold
        self.root = PrefixTree()

    def ReadDB(self, file_name):
        self.LDB.clear()
        self.root.pseudo_projection_in_ldb.clear()
        self.previous_dump.clear()
        with open(file_name, 'r') as file:
            lines = file.readlines()
            for i in range(0,len(lines)):
                sid, processed_sequence = self.ProcessSequence(lines[i])
                if(self.D_prime.get(sid) == None):
                    self.D_prime[sid] = processed_sequence
                    self.LDB[sid] = processed_sequence
                    self.root.psuedo_projection.append([sid,""])
                    self.root.pseudo_projection_in_ldb.append([sid,""])
                else:
                    self.previous_dump[sid] = []
                    for j in range(0,len(self.D_prime[sid])):
                        self.previous_dump[sid].append(self.D_prime[sid][j])
                    for j in range(0,len(processed_sequence)):
                        self.D_prime[sid].append(processed_sequence[j])
                    self.LDB[sid] = self.D_prime[sid]
                    self.root.pseudo_projection_in_ldb.append([sid,""])
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
        ptr1, ptr2 = 0,0
        while(True):
            if(ptr1 >= len(event1)):
                return True #event1 in event2
            if(ptr2>=len(event2)):
                return False
            if(event2[ptr2] > event1[ptr1]):
                return False
            if(event1[ptr1] == event2[ptr2]):
                ptr1=ptr1+1
                continue
            ptr2=ptr2+1


    def ScanningTheDBToGetFrequency(self, pseudo_projection, last_event_items):
        item_count = {}
        for i in range(0,len(pseudo_projection)):
            if(pseudo_projection[i][1] == ""):
                event_no = 0
            else:
                event_no = psuedo_projection[i][1]
            temp_dict = {}
            for j in range(event_no,len(self.D_prime[pseudo_projection[i][0]])):
                # same event count
                verdict = self.TwoEventMatching(last_event_items, self.D_prime[pseudo_projection[i][0]][j])
                if(verdict == True):
                    for k in range(0,len(self.D_prime[pseudo_projection[i][0]][j])):
                        if(self.D_prime[pseudo_projection[i][0]][j][k] > last_event_items[len(last_event_items)-1]):
                            temp_dict['_'+str(self.D_prime[pseudo_projection[i][0]][j][k])] = True
                if(j>event_no):
                    for k in range(0,len(self.D_prime[pseudo_projection[i][0]][j])):
                        temp_dict[str(self.D_prime[pseudo_projection[i][0]][j][k])] = True
            for key in temp_dict:
                item_count[key] = item_count[key] + 1
        return item_count

    def ScanningTheDBToGetProjection(self,psuedo_projection,item, last_event_items, type):
        next_psuedo_projection=[]
        for i in range(0,len(psuedo_projection)):
            if(pseudo_projection[i][1] == ""):
                event_no = 0
            else:
                event_no = psuedo_projection[i][1]
            if(type == 0):
                for j in range(event_no+1, len(self.D_prime[psuedo_projection[i][0]])):
                    if(item in self.D_prime[psuedo_projection[i][0]][j]):
                        next_psuedo_projection.append([psuedo_projection[i][0],j])
                        break
            else:
                for j in range(event_no, len(self.D_prime[psuedo_projection[i][0]])):
                    if(item in self.D_prime[psuedo_projection[i][0]][j] and self.TwoEventMatching(last_event_items, self.D_prime[psuedo_projection[i][0]][j]) == True):
                        next_psuedo_projection.append([psuedo_projection[i][0],j])
                        break
        return next_psuedo_projection

    def WidthPruning(self, iasids, pseqid):
        temp_dict={}
        for i in range(0,len(iasids)):
            temp_dict[iasids[i]]=True
        for i in range(len(pseqid)):
            if(temp_dict.get(pseqid[i][0]) == None):
                continue
            return False
        return True

    def ReturnFrequentItemset(self, temp, minimum_support_threshold):
        ies = {}
        for key in temp:
            if(temp[key] >= minimum_support_threshold):
                ies[key] = temp[key]
        return ies

    def GettingTheIESP(self, node, temp):
        iesp = {}
        for i in range(0,len(node.pseudo_projection_in_ldb)):
            event_no = node.pseudo_projection_in_ldb[i][1]
            sid = node.pseudo_projection_in_ldb[i][0]

    def DepthPruning(self, node, last_event_items,  minimum_support_threshold):
        temp = self.ScanningTheDBToGetFrequency(self, node.pseudo_projection_in_ldb, last_event_items)



        # need to work from here

    def Mining(self):
        minimum_support_threshold = int(ceil(self.percentage_threshold * len(self.D_prime))/100.0)


def ReadMetadata(file_name):
    with open(file_name,'r') as file:
        lines = file.readlines()
        percentage_threshold = float(lines[0].strip())
        iteration_count = int(lines[1].strip())
    return percentage_threshold, iteration_count


directory = ''
percentage_threshold, iteration_count = ReadMetadata(directory+'/metadata.txt')
pbincspan = PBIncSpan(percentage_threshold)
for i in range(1,iteration_count+1):
    input_file_name = directory+'/in'+str(i)+'.txt'
    pbincspan.ReadDB(input_file_name)
    pbincspan.Mining()
