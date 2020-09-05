def StringToIntConverter(list):
    for i in range(0,len(list)):
        list[i]=int(list[i])
    return

def SequenceToStringConversion(seq):
    string = ""
    for i in range(0,len(seq)):
        for j in range(0,len(seq[i])):
            if(string == ""):
                string = str(seq[i][j])
            else:
                string = string + " " + str(seq[i][j])
        string = string + " -1"
    return string

def SPMFConverter(input_file,output_file_name):
    f=open(output_file_name,'w')
    unique_items=[]
    with open(input_file,'r') as file:
        lines = file.readlines()
        for i in range(len(lines)):
            line = lines[i].strip().split(' ')
            StringToIntConverter(line)
            j = 1
            seq = []
            while(j<len(line)):
                T = line[j]
                seq.append([])
                for k in range(j+1,j+1+T):
                    seq[len(seq)-1].append(line[k])
                    unique_items.append(line[k])
                j = j+1+T
            string = SequenceToStringConversion(seq)
            f.write(string+'\n')
            if(len(seq) != line[0]):
                print("bug")
    f.close()

SPMFConverter('D2.data','Test-Synthetic_Processed2.txt')
