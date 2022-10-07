from datetime import date 
from sqlalchemy import create_engine
import boto3
import json
import ntpath
import os
import pandas as pd
import uuid

class DataHandler:
    
    def __init__(self):
        pass

    @staticmethod
    def daterange(  start_date:str, 
                    end_date:str, 
                    frequency:int):
        '''This method generates a range of dates between 2 given dates which is converted to a string list.
        
        syntax: daterange(start_date, end_date, frequency)
        
        Takes 3 arguments
        start_date argument = the date to begin the date_range, in the format "mm-dd-yyyy" (pandas does not accept british date format) including the inverted commas.
        end_date argument = the date to end the date range, in the format "mm-dd-yyyy" (pandas does not accept british date format) including the inverted commas
        frequency argument= an integer which dictates the frequency of the dates in the list. For example, for generating permalinks
        for coinmarketcap.com this could be weekly, so 7 is the frequency. The first date on coinmarketcap.com is 28 Apr 2013
        
        '''
        #generate list of unformatted dates between 2 dates
        
        date_list_unformatted = pd.date_range(start=start_date, end=end_date)

        print(date_list_unformatted)
        #format date to match with the required use (in this example for URL permalinks)
        date_list_all = date_list_unformatted.strftime('%Y%m%d/')
        #slice based on the required frequency of dates
        date_list = date_list_all[::frequency]
        return date_list
        
    @staticmethod
    def __create_url_list_with_date_permalinks( root_url:str, 
                                                date_list:list):
        '''Method for concatenating list of permalinks to given url, returning a list of unique urls containing url and permalink.
        
        syntax: create_url_list_with_date_permalinks(root_url, date_list)
        
        Takes 2 arguments
        root_url argument = the url root address with which to concatenate the permalink list
        date_list argument = predefined date_list from daterange method'''

        url_list = []
        for url_extension in date_list:
            #concatenate the root_url with the url permalink
            url_instance = root_url + str(url_extension)
            #append into list
            url_list.append(url_instance)
        return url_list
    
    @staticmethod
    def create_url_list_final(   
                                start_date:str, 
                                end_date:str, 
                                frequency:int,  
                                root_url:str):
        '''Method which creates a list of urls by combining a list of pre-generated and formatted date permalinks (exectuted
        by 'daterange' method call) and then concatenating the date permalinks to a root url (executed by 'create_url_list_with_date_permalinks'
        method call) 
        
        syntax: create_url_list_final(start_date, end_date, frequency,  root_url)
        
        Takes 4 arguments
        start_date argument = the date to begin the date_range, in the format "mm-dd-yyyy" including the inverted commas.
        end_date argument = the date to end the date range, in the format "mm-dd-yyyy" including the inverted commas.
        frequency argument = an integer which dictates the frequency of the dates in the list. For example, for generating permalinks
        root_url argument = the url root address with which to concatenate the permalink list'''
        
        date_list = DataHandler.daterange(start_date, end_date, frequency)
        final_url_list = DataHandler.__create_url_list_with_date_permalinks(root_url, date_list)
        return final_url_list
        

    @staticmethod
    def create_dict_from_2_lists(list_1:list, list_2:list):
        '''This method creates a dictionary from 2 lists.
        
        syntax: create_dict_from_2_lists(list_1:list, list_2:list)
        
        Takes 2 arguments.
        list_1 and list_2 are the 2 lists to be converted into a dictionary'''
        
        record_uuid_dict = dict(zip(list_1, list_2))
        
        return record_uuid_dict
            
    
    def turn_data_into_file(self, path:str, data_to_convert_into_file):
        '''This method converts data to a JSON file and saves it to a specified path.
        
        syntax: turn_data_into_json_file(path:str, data_to_turn_into_file)

        Takes 2 arguments
        path = path for file to be written to and name of file
        data_to_convert_to_json argument = the data to be stored as a file'''
        with open(path, 'w') as fp:
            json.dump(data_to_convert_into_file, fp)

    def list_zipper(self, list_1:list, list_2:list): 
        '''This method appends 2 lists together according to the index of each, for the length of the shortest list.
        
        syntax: list_zipper(list_1:list, list_2:list)
        
        Requires 2 arguments
        list_1 and list_2 are the lists to be appended
        '''
        combined_list = []
        list_1_length = len(list_1)
        list_2_length = len(list_2)
        shortest_list_length = min(list_1_length, list_2_length)
        for i in range(shortest_list_length):
            combined_list.append([list_1[i], list_2[i]])
        return combined_list
    
    @staticmethod
    def create_dataframe(list_for_dataframe:list, *headings):
        '''This method creates a dataframe from a list of crypto data and column heading arguments
        
        syntax: create_dataframe(list_for_dataframe:list, *headings)
        list_for_dataframe = the list to convert to dataframe, including list of lists. There is a heading for each list element
        *headings = the headings required for each element in list'''
        return pd.DataFrame.from_records(list_for_dataframe, columns=[*headings])
    
    @staticmethod
    def save_dataframe_locally( dataframe, 
                                path_for_new_csv:str):

        '''This method converts a dataframe to csv which is saved locally
        
        syntax: ave_dataframe_locally(dataframe, path:str) 
                                
        Takes 2 arguments.

        dataframe = dataframe to be saved
        path = path to be store the dataframe including .csv file extension'''
        return dataframe.to_csv(path_or_buf=path_for_new_csv)

    @staticmethod
    def csv_to_dataframe(csv_path:str):
        '''This method converts a csv file to a dataframe which is saved locally
        
        syntax: csv_to_dataframe(csv_path:str) 
                                
        Takes 1 argument.

        path = path to the csv file including .csv file extension'''
        return pd.read_csv(csv_path)
        
    @staticmethod
    def create_UUID_list(list_length:int):
        ''' 
        This method generates a list of UUIDs according to predetermined length
        
        syntax: create_UUID_list(list_length:int)
        
        Takes 1 argument.
        list_length = the required UUID list length as integer
          '''
        uuid_list = []   
        #generate a pseudo-unique uuid for every record in the list by taking the length of the list
        for UUID in range(list_length):
            #generates 1 uuid4 and converts to string (this is easier for dictionary saving to JSON)
            single_uuid = str(uuid.uuid4())
            #append the UUID to the list
            uuid_list.append(single_uuid)
        return uuid_list
        
            
        @staticmethod
        def create_dictionary_from_two_lists(list_1:list, list_2:list):
            '''This method creates a dictionary from 2 lists
            
            syntax create_dictionary_from_two_lists(list_1:list, list_2:list)
            
            Takes 2 arguments: the 2 lists to be converted into a dictionary'''
       
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
            
        """This method uploads a file to an S3 bucket

        syntax: upload_file_to_s3(file_path:str, bucket:str, object_name=None)
        
        Takes 2 arguments and one optional argument 
        file_name: File to upload (directory)
        bucket: Bucket to upload to (bucket name)
        object_name: S3 object name, the name you want to give the file. If not specified then file_name is used
        return: True if file was uploaded, else False
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
        """This method uploads a folder to an S3 bucket

        syntax: upload_folder_to_s3(folder_path:str, bucket:str)
        
        Takes 2 arguments 
        folder_name: folder to upload (directory)
        bucket: bucket to upload to (bucket name)
        return: True if file was uploaded, else False
        """
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
        '''This method uploads a .csv file to RDS.
        
        syntax: upload_table_from_csv_to_RDS(path_to_csv:str, name_of_table:str)
        
        Takes 2 arguments:
        path_to_csv = the path to the .csv file
        name_of_table = the name of the table in the RDS to upload to '''
        
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'cmc-scraper-mo.c4ojkdkakmcp.eu-west-2.rds.amazonaws.com' 
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
        '''This method downloads the contents of an RDS table and converts to a dataframe
        
        syntax: get_RDS_to_dataframe(name_of_table=str)
        
        Takes 1 argument
        name_of_table = the name of the  table from RDS to get contents of '''
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'cmc-scraper-mo.c4ojkdkakmcp.eu-west-2.rds.amazonaws.com'
        USER = 'postgres'
        PASSWORD = 'ABC123!!'
        PORT = 5432
        DATABASE = 'postgres'
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        engine.connect()
        return pd.read_sql_table(name_of_table, engine)
   
    @staticmethod
    def get_all_available_webpages():
        '''This method considers the current date to get all historical available daily records of coin market cap and returns a dataframe of dates
        
        syntax: get_all_available_webpages()

        Takes 0 arguments
        '''
        #define date variables of first day of records and today's date to test all range of dates 
        first_day_on_record = date(2013, 4, 28)
        today = date.today()
        #turn into strings to allow input to the method
        first_day_on_record = str(first_day_on_record)
        today = str(today)
        #run the final method create_url_list_final
        all_available_records = DataHandler.create_url_list_final(first_day_on_record, today, 1, 'https://coinmarketcap.com/historical/')
        df = pd.DataFrame(all_available_records, columns=["source_url"])
        return df

    @staticmethod
    def compare_dataframes( dataframe1,
                            dataframe_1_column_name:str,
                            dataframe2,
                            dataframe_2_column_name:str):
        ''' This method compares nominated columns in 2 dataframes and returns a list of the differences between each column
        
        syntax: compare_dataframes(dataframe1, dataframe_1_column_name:str, dataframe2, dataframe_2_column_name:str)
        
        takes 4 arguments
        dataframe1 and dataframe 2 are the 2 dataframes to compare
        dataframe_x_column_name are the corresponding dataframe columns to be compared'''
        set_for_differences = set(dataframe1[dataframe_1_column_name]).difference(set(dataframe2[dataframe_2_column_name]))
        #return the list which has been reordered into dates: this is now the url list for rescraping
        return list(sorted(set_for_differences))    
    
    @staticmethod
    def compare_CSVs(   path_to_CSV1:str,
                        csv_1_column_name:str, 
                        path_to_CSV2:str,
                        csv_2_column_name:str):
        '''This method compares 2 .csv files for differences, returns list of differences between the 
        
        syntax: compare_CSVs(path_to_CSV1:str, path_to_CSV2:str)
        
        Takes 4 arguments
        path_to_compare_CSVx= string arguments for each of the .csv files for comparison
        csv_x_column_name= the columns within the .csv files to be compared
        '''
        #Convert csv1 into df
        df1 = pd.read_csv(path_to_CSV1)
        #Convert csv2 into df
        df2 = pd.read_csv(path_to_CSV2)
        #Convert dfs to sets and then compare for differences
        into_dataframes = DataHandler.compare_dataframes(df1, csv_1_column_name, df2, csv_2_column_name)
        return(into_dataframes)

if __name__ =="__main__":
    yolo = DataHandler()
    


    