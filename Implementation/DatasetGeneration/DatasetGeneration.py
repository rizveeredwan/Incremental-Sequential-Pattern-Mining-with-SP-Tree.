import random

total_item_count = 30
iteration_count = 2
max_sequence_length = 40
max_number_of_sequence_in_batch=500
directory_name = 'E:\Research\Incremental-Sequential-Pattern-Mining\Incremental-Sequential-Pattern-Mining-with-SP-Tree\Implementation\Dataset\Dataset18'

class DatasetGeneration:
    def __init__(self):
        pass
    def SequenceGeneration(self, length):
        global total_item_count
        event = []
        seq = []
        already_added_length = 0
        i = -1
        while (i < length-1):
            i = i + 1
            event_decision = random.randint(0,1)
            if(event_decision == 0):
                # adding into previous event
                if(len(seq)==0):
                    item = random.randint(0,total_item_count-1)
                    seq.append([item])
                else:
                    last_item = seq[len(seq)-1][len(seq[len(seq)-1])-1] # last item of the last event
                    if(last_item == total_item_count-1):
                        i = i - 1
                        continue
                    else:
                        new_item = random.randint(last_item+1, total_item_count-1)
                        seq[len(seq)-1].append(new_item)
            elif(event_decision == 1):
                # adding into new event
                item = random.randint(0,total_item_count-1)
                seq.append([item])
        return seq

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

    def WriteMergedFile(self, file_directory):
        with open(file_directory+'/merged.txt', 'w') as file:
            file.write(str(len(self.complete_database))+'\n')
            for key in self.complete_database:
                string = self.ConvertingASequenceToString(key, self.complete_database[key])
                file.write(string + '\n')
            file.close()

    def Generation(self, directory_name):
        global iteration_count, max_number_of_sequence_in_batch, max_sequence_length
        f =  open(directory_name+'\metadata.txt','w')
        f.write("1\n")
        f.write(str(iteration_count)+'\n')
        f.close()

        total_number_of_sequence = 0
        self.complete_database = {}
        self.saving_length = {}

        local_dictionary = {}

        for i in range(0,iteration_count):
            total_length = random.randint(1,max_number_of_sequence_in_batch)
            f = open(directory_name+'\in'+str(i+1)+'.txt','w')
            f.write(str(total_length)+'\n')
            j = -1
            local_dictionary.clear()
            while j < total_length-1:
                j = j + 1
                verdict = random.randint(0,1)
                if(verdict == 0):
                    # appending to a new sequence
                    if(total_number_of_sequence == 0):
                        j = j -1
                        continue
                    key = random.randint(1, total_number_of_sequence)
                    if(local_dictionary.get(key) != None):
                        j = j - 1
                        continue
                    if(self.saving_length[key] == max_sequence_length):
                        # no more addition is possible
                        j = j - 1
                        continue
                    else:
                        rem_length = max_sequence_length - self.saving_length[key]
                        length = random.randint(1,rem_length)
                        self.saving_length[key] = self.saving_length[key] + length
                        seq = self.SequenceGeneration(length)
                        for k in range(0,len(seq)):
                            self.complete_database[key].append(seq[k])
                        final_string = self. ConvertingASequenceToString(key, seq)
                        local_dictionary[key] = True
                        f.write(final_string+'\n')
                elif(verdict == 1):
                    # new sequence
                    total_number_of_sequence = total_number_of_sequence + 1
                    length = random.randint(1,max_sequence_length-1)
                    seq = self.SequenceGeneration(length)
                    self.complete_database[total_number_of_sequence] = seq
                    self.saving_length[total_number_of_sequence] = length
                    final_string = self.ConvertingASequenceToString(total_number_of_sequence, seq)
                    local_dictionary[total_number_of_sequence] = True
                    f.write(final_string+'\n')
            f.close()


dataset_gen = DatasetGeneration()
dataset_gen.Generation(directory_name)
dataset_gen.WriteMergedFile(directory_name)
