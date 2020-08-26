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
        WriteIntoIncrementalFile(directory_name+'/in'+str(file_ptr)+'.txt',initial_database)
        print("file = ",file_ptr)
        while (all_complete_count<len(sequence_database)):
            file_ptr = file_ptr + 1
            inc_thres = incremental_threshold[random.randint(0,len(incremental_threshold)-1)]
            n = floor(inc_thres * len(sequence_database))
            base_n = n
            visit={}
            database = {}
            fail_count = 0
            while n>0:
                #print(base_n,"n = ",n,len(sequence_database),all_complete_count,len(sid))
                if(all_complete_count >= len(sequence_database)):
                    break
                index2 = random.randint(0,len(sid)-1)
                index = sid[index2]
                #print(index,visit.get(index),len(visit))
                if(visit.get(index) == None):
                    fail_count = 0
                    visit[index] = True
                    position = random.randint(taken_upto[index]+1,len(sequence_database[index])-1)
                    if(position == len(sequence_database[index])-1):
                        all_complete_count = all_complete_count + 1
                        del sid[index2]
                    database[index+1]=[]
                    for j in range(taken_upto[index]+1,position+1):
                        database[index+1].append(sequence_database[index][j])
                    taken_upto[index] = position
                    n = n-1
                else:
                    fail_count = fail_count +1
                    if(fail_count >= 500):
                        break

            WriteIntoIncrementalFile(directory_name+'/in'+str(file_ptr)+'.txt',database)
            print("file = ",file_ptr)
        f=open(directory_name+'/metadata.txt','w')
        f.write('1\n')
        f.write(str(file_ptr)+'\n')
        f.close()

EventMerger('Kosarak25k/Kosarak25k.txt','Kosarak25k/Kosarak25k_Processed.txt')


directory_name = 'Kosarak25k'
file_name = 'Kosarak25k_Processed.txt'
initial_threshold_list = [30,31,32,33,34,35,36,37,38,39,40]
initial_threshold = initial_threshold_list[random.randint(0,len(initial_threshold_list)-1)]
incremental_threshold=[0.05,0.1,0.15,0.2]
IncrementalDatabaseMaker(directory_name,directory_name+'/'+file_name, initial_threshold/100.0,incremental_threshold)
