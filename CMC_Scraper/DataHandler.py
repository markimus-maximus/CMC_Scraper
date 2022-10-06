import json
import uuid
import logging
import uuid
import json
import boto3
import psycopg2
import itertools
import ntpath
from datetime import date 
import pandas as pd
import os
from sqlalchemy import create_engine
from sqlalchemy import inspect

class DataHandler:
    
    def __init__(self):
        pass

    @staticmethod
    def create_UUID_list(UUID_list_length:int):
        ''' 
        This method generates UUIDs for every record in the argument record_list and stores in a list, 
        
        syntax: UUID_dictionary(record_list)
        
        Takes 1 argument.
        UUID_list_length argument = the required length of the UUID list
          '''
        uuid_list = []   
        #generate a pseudo-unique uuid for every record in the list by taking the length of the list
        for UUID in range(UUID_list_length):
            #generates 1 uuid4 and converts to string (this is easier for dictionary saving to JSON)
            single_uuid = str(uuid.uuid4())
            #append the UUID to the list
            uuid_list.append(single_uuid)
        #making the dictionary with the record list and the uuid list just generated

    @staticmethod
    def create_dict_from_2_lists(list_1, list_2):
        '''This method creates a dictionary from 2 lists.
        
        syntax: create_dict_from_2_lists(list_1, list_2)
        
        Takes 2 arguments.
        list_1 and list_2 are the 2 lists to be converted into a dictionary'''
        
        record_uuid_dict = dict(zip(list_1, list_2))
        
        return record_uuid_dict
            
    
    def turn_data_into_json_file(self, path, data_to_convert_to_json):
        '''This method converts data to a JSON file and saves it to a specified path.
        
        syntax: turn_data_into_json_file(path, data_to_turn_into_json)

        Takes 2 arguments
        path = path for file to be written to and name of file
        data_to_convert_to_json argument = the file to be stored as a json file'''
        with open(path, 'w') as fp:
            json.dump(data_to_convert_to_json, fp)# moving the json file to a different directory

    def list_zipper(self, list_1, list_2): 
        '''This method appends 2 lists together according to the index of each for the length of the shortest list.
        
        syntax: list_zipper(List_1, List_2)
        
        Requires 2 arguments
        List_1 and List_2 are the lists to be appended
        '''
        combined_list = []
        list_1_length = len(list_1)
        list_2_length = len(list_2)
        shortest = min(list_1_length, list_2_length)
        for i in range(shortest):
            combined_list.append([list_1[i], list_2[i]])
        return combined_list
    
    @staticmethod
    def create_dataframe(list_for_dataframe:list, *data):
        '''This method creates a dataframe from a list of crypto data and column heading arguments
        
        syntax: create_dataframe(list_for_dataframe, *data)'''
        return pd.DataFrame.from_records(list_for_dataframe, columns=[*data])
    
    @staticmethod
    def save_dataframe_locally( dataframe, 
                                path:str):
        return dataframe.to_csv(path_or_buf=path)

    @staticmethod
    def csv_to_dataframe(csv_path:str):
        return pd.read_csv(csv_path)
        
    @staticmethod
    def create_UUID_list(list_length:list):
        ''' 
        This method generates UUIDs for every record in the method attribute list and stores in a list, before concatenating the
        UUID with a list to generate a dictionary.
        
        syntax: UUID_dictionary(record_list)
        
        Takes 1 argument.
        record_list argument= the list of records which are to be concatenated to UUIDs
          '''
        uuid_list = []   
        #generate a pseudo-unique uuid for every record in the list by taking the length of the list
        for UUID in range(len(list_length)):
            #generates 1 uuid4 and converts to string (this is easier for dictionary saving to JSON)
            single_uuid = str(uuid.uuid4())
            #append the UUID to the list
            uuid_list.append(single_uuid)
            
        def create_dictionary_from_two_lists(list_1:list, list_2:list):
       
        #making the dictionary with the record list and the uuid list just generated
            record_uuid_dict = {}
            record_uuid_dict = dict(zip(list_1, list_2))
            return record_uuid_dict

    @staticmethod
    def turn_file_into_json_file( path:str, 
                                        file_to_turn_into_json:str):
        '''This method converts a file to a JSON file and saves it to a specified path.
        
        syntax: turn_file_into_json_file(path, dictionary_to_turn_into_json)

        Takes 2 arguments
        path argument = path for file to be written to and name of file
        file_to_turn_into_json argument = the file to be stored as a json file'''
        with open(path, 'w') as fp:
            json.dump(file_to_turn_into_json, fp)
    
    @staticmethod
    def crypto_data_UUID_list_dictionary(   record_list:list, 
                                            path:str):
        Dictionary = DataHandler.create_UUID_list(len(record_list))
        DataHandler.turn_file_into_json_file(path, Dictionary)
        return Dictionary

    @staticmethod
    def upload_file_to_s3(  file_path:str, 
                            bucket:str, 
                            object_name=None):
            
        """Upload a file to an S3 bucket

        :param file_name: File to upload (directory)
        :param bucket: Bucket to upload to (bucket name)
        :param object_name: S3 object name, the name you want to give the file. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """
        file_name = str(ntpath.basename(file_path))
        print(file_name) 
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = file_name
        # Create instance of S3 
        s3_client = boto3.client('s3')
        #Get S3 contents and norrow down by Prefix=file_name
        already_uploaded = s3_client.list_objects_v2(Bucket=bucket, Prefix=file_name)
        #If 'Contents' exists in the search then there must be a match
        if 'Contents' in already_uploaded:
             print('File already in bucket')
        else: s3_client.upload_file(file_path, bucket, object_name) 
        
    @staticmethod
    def upload_folder_to_S3(folder_path:str, 
                            bucket:str):
        s3_client = boto3.client('s3')
        for root,dirs,files in os.walk(folder_path):
            for file in files:
                file =str(file)
                already_uploaded = s3_client.list_objects_v2(Bucket=bucket, Prefix=file)
                print(already_uploaded)
                if 'Contents' in already_uploaded:
                    print('File already in bucket, no file uploaded') 
                else: s3_client.upload_file(os.path.join(root, file), bucket, file)

    @staticmethod
    def upload_table_from_csv_to_RDS(path_to_csv:str, 
                                    name_of_table:str):
        
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'cmc-scraper-mo.c4ojkdkakmcp.eu-west-2.rds.amazonaws.com' # Change it to your AWS endpoint
        USER = 'postgres'
        PASSWORD = 'ABC123!!'
        PORT = 5432
        DATABASE = 'postgres'
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        engine.connect()
        #import the .csv which is stored and convert back to a dataframe
        dataframe = pd.read_csv(path_to_csv)
        print(dataframe.head(10))
        dataframe.to_sql(name_of_table, engine)

    @staticmethod
    def get_RDS_to_dataframe(name_of_table=str):
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'cmc-scraper-mo.c4ojkdkakmcp.eu-west-2.rds.amazonaws.com' # Change it to your AWS endpoint
        USER = 'postgres'
        PASSWORD = 'ABC123!!'
        PORT = 5432
        DATABASE = 'postgres'
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        engine.connect()
        return pd.read_sql_table(name_of_table, engine)
   
    @staticmethod
    def get_all_available_webpages():
        #define date variables of first day of records and today's date to test all range of dates 
        first_day_on_record = date(2013, 4, 28)
        today = date.today()
        #turn into strings to allow input to the method
        first_day_on_record = str(first_day_on_record)
        today = str(today)
        #run the final method create_url_list_final
        all_available_records = CMCScraper.create_url_list_final(first_day_on_record, today, 1, 'https://coinmarketcap.com/historical/')
        df = pd.DataFrame(all_available_records, columns=["source_url"])
        return df

    @staticmethod
    def compare_dataframes( dataframe1, 
                            dataframe2):
        set_for_differences = set(dataframe1['source_url']).difference(set(dataframe2['source_url']))
        #return the list which has been reordered into dates: this is now the url list for rescraping
        return list(sorted(set_for_differences))    
    
    @staticmethod
    def compare_CSVs(   path_to_CSV1:str, 
                        path_to_CSV2:str):
        #Convert csv1 into df
        df1 = pd.read_csv(path_to_CSV1)
        #Convert csv2 into df
        df2 = pd.read_csv(path_to_CSV2)
        #Convert dfs to sets and then compare for differences
        into_dataframes = CMCScraper.compare_dataframes(df1, df2)
        return(into_dataframes)

if __name__ =="__main__":
    DataHandler()