from math import ceil
import sys

class INCSP:
    def __init__(self,minimum_percentage):
        self.percentage_threshold = minimum_percentage
        self.database = {}
        self.new_database = {}
        self.total_database_size = 0
        self.frequent_patterns={}
        self.one_length_candidates={}

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

    def ReadDB(self, file_name):
        with open(file_name,'r') as file:
            lines = file.readlines()
            count = int(lines[0].strip())
            for i in range(1,count+1):
                sid, processed_sequence = self.ProcessSequence(lines[i])
                self.new_database[sid] = processed_sequence
        for key in self.new_database:
            if(self.database.get(key) == None):
                self.total_database_size = self.total_database_size + 1
        self.IncSPMining()

    def MergeWithOldDB(self):
        for key in self.new_database:
            if(self.database.get(key) != None):
                for i in range(0,len(self.new_database[key])):
                    self.database[key].append(self.new_database[key][i])
            else:
                self.database[key]=self.new_database[key]
        self.new_database.clear()

    def GenerateLengthOneCandidates(self):
        for key in self.new_database:
            for i in range(0,len(self.new_database[key])):
                for j in range(0,len(self.new_database[key][i])):
                    self.one_length_candidates[self.new_database[key][i][j]] = True

    def SubPatternChecking(self, base_pattern, actual_pattern):
        prev_ending = -1
        found = False
        for i in range(0, len(actual_pattern)):
            prev_ending = prev_ending + 1
            found = False
            while(prev_ending<len(base_pattern)):
                if(len(base_pattern[prev_ending]) < len(actual_pattern[i])):
                    prev_ending = prev_ending + 1
                    continue
                ptr = 0
                for j in range(0, len(base_pattern[prev_ending])):
                    if(base_pattern[prev_ending][j] == actual_pattern[i][ptr]):
                        ptr=ptr+1
                    elif(base_pattern[prev_ending][j] > actual_pattern[i][ptr]):
                        found = False
                        break
                    if(ptr == len(actual_pattern[i])):
                        break
                if(ptr == len(actual_pattern[i])):
                    found = True
                    break
                prev_ending = prev_ending + 1
            if(found == False):
                return 0
        return 1

    def SupportCountOne(self,xk):
        for key in self.new_database:
            if(self.database.get(key) == None):
                # new sequence
                for i in range(0,len(xk)):
                    sup = self.SubPatternChecking(self.new_database[key], xk[i][0])
                    xk[i][1] = xk[i][1]+sup
            else:
                # merged with old sequence
                for i in range(0,len(xk)):
                    sup = self.SubPatternChecking(self.new_database[key], xk[i][0])
                    if(sup == 1):
                        if(self.SubPatternChecking(self.database[key], xk[i][0]) == 0):
                            xk[i][1] = xk[i][1]+sup
        return xk

    def SupportCountTwo(self, xk_prime):
        for key in self.database:
            for i in range(0,len(xk_prime)):
                sup = self.SubPatternChecking(self.database[key], xk_prime[i][0])
                xk_prime[i][1] = xk_prime[i][1] + sup
        return xk_prime

    def NewSequenceCount(self):
        count = 0
        for key in self.new_database:
            if(self.database.get(key) == None):
                count = count + 1
        return count

    def ListCopy(self, list):
        patt = []
        for i in range(0,len(list)):
            temp = []
            for j in range(0,len(list[i])):
                temp.append(list[i][j])
            patt.append(temp)
        return patt

    def TwoPatternMatching(self, pattern1, pattern2):
        sub_patt1 = []
        sub_patt2 = []
        for i in range(0,len(pattern1)):
            temp = []
            st = 0
            if(i==0):
                st = 1
            for j in range(st,len(pattern1[i])):
                temp.append(pattern1[i][j])
            if(len(temp)>0):
                sub_patt1.append(temp)

        for i in range(0,len(pattern2)):
            temp = []
            en = len(pattern2[i])
            if(i==len(pattern2)-1):
                en = en - 1
            for j in range(0,en):
                temp.append(pattern2[i][j])
            if(len(temp) > 0):
                sub_patt2.append(temp)

        if(sub_patt1 != sub_patt2):
            return False
        if(len(pattern2[len(pattern2)-1]) == 1):
            # sequence extension
            join_result = self.ListCopy(pattern1)
            join_result.append(pattern2[len(pattern2)-1].copy())
        else:
            join_result =  self.ListCopy(pattern1)
            join_result[len(join_result)-1].append(pattern2[len(pattern2)-1][len(pattern2[len(pattern2)-1])-1])
        return join_result

    def Join(self, list_of_patterns):
        candidate = []
        hash_table = {}
        for i in range(0,len(list_of_patterns)):
            hash_table[str(list_of_patterns[i])] =  True
            for j in range(0, len(list_of_patterns)):
                #print("previous list = ",list_of_patterns, list_of_patterns[i],list_of_patterns[j])
                join_result = self.TwoPatternMatching(list_of_patterns[i],list_of_patterns[j])
                #print("now = ",list_of_patterns)
                if(join_result == False):
                    continue
                candidate.append(join_result)
        return candidate, hash_table

    def GenerateSubPatternsAndCheck(self, base_pattern, hash_table):
        for i in range(0,len(base_pattern)):
            for j in range(0,len(base_pattern[i])):
                sub_patt = []
                for k in range(0,len(base_pattern)):
                    temp = []
                    for l in range(0,len(base_pattern[k])):
                        if(k == i and j == l):
                            continue
                        else:
                            temp.append(base_pattern[k][l])
                    if(len(temp) > 0):
                        sub_patt.append(temp)
                if(hash_table.get(str(sub_patt)) == None):
                    return False
        return True

    def Prune(self, candidate, hash_table):
        actual_candidates = []
        for i in range(0,len(candidate)):
            base_pattern = candidate[i]
            verdict = self.GenerateSubPatternsAndCheck(base_pattern, hash_table)
            if(verdict == True):
                actual_candidates.append(base_pattern)
        return actual_candidates

    def TwoLengthCandidateGeneration(self, list_of_patterns):
        candidates = []
        for i in range(0,len(list_of_patterns)):
            for j in range(0,len(list_of_patterns)):
                candidates.append([list_of_patterns[i][0],list_of_patterns[j][0]])
                if(list_of_patterns[i][0][0]<list_of_patterns[j][0][0]):
                    candidates.append([[list_of_patterns[i][0][0],list_of_patterns[j][0][0]]])
        return candidates

    def IncSPMining(self):
        xk=[]
        self.GenerateLengthOneCandidates()
        for key in self.one_length_candidates:
            xk.append([[[key]],0])
        k=1
        while True:
            xk = self.SupportCountOne(xk)
            xk_prime = []
            for i in range(0,len(xk)):
                if(self.frequent_patterns.get(k) != None and self.frequent_patterns[k].get(str(xk[i][0])) != None):
                    continue
                if(xk[i][1]<(self.percentage_threshold*(self.total_database_size-len(self.database)))):
                    xk_prime.append([xk[i][0],0])
            xk_prime = self.SupportCountTwo(xk_prime)
            sk = {}
            ptr = -1
            list_of_patterns = []
            for i in range(0,len(xk)):
                if(self.frequent_patterns.get(k) != None and self.frequent_patterns[k].get(str(xk[i][0])) != None):
                    prev_freq = self.frequent_patterns[k][str(xk[i][0])]
                    new_freq = xk[i][1]
                    if((prev_freq+new_freq) >= (self.percentage_threshold * self.total_database_size)/100.0):
                        sk[str(xk[i][0])]=prev_freq+new_freq
                        list_of_patterns.append(xk[i][0])
                else:
                    ptr = ptr + 1
                    prev_freq = xk_prime[ptr][1]
                    new_freq = xk[i][1]
                    if((prev_freq+new_freq) >= (self.percentage_threshold * self.total_database_size)/100.0):
                        sk[str(xk[i][0])]=prev_freq+new_freq
                        list_of_patterns.append(xk[i][0])
            self.frequent_patterns[k] = sk
            k = k + 1
            # generating candidates
            if(k == 2):
                candidates = self.TwoLengthCandidateGeneration(list_of_patterns)
            else:
                candidates, hash_table = self.Join(list_of_patterns)
                candidates = self.Prune(candidates, hash_table)
            xk.clear()
            if(len(candidates) > 0):
                for i in range(0,len(candidates)):
                    xk.append([candidates[i],0])
            else:
                while(True):
                    if(self.frequent_patterns.get(k) != None):
                        self.frequent_patterns[k].clear()
                        k = k + 1
                    else:
                        break
                break
        self.MergeWithOldDB()
        
    def WriteFrequentPatterns(self):
        k = 1
        while True:
            if(self.frequent_patterns.get(k) != None):
                for key in self.frequent_patterns[k]:
                    print(key)
                    print(self.frequent_patterns[k][key])
                k = k + 1
            else:
                break

def ReadMetadata(file_name):
    with open(file_name,'r') as file:
        lines = file.readlines()
        percentage_threshold = float(lines[0].strip())
        iteration_count = int(lines[1].strip())
        file.close()
        return percentage_threshold, iteration_count

directory = 'E:\Research\Incremental-Sequential-Pattern-Mining\Incremental-Sequential-Pattern-Mining-with-SP-Tree\Implementation\Dataset\Dataset2'

percentage_threshold, iteration_count = ReadMetadata(directory+'\metadata.txt')

inc_sp = INCSP(percentage_threshold)
for i in range(1,iteration_count+1):
    input_file_name = directory+'\in'+str(i)+'.txt'
    inc_sp.ReadDB(input_file_name)
    #print("Mining done")
    sys.stdout = open('.\Output\incsp-out-'+str(i)+'.txt','w')
    inc_sp.WriteFrequentPatterns()
