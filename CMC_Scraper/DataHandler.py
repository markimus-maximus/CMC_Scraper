import json
import uuid

class DataHandling:
    
    def __init__(self):
        
        

        self.record_uuid_dict = {}


    def UUID_dictionary(self, record_list):
        ''' 
        This method generates UUIDs for every record in the method attribute list and stores in a list, before concatenating the
        UUID with a list to generate a dictionary.
        
        syntax: UUID_dictionary(record_list)
        
        Takes 1 argument.
        record_list argument = the list of records which are to be concatenated to UUIDs
          '''
        uuid_list = []   
        #generate a pseudo-unique uuid for every record in the list by taking the length of the list
        for UUID in range(len(record_list)):
            #generates 1 uuid4 and converts to string (this is easier for dictionary saving to JSON)
            single_uuid = str(uuid.uuid4())
            #append the UUID to the list
            uuid_list.append(single_uuid)
        #making the dictionary with the record list and the uuid list just generated
        
        self.record_uuid_dict = dict(zip(self.uuid_list, record_list))
        
        return self.record_uuid_dict
            
    
    def turn_dictionary_into_json_file(self, path, file_to_turn_into_json):
        '''This method converts a file to a JSON file and saves it to a specified path.
        
        syntax: turn_dictionary_into_json_file(path, dictionary_to_turn_into_json)

        Takes 2 arguments
        path argument = path for file to be written to and name of file
        file_to_turn_into_json argument = the file to be stored as a json file'''
        with open(path, 'w') as fp:
            json.dump(file_to_turn_into_json, fp)# moving the json file to a different directory- is there a more efficient way of doing this?

    def list_zipper(self, shortest_list, list_1, list_2): 
        '''This function appends 2 lists together based on the length on the shortest list according to the index of the list.
        
        syntax: list_zipper(shortest_list, List_1, List_2)
        
        Requires 3 arguments
        shortest_list argument = the list with the shortest number of indices (prevents out of range error), 
        list 1 argument = one of the lists to append 
        list 2 argument = the second list to be appended together
        '''
        
        for i in range(len(shortest_list)):
            self.combined_lists.append([list_1[i], list_2[i]])
        
        print(self.combined_lists)

if __name__ =="__main__":
    DataHandler()