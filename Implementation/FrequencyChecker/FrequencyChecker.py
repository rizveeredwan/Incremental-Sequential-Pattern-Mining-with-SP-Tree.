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
        sub_patt = ""
        for j in range(0,len(patt)):
            if(patt[j] == " "):
                continue
            if(patt[j] == '['):
                sub_patt = ""
            elif(patt[j] == ']'):
                sub_patt = sub_patt.split(',')
                temp = []
                for k in range(0,len(sub_patt)):
                    try:
                        value = int(sub_patt[k].strip())
                        temp.append(value)
                    except Exception as e:
                        pass
                if(len(temp)>0):
                    full_patt.append(temp)
                sub_patt = ""
            else:
                sub_patt = sub_patt + patt[j]
        return full_patt

    def ReadGeneratedPatterns(self, pattern_file_name):
        self.patterns_support=[]
        self.patterns=[]
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
        list = []
        for key in self.database:
            base_pattern = self.database[key]
            value = self.SubPatternChecking(base_pattern, pattern)
            support = support + value
            if(value == 1):
                list.append(key)
        return support,list

    def SanityChecking(self):
        matched = True
        for i in range(0,len(self.patterns)):
            found_support,list = self.SupportMeasureInDB(self.patterns[i])
            calculated_support = self.patterns_support[i]
            if(calculated_support != found_support):
                print("Support value mismatched")
                print(self.patterns[i], found_support, calculated_support)
                #print(list)
                matched = False
                return matched
            else:
                pass
                #print(self.patterns[i], found_support, calculated_support)
                #print(list)
        print("Match status = ", matched)
        return matched

    def ReadMetadataFile(self, file_name):
        with open(file_name,'r') as file:
            lines = file.readlines()
            self.iteration_count = int(lines[1].strip())

file_directory = 'E:\Research\Incremental-Sequential-Pattern-Mining\Incremental-Sequential-Pattern-Mining-with-SP-Tree\Implementation\Dataset\Bible'
#pattern_file_directory = 'E:\Research\Incremental-Sequential-Pattern-Mining\Incremental-Sequential-Pattern-Mining-with-SP-Tree\Implementation\PBIncSpan\Output\pbincspan-out'
pattern_file_directory = 'E:\Research\Incremental-Sequential-Pattern-Mining\Incremental-Sequential-Pattern-Mining-with-SP-Tree\Implementation\Dataset\Bible\special'

freq_checker = FrequencyChecker()
freq_checker.ReadMetadataFile(file_directory+'\metadata.txt')
for i in range(0,freq_checker.iteration_count):
    print("iteration_count ",i)
    input_file_name = file_directory+"\in"+str(i+1)+'.txt'
    freq_checker.ReadDB(input_file_name)
    #pattern_file =  file_directory+"\out"+str(i+1)+'.txt'
    pattern_file = pattern_file_directory+str(1)+'.txt'
    freq_checker.ReadGeneratedPatterns(pattern_file)
    verdict = freq_checker.SanityChecking()
    print(pattern_file+" checking done\n\n")
    if(verdict == False):
        continue
        break
