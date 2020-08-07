class PatternMatcher:
    def __init__(self):
        pass
    def ReadPatterns(self, file_name):
        dict = {}
        with open(file_name, 'r') as file:
            lines = file.readlines()
            for i in range(0,len(lines),2):
                dict[lines[i].strip()]=int(lines[i+1].strip())
        return dict
    def Matcher(self, dict1, dict2):
        for key in dict1:
            if(dict2.get(key) == None):
                print("pattern = ",key, " not found in second file.")
                return False
            elif(dict2[key] != dict1[key]):
                print("pattern = ",key, " support mismatched")
                return False
        return True

pattern_matcher = PatternMatcher()
counter = 30
for i in range(1,counter+1):
    file1 = 'E:\Research\Incremental-Sequential-Pattern-Mining\Incremental-Sequential-Pattern-Mining-with-SP-Tree\Implementation\Dataset\Dataset17\out'+str(i)+'.txt'
    file2 = 'E:\Research\Incremental-Sequential-Pattern-Mining\Incremental-Sequential-Pattern-Mining-with-SP-Tree\Implementation\INCSP\Output\incsp-out'+str(i)+'.txt'
    print("Matching "+str(i))
    dict1 = pattern_matcher.ReadPatterns(file1)
    dict2 = pattern_matcher.ReadPatterns(file2)
    print("Checking Base file Vs Sanity File")
    verdict = pattern_matcher.Matcher(dict1, dict2)
    if(verdict == True):
        print("Checking Sanity File Vs Base File")
        verdict = pattern_matcher.Matcher(dict2, dict1)
        if(verdict == True):
            print("All matched perfectly")
        else:
            break
    else:
        break
