class FileMerger:
    def __init__(self):
        self.database={}

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

    def ReadFile(self, file_name):
        with open(file_name,'r') as file:
            lines = file.readlines()
            for i in range(1,len(lines)):
                sid, processed_sequence = self.ProcessSequence(lines[i])
                if(self.database.get(sid) == None):
                    self.database[sid] = []
                for j in range(0,len(processed_sequence)):
                    self.database[sid].append(processed_sequence[j])
            file.close()

    def EventToString(self, event):
        string = str(event[0])
        for i in range(1,len(event)):
            string = string+ " "+str(event[i])
        string = string + " -1"
        return string

    def ConvertingASequenceToString(self, sid, list):
        final_string = ""
        for i in range(0,len(list)):
            string = self.EventToString(list[i])
            if(i == 0):
                final_string = string
            else:
                final_string = final_string + " "+string
        final_string = str(sid)+" "+final_string
        return final_string

    def WriteFile(self,file_name):
        with open(file_name,'w') as file:
            file.write(str(len(self.database))+'\n')
            for i in range(1,len(self.database)+1):
                final_string = self.ConvertingASequenceToString(i,self.database[i])
                file.write(final_string+'\n')
            file.close()


obj = FileMerger()
counter = 2
for i in range(1,counter+1):
    file_name = './Dataset17/in'+str(i)+'.txt'
    obj.ReadFile(file_name)

obj.WriteFile('./Dataset17/mergedUpto'+str(counter)+'.txt')
