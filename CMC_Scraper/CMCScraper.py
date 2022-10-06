from msilib.schema import Binary
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import logging
from botocore.exceptions import ClientError
import numpy as np
import os
import time
from os import listdir
from os.path import isfile, join
import pandas as pd
from pathlib import Path
import requests
from selenium.webdriver.common.by import By
import urllib.request
from DataHandler import DataHandling
import uuid
import json
import logging
import re
import boto3
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import inspect
import itertools
import ntpath






class CMCScraper:
    ''' Class for scraping data from Coin Market Cap, although much of this code could be easily adapted for other scraping applications.
    
    This class can generate a list of dates between 2 given dates and formats the list in order to  use them as permalinks, 
    carried out by the method 'daterange'. The second method 'create_url_list_with_date_permalinks' iteratively concatenates the 
    permalinks to a root url. The result of this is a list of urls which can be used to iterate through.
    Additionally, this class can scrape and save all crypto price records as well as images from a specified number of webpages, 
    as defined by the generated url list above'''
   
    def __init__(self):
        print('init started')
        self.crypto_rank_list =  []
        self.crypto_name_list = []
        self.crypto_market_cap_list = []
        self.crypto_price_list = []
        self.crypto_circulating_supply_list = []
        self.crypto_ticker_list = []
        self.crypto_price_change_list = []
        self.daily_records_combined_list = []
        self.total_entries = 0
        self.average_entries = 0
        self.total_entries_appended = 0
        self.number_of_downloads = 0
        self.total_name_entries = 0
        self.total_CS_entries = 0 
        self.total_MK_entries = 0 
        self.total_crypto_price_entries = 0 
        self.total_CT_entries = 0
        self.crypto_url_tag_list = []
        self.total_crypto_url_tag_entries = 0
        self.total_rank_entries = 0
        self.url_tag = str
        self.name_and_images_combined_list = []
        self.image_name_list = []
        self.user_friendly_tag_list = []

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
        
        date_list = CMCScraper.daterange(start_date, end_date, frequency)
        final_url_list = CMCScraper.__create_url_list_with_date_permalinks(root_url, date_list)
        return final_url_list
        

    def __get_image_src_list_from_webpage ( self, 
                                            url:str):
        '''This method generates a list of URLS corresponding to data from a webpage and retrieves only .png
        files. This will only get the first 10 images since the rest of the images are dynamically accessed.
        
        syntax: get_image_src_list_from_webpage(url)
        
        Takes 1 argument (likely inherited from url_list in parent method)
        url argument = the webpage url to scrape and retrieve the images
        '''
        
        #create BS object
        soup = self.__get_soup(url)
        print(f'Page scraped: {url}')
        #create a variable for the table rows (tr), limited to the length of the number of table rows on the page
        image_table_rows = soup.find_all('tr', attrs={'class':'cmc-table-row'})
        #scrape the crypo name data
        for crypto_name_area in image_table_rows:
            #get the actual name
            name_column = crypto_name_area.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sticky cmc-table__cell--sortable cmc-table__cell--left cmc-table__cell--sort-by__name'})
                #Prevents None error if the loop conitnues further than the available rows for scraping 
            if name_column == None:
                    break
                #find the column within the row and strip the text
            crypto_name = name_column.find('a', attrs={'class': 'cmc-table__column-name--name cmc-link'}).text.strip()
            #append names into list   
            self.image_name_list.append(crypto_name)
            # find images in same row
            image = name_column.find('img')
            #Prevents iterating too far and returning None, which would break the scraper 
            if image == None:
                break
            #extract only src
            image = image['src']
            #pairs the name and image src scraped from the same row to generate a "friendly" name tag
            crypto_name_and_image_single = [crypto_name, image]
            if crypto_name_and_image_single not in self.name_and_images_combined_list:
                self.name_and_images_combined_list.append(crypto_name_and_image_single)
            #prevent_rescrape of image_list elements
            if image not in self.image_list:
                self.image_list.append(image)
        #length of image_list to be used as an assertion
        self.one_day_image_list_length = len(self.image_list) 
        #append daily records to the master list
        
    def __save_images_from_webpage  (self, 
                                    path:str):
        '''This method retrieves and saves the images generated in method 'get_image_src_list_from_webpage' to an indicated
        path
        
        syntax: save_images_from_webpage(path)
        
        Takes 1 argument
        path argument = the path to save the file once retrieved (the file name is modified for every unique image). 
        '''
        len_path = len(path)
        #loop to iterate through the image list, using enumerate method to rename the file after every iteration
        for i, image in enumerate(self.image_list, 1):
            #renaming the file
            path = f'{path[:len_path]}\{i}.png' 
            #code to prevent redownloading of duplicates from previous iterations of the enumeration loop
            if os.path.exists(path):
                pass
            else:
                #retrieve the image and save with path
                urllib.request.urlretrieve(image, path)
            #counts the number of image downloads
            self.number_of_downloads = i

    def save_images_from_multiple_webpages( self, 
                                            url_list:list, 
                                            num_pages:int, 
                                            path:str):
        '''Method which incorporates previous methods to scrape multiple webpages, retrieve the images and save images locally.
        
        syntax: save_images_from_multiple_webpages(url_list, num_pages, path)
       
        Takes 3 arguments
        url_list argument = the list of urls to iterate through when scraping
        num_pages argument= The number of pages which are iterated through 
        path argument= The folder path for saving the first document once retrieved (the file name is modified for every unique image). 
        '''
        #Looping through the method which scrapes the images src and name for given number of pages
        for url in url_list[:num_pages]:
            self.__get_image_src_list_from_webpage(url)
        #After all is scraped, the images are downloaded and saved in folder with path 
        self.__save_images_from_webpage(path)
        return self.image_list
        
    def __scrape_items_from_row(self):   
        ''' This function scrapes the data from one of the cryptocurrency rows generated in the function 'get_crypto_rows'. 
        
        In this function, the crypto name, price, ticker, market cap and circulating supply are stored in individual lists. Each value, 
        for example price, is stored in a list of each of the cryptocurrencies from that day. For example, all of the names of cryptocurrencies
        scraped from a particular webpage (corresponding to a particular date) would be contained in the list crypto_name_list. 

        syntax: scrape_item_from_row()
        
        Requires 0 arguments 
        '''
        #start counter
        count = 0
        for row in self.tr:
            #store the name of the coin as a variable by finding td element (column) 
            name_column = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sticky cmc-table__cell--sortable cmc-table__cell--left cmc-table__cell--sort-by__name'})
            #Prevents None error if the loop conitnues further than the available rows for scraping 
            if name_column == None:
                break
            #find the column within the row and strip the text
            crypto_name = name_column.find('a', attrs={'class': 'cmc-table__column-name--name cmc-link'}).text.strip()
            #find and create variable for crypto_rank
            crypto_rank = int(row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sticky cmc-table__cell--sortable cmc-table__cell--left cmc-table__cell--sort-by__rank'}).text.strip())
            #Getting the first letter of the crypto name to check if it is in the ticker in the assertion below
            crypto_name_first_index = crypto_name[0].upper()
            #find and createv variable for market cap with currency sign
            crypto_market_cap = str(row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__market-cap'}).text.strip())
            #Remove all symbols and anything else which is non-numeric
            crypto_market_cap = re.sub("[^\d\.]", "", crypto_market_cap)
            #There are some instances in which '--' denotes none. Since the symbols are removed abve, this results in ''. As such this is replaced with 0. Also converted to float
            if crypto_market_cap == '':
                crypto_market_cap = float(0)
            #Convert all to float
            else: crypto_market_cap = float(crypto_market_cap)
            #Find and create variable for the price with currency sign
            crypto_price = str(row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__price'}).text.strip())
            #Remove all symbols and anything else which is non-numeric
            crypto_price = re.sub("[^\d\.]", "", crypto_price)
            #There are some instances in which '--' denotes none. Since the symbols are removed abve, this results in ''. As such this is replaced with 0. Also converted to float
            if crypto_price == '':
                crypto_price = float(0)
            #Convert all to float
            else: crypto_price = float(crypto_price)
            #Find and create variable for the circulating supply with ticker
            crypto_circulating_supply_and_ticker = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__circulating-supply'}).text.strip()
            #Find and create variable for the circulating supply by splitting the supply+ticker variable
            crypto_ticker = crypto_circulating_supply_and_ticker.split(' ')[1]
            #Find and create variable for the coin ticker
            crypto_circulating_supply = crypto_circulating_supply_and_ticker.split(' ')[0]
            #Remove all symbols and anything else which is non-numeric
            crypto_circulating_supply = re.sub("[^\d\.]", "", crypto_circulating_supply)
             #There are some instances in which '--' denotes none. Since the symbols are removed abve, this results in ''. As such this is replaced with 0. Also converted to float
            if crypto_circulating_supply == '':
                crypto_circulating_supply = float(0)
            #convert all to float
            else: crypto_circulating_supply = float(crypto_circulating_supply)
            #Find and create variable for 24 hour % change in price
            crypto_price_change = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__percent-change-24-h'}).text.strip()
            #remove % symbol, also if there is no change it is marked as '--' by CMC, so need to check that before converting to float as it will break the scraper, if it is then will convert to value float 0
            crypto_price_change = re.sub("[^\d\.]", "", crypto_price_change)
            if crypto_price_change == '':
                crypto_price_change = float(0)
                #convert all to float
            else: crypto_price_change = float(crypto_price_change)
            #Some exceptions to the assertion rule
            if crypto_ticker == 'PTS':
                pass 
            elif crypto_name == 'Kittehcoin' or 'Electric' or 'Stellar':
                pass
            else: assert crypto_name_first_index in crypto_ticker, "The crypto name does not correspond to the crypto ticker"
            #append the data to the associated 
            self.crypto_url_tag_list.append(self.url_tag) 
            self.crypto_rank_list.append(crypto_rank)
            self.crypto_name_list.append(crypto_name)
            self.crypto_market_cap_list.append(crypto_market_cap)
            self.crypto_price_list.append(crypto_price)
            self.crypto_circulating_supply_list.append(crypto_circulating_supply)
            self.crypto_ticker_list.append(crypto_ticker)
            self.crypto_price_change_list.append(crypto_price_change)
            # increase the counter for appending rows within 1 day   
            count += 1
            #limits the number of iterations to the number of rows
            if count == self.tr_length:
                break
    
    def __get_soup( self,
                    url:str
                    ):
        '''Requires 2 arguments
        num_pages argument = number of webpages to iterate through from the url_list
        url_list argument = the list with urls to iterate through'''
       
        #request webpage
        webpage = requests.get(url)
        #hold on a tick to prevent skipping urls
        time.sleep(0.5)
        #parse the html
        soup = BeautifulSoup(webpage.text, 'html.parser')
        #create a variable for the table rows (tr), limited to the length of the number of table rows on the page
        return soup
    
    def __get_crypto_rows(  self ,
                            url_list:list,
                            num_pages:int):
        '''This method scrapes each row of data correlating to the associated cryptocurrency.
        
        Example use case: Scraping a row of Bitcoin data  from a particular webpage (date). The data included in a 
        row are name, market cap, price, circulating supply and crypto ticker
        
        syntax:  crypto_scrape_get_crypto_rows(num_pages, url_list)
        
        Requires 2 arguments
        num_pages argument = number of webpages to iterate through from the url_list
        url_list argument = the list with urls to iterate through
          '''
        #creating count for each iteration below
        count = 0
        #iterates through the url_list from create_url_final, limited by parameter 'num_pages' which is the number of pages 
        for url in url_list[:num_pages]:
            #bringing in url_tag from __scrape_items_from_row method
            self.url_tag = url
            #separate function to create BS object
            soup = self.__get_soup(url)
            #get all rows
            self.tr = soup.find_all('tr', attrs={'class':'cmc-table-row'})
            #Gets the number of records per page, useful for scraping all records 
            self.tr_length = len(self.tr)
            #call the function iteratively
            self.__scrape_items_from_row()
            #increase the count above for each iteration
            count += 1
            print(f'Page scraped: {self.url_tag}')
        #getting lengths of lists for assertions and checks later dowjn the line 
        self.total_crypto_url_tag_entries = len(self.crypto_url_tag_list)
        self.total_rank_entries = len(self.crypto_rank_list)
        self.total_name_entries = len(self.crypto_name_list)
        self.total_CS_entries = len(self.crypto_circulating_supply_list)
        self.total_MK_entries = len(self.crypto_market_cap_list)
        self.total_crypto_price_entries = (len(self.crypto_price_list))
        self.total_CT_entries = (len(self.crypto_ticker_list))
        self.total_price_change_entries = len(self.crypto_price_change_list)
            
        #Getting sum total of the entries then dividing by the number of categories to get total and average entries, respectively
        self.total_entries = self.total_crypto_url_tag_entries + self.total_rank_entries + self.total_name_entries + self.total_CS_entries + self.total_MK_entries + self.total_crypto_price_entries + self.total_CT_entries + self.total_price_change_entries
        self.average_entries = int(self.total_entries / 8)

        assert self.average_entries == self.total_CT_entries, "The total_name_entries is not equal to total_CT_entries"
            
        return self.crypto_url_tag_list, self.crypto_rank_list, self.crypto_name_list, self.crypto_market_cap_list, self.crypto_price_list,  self.crypto_circulating_supply_list, self.crypto_ticker_list, self.crypto_price_change_list
            
   
    def __generate_user_friendly_tag(self):

        for i in range(len(self.crypto_name_list)):
            user_friendly_tag_list = self.crypto_name_list[i]+ f' {self.crypto_url_tag_list[i]}'
            self.user_friendly_tag_list.append (user_friendly_tag_list)
    
    def __daily_record_concatenater(self):    
        '''This code packages each record into a list: for example BTC price from a particular date. 
        
        The generated lists can then be added to a dictionary. This function could be broadly applicable
        to any collection of lists which yield corresponding data from the same index. 
        
        syntax daily_record_concatenater()
        
        requires 0 arguments
        '''
        #iterates for the number of elements in url_tag_list
        for i in range(len(self.crypto_url_tag_list)):
            self.daily_records_combined_list.append([self.user_friendly_tag_list[i], self.crypto_url_tag_list[i], self.crypto_rank_list[i], self.crypto_name_list[i],self.crypto_market_cap_list[i],self.crypto_price_list[i],self.crypto_circulating_supply_list[i],self.crypto_ticker_list[i], self.crypto_price_change_list[i]]) 
        self.total_entries_appended = len(self.daily_records_combined_list)
        return self.daily_records_combined_list  
    
    
    def get_crypto( self, 
                    url_list:list, 
                    num_pages=None):
        if num_pages == None:
            num_pages = len(url_list)
        self.__get_crypto_rows(url_list, num_pages)
        self.__generate_user_friendly_tag()
        all_scraped_data_list = self.__daily_record_concatenater()
        assert self.total_entries_appended == self.average_entries, "The number of total entries in the appended list does not match the total_crypto_url_tag_entries"
        return all_scraped_data_list 

    @staticmethod
    def create_crypto_dataframe(list_of_lists_for_table:list):
        return pd.DataFrame.from_records(list_of_lists_for_table, columns=["ID", "source_url", "Rank", "Name", "Market Capitalisation", "Price", "Circulating Supply", "Ticker", "24 h change"])
    
    @staticmethod
    def save_dataframe_locally( dataframe, 
                                path:str):
        return dataframe.to_csv(path_or_buf=path)

    @staticmethod
    def csv_to_dataframe(csv_path:str):
        return pd.read_csv(csv_path)
        
    @staticmethod
    def UUID_dictionary(record_list:list):
        ''' 
        This method generates UUIDs for every record in the method attribute list and stores in a list, before concatenating the
        UUID with a list to generate a dictionary.
        
        syntax: UUID_dictionary(record_list)
        
        Takes 1 argument.
        record_list argument= the list of records which are to be concatenated to UUIDs
          '''
        uuid_list = []   
        #generate a pseudo-unique uuid for every record in the list by taking the length of the list
        for UUID in range(len(record_list)):
            #generates 1 uuid4 and converts to string (this is easier for dictionary saving to JSON)
            single_uuid = str(uuid.uuid4())
            #append the UUID to the list
            uuid_list.append(single_uuid)
            
        #making the dictionary with the record list and the uuid list just generated
        record_uuid_dict = {}
        record_uuid_dict = dict(zip(uuid_list, record_list))
        return record_uuid_dict

    @staticmethod
    def turn_dictionary_into_json_file( path:str, 
                                        file_to_turn_into_json:str):
        '''This method converts a file to a JSON file and saves it to a specified path.
        
        syntax: turn_dictionary_into_json_file(path, dictionary_to_turn_into_json)

        Takes 2 arguments
        path argument = path for file to be written to and name of file
        file_to_turn_into_json argument = the file to be stored as a json file'''
        with open(path, 'w') as fp:
            json.dump(file_to_turn_into_json, fp)
    
    @staticmethod
    def crypto_data_UUID_list_dictionary(   record_list:list, 
                                            path:str):
        Dictionary = CMCScraper.UUID_dictionary(record_list)
        CMCScraper.turn_dictionary_into_json_file(path, Dictionary)
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
   
    def upload_data_to_pre_existing_RDS(self, 
                                        sql_table_name:str):
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'cmc-scraper-mo.c4ojkdkakmcp.eu-west-2.rds.amazonaws.com' 
        USER = 'postgres'
        PASSWORD = 'ABC123!!'
        PORT = 5432
        DATABASE = 'postgres'
        #assemble connection credentials
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        #connect to RDS
        engine.connect()
        #reads the sql table and converts to dataframe
        sql_df = pd.read_sql_table(sql_table_name, engine) 
        print(f'sql_df: {sql_df}')
        #creates a dataframe of all available urls from first date to present day
        all_available_entries = CMCScraper.get_all_available_webpages()
        #comares both dataframes for differences and returns a list of urls yet to be scraped
        comparison = CMCScraper.compare_dataframes(all_available_entries, sql_df)
        print(f'comparison: {comparison}')
        #retrieves the remaining data to be scraped
        get_remaining_data = self.get_crypto(comparison)
        #Creates a dataframe of the freshly-scraped data
        df_of_fresh_data = CMCScraper.create_crypto_dataframe(get_remaining_data)
        print(f'df of fresh data {df_of_fresh_data}')
        #Uploads to sql
        df_of_fresh_data.to_sql(sql_table_name, engine, if_exists='append', index= False)

if __name__ =="__main__":
    yolo = CMCScraper()
    all_urls = yolo.create_url_list_final('04-28-2013', '05-23-2013', 1, 'https://coinmarketcap.com/historical/')
    all_data = yolo.get_crypto(all_urls, len(all_urls))
    dataframe = yolo.create_crypto_dataframe(all_data)
    print(dataframe)
    #csv = yolo.save_dataframe_locally(dataframe, r"C:\Users\marko\DS Projects\Data\scrape_up_to_23-09-22.csv")
    #dictionary = yolo.crypto_data_UUID_list_dictionary(all_data, r"C:\Users\marko\DS Projects\Data\scrape_up_to_23-09-22.json")
    #yolo.upload_data_to_pre_existing_RDS('crypto_datatable')
    #new_RDS = yolo.get_RDS_to_dataframe('crypto_datatable')
    #print(new_RDS)
    #yolo.upload_table_from_csv_to_RDS(r"C:\Users\marko\DS Projects\Data\scrape_up_to_23-09-22.csv", 'crypto_datatable')
    #dataframe = pd.read_csv(r"C:\Users\marko\DS Projects\Data\scrape_up_to_23-09-22.csv")
    #dataframe[["Market Capitalisation","Price", 'Circulating Supply', '24 h change']] = dataframe[["Market Capitalisation","Price", 'Circulating Supply', '24 h change']].apply(pd.to_numeric)
    #print(dataframe)