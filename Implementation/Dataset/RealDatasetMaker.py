# Code to Organize the real dataset
import random
from math import floor

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

def GettingTheEvents(list):
    temp = []
    sequence = []
    for i in range(0,len(list)):
        if(list[i] == -1):
            sequence.append(temp)
            temp = []
        elif(list[i] == -2):
            break
        else:
            temp.append(list[i])
    return sequence

def EventMerger(old_file_name, new_file_name):
    items = []
    sequence_database = []
    with open(old_file_name,'r') as file:
        lines = file.readlines()
        for i in range(0,len(lines)):
            line = lines[i].strip().split(' ')
            StringToIntConverter(line)
            sequence = GettingTheEvents(line)
            k=0
            while(k<len(sequence)):
                v = random.randint(0,1)
                if(v==1):
                    # merging events
                    if((k+1)<len(sequence)):
                        for j in range(0,len(sequence[k+1])):
                            sequence[k].append(sequence[k+1][j])
                        del sequence[k+1]
                    else:
                        break
                else:
                    k=k+1
            sequence_database.append(sequence)
            for j in range(0,len(sequence)):
                for k in range(0,len(sequence[j])):
                    items.append(sequence[j][k])
        file.close()
    with open(new_file_name,'w') as file:
        items = sorted(items)
        unique_events = [items[0]]
        index={}
        index[items[0]]=0
        for i in range(1,len(items)):
            if(items[i] != unique_events[len(unique_events)-1]):
                unique_events.append(items[i])
                index[items[i]]=len(unique_events)-1
        for i in range(len(sequence_database)):
            sequence = sequence_database[i]
            for j in range(0,len(sequence)):
                for k in range(0,len(sequence[j])):
                    sequence[j][k] = index[sequence[j][k]]
                sequence[j] = sorted(sequence[j])
            sequence = SequenceToStringConversion(sequence)
            file.write(sequence+'\n')
        file.close()

def WriteIntoIncrementalFile(file_name,database):
    with open(file_name,'w') as file:
        file.write(str(len(database))+'\n')
        for key in database:
            string = str(key)
            for i in range(0,len(database[key])):
                for j in range(0,len(database[key][i])):
                    string = string + " " + str(database[key][i][j])
                string = string + ' -1'
            file.write(string+'\n')
        file.close()
        return

def IncrementalDatabaseMaker(directory_name,file_name, initial_threshold,incremental_threshold):
    sequence_database=[]
    taken_upto = []
    sid = []
    with open(file_name,'r') as file:
        lines = file.readlines()
        for i in range(0,len(lines)):
            line = lines[i].strip().split(' ')
            StringToIntConverter(line)
            sequence = GettingTheEvents(line)
            sequence_database.append(sequence)
            taken_upto.append(-1)
            sid.append(i)
        n = floor(initial_threshold * len(sequence_database))
        i = 0
        visit={}
        initial_database={}
        all_complete_count = 0
        while (i<n):
            index2 = random.randint(0,len(sid)-1)
            index = sid[index2]
            if(visit.get(index) == None):
                visit[index]=True
                position = random.randint(0,len(sequence_database[index])-1)
                taken_upto[index] = position
                if(position == len(sequence_database[index])-1):
                    all_complete_count = all_complete_count + 1
                    del sid[index2]
                initial_database[index+1]=[]
                for j in range(0,position+1):
                    initial_database[index+1].append(sequence_database[index][j])
                i = i + 1
        file_ptr = 1
        print(len(initial_database),len(sequence_database))
        WriteIntoIncrementalFile(directory_name+'/in'+str(file_ptr)+'.txt',initial_database)
        print("file = ",file_ptr)
        file_ptr = file_ptr + 1
        database = {}
        while len(visit)<len(sequence_database):
            index = random.randint(0,len(sequence_database)-1)
            if(visit.get(index) == None):
                visit[index] = True
                database[index+1] = []
                for j in range(0,len(sequence_database[index])):
                    database[index+1].append(sequence_database[index][j])
                taken_upto[index] = len(sequence_database[index])-1
            elif(taken_upto[index]<len(sequence_database[index])-1):
                database[index+1]=[]
                for j in range(taken_upto[index]+1,len(sequence_database[index])):
                    database[index+1].append(sequence_database[index][j])
                taken_upto[index] = len(sequence_database[index])-1
        WriteIntoIncrementalFile(directory_name+'/in'+str(file_ptr)+'.txt',database)
        f=open(directory_name+'/metadata.txt','w')
        f.write('1\n')
        f.write(str(file_ptr)+'\n')
        f.close()

