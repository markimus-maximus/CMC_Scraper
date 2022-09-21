from msilib.schema import Binary
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import logging
from botocore.exceptions import ClientError
import numpy as np
import os
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
import boto3
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import inspect






class CMCScraper:
    ''' Class for scraping data from Coin Market Cap, although much of this code could be easily adapted for other scraping applications.
    
    This class can generate a list of dates between 2 given dates and formats the list in order to  use them as permalinks, 
    carried out by the method 'daterange'. The second method 'create_url_list_with_date_permalinks' iteratively concatenates the 
    permalinks to a root url. The result of this is a list of urls which can be used to iterate through.
    Additionally, this class can scrape and save all crypto price records as well as images from a specified number of webpages, 
    as defined by the generated url list above'''
   
    def __init__(self):
        print('init started')
        
        self.date_list_weekly = []

        self.date_list_unformatted = []

        self.date_list_all = []
    
        self.uuid_list = []
    
        self.record_uuid_dict = {}

        self.crypto_rank_list =  []

        self.crypto_name_list = []
    
        self.crypto_market_cap_list = []

        self.crypto_price_list = []
    
        self.crypto_circulating_supply_list = []

        self.crypto_ticker_list = []

        self.crypto_price_change_list = []
        
        self.daily_records_combined_list = []

        self.image_list = []

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
        
        self.record_uuid_dict = {}

        self.name_list_and_images_one_day = []

        self.name_list_and_images_all = []

        self.image = str

        self.crypto_name = str

        
    def __daterange(self, start_date, end_date, frequency):
        '''This method generates a range of dates between 2 given dates which is converted to a string list.
        
        syntax: daterange(start_date, end_date, frequency)
        
        Takes 3 arguments
        start_date argument = the date to begin the date_range, in the format "dd-mm-yyyy" including the inverted commas.
        end_date argument = the date to end the date range, in the format "dd-mm-yyyy" including the inverted commas
        frequency argument= an integer which dictates the frequency of the dates in the list. For example, for generating permalinks
        for coinmarketcap.com this could be weekly, so 7 is the frequency. The first date on coinmarketcap.com is 28 Apr 2013
        
        '''
        #generate list of unformatted dates between 2 dates
        date_list_unformatted = pd.date_range(start= start_date, end = end_date)
        #format date to match with the required use (in this example for URL permalinks)
        date_list_all = date_list_unformatted.strftime('%Y%m%d/')
        #slice based on the required frequency of dates
        date_list = date_list_all[::frequency]
        return date_list
        

    def __create_url_list_with_date_permalinks(self, root_url, date_list):
        '''Method for concatenating list of permalinks to given url, returning a list of unique urls containing url and permalink.
        
        syntax: create_url_list_with_date_permalinks(root_url, date_list)
        
        Takes 2 arguments
        root_url argument = the url root address with which to concatenate the permalink list
        date_list argument = predefined date_list from daterange method'''

        final_url_list = []
        
        for url_extension in date_list:
            #concatenate the root_url with the url permalink
            url_instance = root_url + str(url_extension)
            #append into list
            final_url_list.append(url_instance)
        return final_url_list

    def create_url_list_final(self, start_date, end_date, frequency,  root_url):
        '''Method which creates a list of urls by combining a list of pre-generated and formatted date permalinks (exectuted
        by 'daterange' method call) and then concatenating the date permalinks to a root url (executed by 'create_url_list_with_date_permalinks'
        method call) 
        
        syntax: create_url_list_final(start_date, end_date, frequency,  root_url)
        
        Takes 4 arguments
        start_date argument = the date to begin the date_range, in the format "dd-mm-yyyy" including the inverted commas.
        end_date argument = the date to end the date range, in the format "dd-mm-yyyy" including the inverted commas
        frequency argument= an integer which dictates the frequency of the dates in the list. For example, for generating permalinks
        root_url argument = the url root address with which to concatenate the permalink list'''
        
        date_list = self.__daterange(start_date, end_date, frequency)
        final_url = self.__create_url_list_with_date_permalinks(root_url, date_list)
        return final_url
        

    def __get_image_src_list_from_webpage(self, url):
        '''Thi__s method generates a list of URLS corresponding to data from a webpage and retrieves only .png
        files. This will only get the first 10 images since the rest of the images are dynamically accessed.
        
        syntax: get_image_src_list_from_webpage(url)
        
        Takes 1 argument (likely inherited from url_list in parent method)
        url argument = the webpage url to scrape and retrieve the images
         '''
        #name_list_and_images_one_record = []
        
        #request webpage
        webpage = requests.get(url)
        
        #parse the html
        soup = BeautifulSoup(webpage.text, 'html.parser')

        
        #create a variable for the table rows (tr), limited to the length of the number of table rows on the page
        image_table_rows = soup.find_all('tr', attrs={'class':'cmc-table-row'})
        
        for crypto_name_area in image_table_rows:
            
            
            name_column = crypto_name_area.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sticky cmc-table__cell--sortable cmc-table__cell--left cmc-table__cell--sort-by__name'})
                #Prevents None error if the loop conitnues further than the available rows for scraping 
            if name_column == None:
                    break

                #find the column within the row and strip the text
            self.crypto_name = name_column.find('a', attrs={'class': 'cmc-table__column-name--name cmc-link'}).text.strip()
            #append names into list   
            
            # find images in same row
            self.image = name_column.find('img')
            if self.image == None:
                    self.image = 'None retrieved'
            #find only src
            else: self.image = self.image['src']

            
            #ensure that only .png files are saved 
            if '.png' not in self.image:
                pass
            
            #prevent rescraping
            elif self.crypto_name in self.name_list_and_images_all:
                pass
            
            #appends stripped url to list
            else:
                self.image_list.append(self.image)
                name_list_and_images_one_record =[self.image, self.crypto_name]
                self.name_list_and_images_one_day.append(name_list_and_images_one_record)
            
            #self.name_list_and_images.append(name_list_and_images_one_record)
        #length of image_list to be used as an assertion
        self.one_day_image_list_length = len(self.image_list) 
        self.name_list_and_images_all.append(self.name_list_and_images_one_day)
        print(self.name_list_and_images_all)
        
    
    def __save_images_from_webpage(self, path):
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

        
        
    def save_images_from_multiple_webpages(self, url_list, num_pages, path):
        '''Method which incorporates previous methods to scrape multiple webpages, retrieve the images and save images locally.
        
        syntax: save_images_from_multiple_webpages(url_list, num_pages, path)
       
        Takes 3 arguments
        url_list argument = the list of urls to iterate through when scraping
        num_pages argument= The number of pages which are iterated through 
        path argument= The folder path for saving the first document once retrieved (the file name is modified for every unique image). 
        '''
        #Looping through the 2 methods
        for url in url_list[:num_pages]:
            
            self.__get_image_src_list_from_webpage(url)
            self.__save_images_from_webpage(path)
        
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
            crypto_rank = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sticky cmc-table__cell--sortable cmc-table__cell--left cmc-table__cell--sort-by__rank'}).text.strip()
            #Getting the first letter of the crypto name to check if it is in the ticker in the assertion below
            crypto_name_first_index = crypto_name[0].upper()
            #find and createvvariable for market cap
            crypto_market_cap = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__market-cap'}).text.strip()
            #Find and create variable for the price
            crypto_price = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__price'}).text.strip()
            #Find and create variable for the circulating supply
            crypto_circulating_supply_and_ticker = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__circulating-supply'}).text.strip()
            #Find and create variable for the circulating supply by splitting the supply+ticker variable
            crypto_ticker = crypto_circulating_supply_and_ticker.split(' ')[1]
            #Find and create variable for the coin ticker
            crypto_circulating_supply = crypto_circulating_supply_and_ticker.split(' ')[0]
            #Find and create variable for 24 hour % change in price
            crypto_price_change = row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sortable cmc-table__cell--right cmc-table__cell--sort-by__percent-change-24-h'}).text.strip()

            
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
  
    
    def __get_crypto_rows(self, url_list, num_pages):
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
            #request webpage
            webpage = requests.get(url)
            #parse the html
            soup = BeautifulSoup(webpage.text, 'html.parser')
            #create a variable for the table rows (tr), limited to the length of the number of table rows on the page
            self.tr = soup.find_all('tr', attrs={'class':'cmc-table-row'})
            #Gets the number of records per page, useful for scraping all records 
            self.tr_length = len(self.tr)
            #call the function iteratively
            self.__scrape_items_from_row()
            #increase the count above for each iteration
            count += 1

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
            
   
    def __daily_record_concatenater(self):    
        '''This code packages each record into a list: for example BTC price from a particular date. 
        
        The generated lists can then be added to a dictionary. This function could be broadly applicable
        to any collection of lists which yield corresponding data from the same index. 
        
        syntax daily_record_concatenater()
        
        requires 0 arguments
        '''
        for i in range(len(self.crypto_url_tag_list)):
            self.daily_records_combined_list.append([self.crypto_url_tag_list[i], self.crypto_rank_list[i], self.crypto_name_list[i],self.crypto_market_cap_list[i],self.crypto_price_list[i],self.crypto_circulating_supply_list[i],self.crypto_ticker_list[i], self.crypto_price_change_list[i]]) 
        self.total_entries_appended = len(self.daily_records_combined_list)
        return self.daily_records_combined_list  
    
    
    def get_crypto(self, url_list, num_pages):
        if self.url_tag in self.crypto_url_tag_list:
            print('crypto_data_rescrape attempt')
            pass
        else:
            self.__get_crypto_rows(url_list, num_pages)
            all_scraped_data_list = self.__daily_record_concatenater()
        assert self.total_entries_appended == self.average_entries, "The number of total entries in the appended list does not match the total_crypto_url_tag_entries"
        print(all_scraped_data_list)
        return all_scraped_data_list 

    
    def create_table_and_save_locally(self, concatenated_list, path):
        crypto_data_frame = pd.DataFrame.from_records(concatenated_list, columns=["source_url", "Rank", "Name", "Market Capitalisation", "Price", "Circulating Supply", "Ticker", "24 h change"])
        print(crypto_data_frame)
        crypto_data_frame.to_csv(path_or_buf=path)
        return crypto_data_frame

    
    def UUID_dictionary(self, record_list:list):
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
        self.record_uuid_dict = dict(zip(uuid_list, record_list))
        return self.record_uuid_dict

    
    def turn_dictionary_into_json_file(self, path, file_to_turn_into_json):
        '''This method converts a file to a JSON file and saves it to a specified path.
        
        syntax: turn_dictionary_into_json_file(path, dictionary_to_turn_into_json)

        Takes 2 arguments
        path argument = path for file to be written to and name of file
        file_to_turn_into_json argument = the file to be stored as a json file'''
        with open(path, 'w') as fp:
            json.dump(file_to_turn_into_json, fp)
    
    
    def crypto_data_UUID_list_dictionary(self, record_list:list, path):
        Dictionary = self.UUID_dictionary(record_list)
        self.turn_dictionary_into_json_file(path, self.record_uuid_dict)
        return Dictionary

    # def upload_files(self, 
    #                 my_path, 
    #                 bucket_name, 
    #                 S3_name=None):
    #     """Upload a file to an S3 bucket

    #     :param file_name: File to upload
    #     :param bucket: Bucket to upload to
    #     :param object_name: S3 object name. If not specified then file_name is used
    #     :return: True if file was uploaded, else False
    #     """
           
    #     uploaded_files = [f for f in listdir(my_path) if isfile(join(my_path, f))]   
    #     #print(uploaded_files)
    #     #     If S3 object_name was not specified, use my_path
    #     if S3_name is None:
    #         S3_name = os.path.basename(my_path)

    #     # Upload the files
    #     s3_client = boto3.client('s3')
    #     try:
    #         response = s3_client.upload_file(uploaded_files, bucket_name, S3_name)
    #     except ClientError as e:
    #         logging.error(e)
    #         return False
    #     return True

    def upload_file_to_s3(self, file_name, bucket, object_name=None):
        """Upload a file to an S3 bucket

        :param file_name: File to upload (directory)
        :param bucket: Bucket to upload to (bucket name)
        :param object_name: S3 object name, the name you want to give the file. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        # Upload the file
        s3_client = boto3.client('s3')
        try:
            response = s3_client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def upload_folder_to_S3(self, path, bucket):
        s3_client = boto3.client('s3')
        for root,dirs,files in os.walk(path):
            for file in files:
                s3_client.upload_file(os.path.join(root, file), bucket, file)


    def upload_table_from_csv_to_RDS(self):
        
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
        self.dataframe = pd.read_csv(r"C:\Users\marko\OneDrive\Desktop\Web_Scraping\New folder (2)\datatable.csv")
        print(self.dataframe.head())
        self.dataframe.to_sql('crypto_dataset', engine, if_exists='replace')

if __name__ =="__main__":
    

    yolo = CMCScraper()
    final_url = yolo.create_url_list_final('28-04-2013', '18-09-2022', 1, 'https://coinmarketcap.com/historical/')
    #get_images_one_day = yolo.get_image_src_list_from_webpage('https://coinmarketcap.com/historical/20130616/')
    #get_all_images = yolo.save_images_from_multiple_webpages(final_url, 50, r"C:\Users\marko\OneDrive\Desktop\image_data")
    crypto_data_list = yolo.get_crypto(final_url, 10)
    #yolo.create_table_and_save_locally(crypto_data_list, r"C:\Users\marko\OneDrive\DS Projects\Web_Scraping\Data\datatable.csv")
    #yolo.sql()
    #yolo.crypto_data_UUID_list_dictionary(crypto_data_list, r"C:\Users\marko\OneDrive\DS Projects\Web_Scraping\Data\dict.json")
    #dictionary_for_images = yolo.crypto_data_UUID_list_dictionary(, r"C:\Users\marko\OneDrive\DS Projects\Web_Scraping\Data\dict.json"
    #yolo.upload_files(r"C:\Users\marko\OneDrive\Desktop\Web_Scraping\New folder (2)", 's3://mofirstbucket1/CMC data upload 1/', 'CMCdata upload 1/')
    #yolo.upload_file(r"C:\Users\marko\OneDrive\Desktop\Web_Scraping\New folder (2)\1.png", 'cmc-bucket-mo')
    #upload_folder(r"C:\Users\marko\OneDrive\Desktop\Web_Scraping\New folder (2)", 'cmc-bucket-mo')