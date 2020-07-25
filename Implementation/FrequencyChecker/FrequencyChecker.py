class FrequencyChecker:
    def __init__(self):
        self.database={}
        self.patterns=[]
        self.patterns_support=[]

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

        with open(file_name, 'r') as file:
            lines = file.readlines()
            for i in range(1, len(lines)):
                sid, processed_sequence = self.ProcessSequence(lines[i])
                if(self.database.get(sid) == None):
                    self.database[sid] = processed_sequence
                else:
                    for j in range(0, len(processed_sequence)):
                        self.database[sid].append(processed_sequence[j])

    def ConversionStringToList(self, patt):
        patt = patt.strip()
        patt = patt[1:len(patt)-1]
        full_patt = []
        sub_patt = []
        for j in range(0,len(patt)):
            if(patt[j] == " " or patt[j] == ','):
                continue
            if(patt[j] == '['):
                sub_patt = []
            elif(patt[j] == ']'):
                full_patt.append(sub_patt)
            else:
                value = int(patt[j].strip())
                sub_patt.append(value)
        return full_patt

    def ReadGeneratedPatterns(self, pattern_file_name):
        with open(pattern_file_name, 'r') as file:
            lines = file.readlines()
            for i in range(0,len(lines),2):
                supp = int(lines[i+1].strip())
                self.patterns_support.append(supp)
                full_patt = self.ConversionStringToList(lines[i])
                self.patterns.append(full_patt)

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

    def SupportMeasureInDB(self, pattern):
        support = 0
        for key in self.database:
            base_pattern = self.database[key]
            value = self.SubPatternChecking(base_pattern, pattern)
            support = support + value
        return support

    def SanityChecking(self):
        matched = True
        for i in range(0,len(self.patterns)):
            found_support = self.SupportMeasureInDB(self.patterns[i])
            calculated_support = self.patterns_support[i]
            if(calculated_support != found_support):
                print("Support value mismatched")
                print(self.patterns[i], found_support, calculated_support)
                matched = False
        print("Match status = ", matched)


database_file = 'E:\Research\Incremental-Sequential-Pattern-Mining\Incremental-Sequential-Pattern-Mining-with-SP-Tree\Implementation\INCSPTree_BPFSPTree\Dataset\Dataset8\in1.txt'
pattern_file = 'E:\Research\Incremental-Sequential-Pattern-Mining\Incremental-Sequential-Pattern-Mining-with-SP-Tree\Implementation\INCSPTree_BPFSPTree\Dataset\Dataset8\out1.txt'

freq_checker = FrequencyChecker()
freq_checker.ReadDB(database_file)
freq_checker.ReadGeneratedPatterns(pattern_file)
freq_checker.SanityChecking()