def AvgNumberOfItemsetsRemoved(base_file,input_file):
    item_count = {}
    item_count_new = {}
    with open(base_file,'r') as file:
        lines = file.readlines()
        for i in range(0,len(lines)):
            line = lines[i].strip().split(' ')
            StringToIntConverter(line)
            sequence = GettingTheEvents(line)
            item_count[i+1]=len(sequence)
    with open(input_file,'r') as file:
        lines = file.readlines()
        for i in range(0,len(lines)):
            line = lines[i].strip().split(' ')
            index = int(line[0])
            line = line[1:len(line)]
            StringToIntConverter(line)
            sequence = GettingTheEvents(line)
            item_count_new[index-1] = len(sequence)

    sum = 0
    for key in item_count:
        value = item_count[key]
        if(item_count_new.get(key) != None):
            sum = sum + item_count[key] - item_count_new[key]
    sum = (sum*1.0)/(len(item_count))
    print("Average Itemset Removed = ",sum)

def SyntheticBasicDatasetMaker(input_file_name,output_file_name):
    items = []
    itemset_database = []
    with open(input_file_name,'r') as file:
        lines = file.readlines()
        for i in range(0,len(lines)):
            line = lines[i].strip().split(' ')
            StringToIntConverter(line)
            line = sorted(line)
            itemset_database.append(line)
            for j in range(0,len(line)):
                items.append(line[j])
        file.close()

    items = sorted(items)
    order = {}
    count = 0
    order[items[0]]=0
    for i in range(1,len(items)):
        if(items[i]>items[i-1]):
            count = count + 1
            order[items[i]] = count
    with open(output_file_name,'w') as file:
        for i in range(0,len(itemset_database)):
            string = str(itemset_database[i][0])
            v = random.randint(0,1)
            last_event = []
            last_event.append(itemset_database[i][0])
            f = False
            for j in range(0,len(itemset_database[i])):
                v = random.randint(0,1)
                if(v == 0):
                    if(itemset_database[i][j] not in last_event):
                        string = string + " "+str(itemset_database[i][j])
                        last_event.append(itemset_database[i][j])
                    else:
                        string = string + " " + '-1'
                        string = string + " "+ str(itemset_database[i][j])
                        last_event = [itemset_database[i][j]]
                elif(v == 1):
                    string = string + " "+"-1"
                    string = string + " "+ str(itemset_database[i][j])
                    last_event = [itemset_database[i][j]]
            string = string + " -1"
            file.write(string+'\n')
        file.close()

def AverageSequenceLength(file_name):
    sum = 0
    with open(file_name,'r') as file:
        lines = file.readlines()
        for i in range(0,len(lines)):
            line = lines[i].strip().split(' ')
            StringToIntConverter(line)
            sequence = GettingTheEvents(line)
            for j in range(0,len(sequence)):
                sum = sum + len(sequence[j])
        sum = (sum)/(len(lines)*1.0)
        print("Avg Seq. Length = ",sum)

def UniqueItemCount(file_name):
    flag = {}
    with open(file_name,'r') as file:
        lines = file.readlines()
        for i in range(0,len(lines)):
            line = lines[i].strip().split(' ')
            StringToIntConverter(line)
            sequence = GettingTheEvents(line)
            for j in range(0,len(sequence)):
                for k in range(0,len(sequence[j])):
                    flag[sequence[j][k]] = True
        print("Unique Item Count = ",len(flag))

def AverageItemsetLength(file_name):
    count_item = 0
    count_event = 0
    with open(file_name,'r') as file:
        lines = file.readlines()
        for i in range(0,len(lines)):
            line = lines[i].strip().split(' ')
            StringToIntConverter(line)
            sequence = GettingTheEvents(line)
            count_event = count_event + len(sequence)
            for j in range(0,len(sequence)):
                count_item = count_item + len(sequence[j])
        print(count_item/(count_event*1.0))

#EventMerger('c20d10k/c20d10k.txt','c20d10k/c20d10k_Processed.txt')
#SyntheticBasicDatasetMaker('c20d10k/c20d10k.txt','c20d10k/c20d10k_Processed.txt')

"""
directory_name = 'c20d10k'
file_name = 'c20d10k_Processed.txt'
initial_threshold_list = [90]
initial_threshold = initial_threshold_list[random.randint(0,len(initial_threshold_list)-1)]
incremental_threshold=[0.1]
IncrementalDatabaseMaker(directory_name,directory_name+'/'+file_name, initial_threshold/100.0,incremental_threshold)
"""

AvgNumberOfItemsetsRemoved('c20d10k/c20d10k_Processed.txt','c20d10k/in1.txt')
#AverageSequenceLength('Kosarak25k/Kosarak25k_Processed.txt')
#UniqueItemCount('t25i10d10k/t25i10d10k_Processed.txt')
#AverageItemsetLength('Bible/Bible_Processed.txt')
