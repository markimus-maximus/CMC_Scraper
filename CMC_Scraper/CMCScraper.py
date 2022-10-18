from bs4 import BeautifulSoup
from DataHandler import DataHandler
from pathlib import Path
from sqlalchemy import create_engine
import json
import logging
import os
import pandas as pd
import re
import requests
from selenium.webdriver.common.by import By
import sys
import time
import urllib.request

class CMCScraper(DataHandler):
    ''' Class for scraping data from Coin Market Cap, although much of this code could be easily adapted for other scraping applications.
    
    This class can generate a list of dates between 2 given dates and formats the list in order to  use them as permalinks, 
    carried out by the method 'daterange'. The second method 'create_url_list_with_date_permalinks' iteratively concatenates the 
    permalinks to a root url. The result of this is a list of urls which can be used to iterate through.
    Additionally, this class can scrape and save all crypto price records as well as images from a specified number of webpages, 
    as defined by the generated url list above'''

    
    
    def __init__(self):
        #Define logging parameters: currently configured to display info and above on the console
        logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    handlers=[
                    logging.FileHandler("CMCScraper_log.log"),
                    logging.StreamHandler(sys.stdout)])
        logging.info('Scraper instance started')
        
        self.crypto_url_tag_list = []
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
        self.total_name_entries = 0
        self.total_CS_entries = 0 
        self.total_MK_entries = 0 
        self.total_crypto_price_entries = 0 
        self.total_CT_entries = 0
        self.total_crypto_url_tag_entries = 0
        self.total_rank_entries = 0
        self.url_tag = str
        self.image_name_list = []
        self.user_friendly_tag_list = []
        self.image_list = []
        self.image_data_combined_list = []

    def __get_image_data_from_webpage ( self, 
                                        url:str):
        '''This method generates a list of URLS corresponding to data from a webpage and retrieves only .png
        files. These .png urls will be returned in a list. This will only get the first 10 images since the 
        rest of the images are dynamically accessed.
        
        syntax: get_image_src_list_from_webpage(url)
        
        Takes 1 argument (likely inherited from url_list in child method)
        url argument = the webpage url to scrape and retrieve the images
        '''
        logging.info('__get_image_src_list_from_webpage method called')
        #create BS object
        soup = self.__get_soup(url)
        logging.info(f'Page scraped: {url}')
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
            #pairs the name and image src scraped from the same row to generate a "user-friendly" name tag
            crypto_name_and_image_single = [crypto_name, image, url]
            if crypto_name_and_image_single not in self.image_data_combined_list:
                self.image_data_combined_list.append(crypto_name_and_image_single)
            #prevent_rescrape of image_list elements
            if image not in self.image_list:
                self.image_list.append(image)
        return self.image_list
        
        
    def __retrieve_images_from_webpage  (self, 
                                    path:str,
                                    image_list:list):
        '''This method retrieves and saves the images generated in method 'get_image_src_list_from_webpage' to an indicated
        path. Each image is named according to the unique number given on coinmarket cap
        
        syntax: save_images_from_webpage(path)
        
        Takes 1 argument
        path argument = the path to save the file once retrieved (the file name is modified for every unique image). 
        '''
        logging.info('__save_images_from_webpage method called')
        path=str(path)
        len_path = len(path)
        #loop to iterate through the image list, using enumerate method to rename the file after every iteration
        for image in image_list:
            #extracting numerical data from image name string 
            image_sliced = re.findall('[0-9]+', image)
            #Slicing out the last number to get unique number of image
            image_sliced = image_sliced[3]
            #renaming the file
            path = f'{path[:len_path]}\{image_sliced}.png' 
            #code to prevent redownloading of duplicates from previous iterations of the enumeration loop
            if os.path.exists(path):
                pass
            else:
                #retrieve the image and save with path
                urllib.request.urlretrieve(image, path)

    def save_images_from_multiple_webpages( self, 
                                            url_list:list, 
                                            num_pages:int, 
                                            image_path:str,
                                            ):
        '''Method which incorporates previous methods to scrape multiple webpages, retrieve the images and save images locally.
        
        syntax: save_images_from_multiple_webpages(url_list, num_pages, path)
       
        Takes 3 arguments
        url_list argument = the list of urls to iterate through when scraping
        num_pages argument= The number of pages which are iterated through 
        path argument= The folder path for saving the first document once retrieved (the file name is modified for every unique image). 
        '''
        #Looping through the method which scrapes the images src and name for given number of pages
        for url in url_list[:num_pages]:
            image_list = self.__get_image_data_from_webpage(url)
        #After all .png is scraped, the images are downloaded and saved in folder with path 
            self.__retrieve_images_from_webpage(image_path, image_list)
        dataframe = DataHandler.create_dataframe(self.image_data_combined_list, 'name', 'image', 'source_url')
        print(dataframe)
        return dataframe

    def get_more_image_data(self, local_folder_path:str, bucket_name:str, s3_csv_file_name:str, s3):
       # create csv object obtained from s3
        csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_csv_file_name)
       # turn csv object into df
        df_of_s3 = pd.read_csv(csv_obj['Body'])
        #print contents of df
        print(f'all_s3: {df_of_s3}')
        #Calculate webpages which need to be scraped
        outstanding_webpages = self.get_outstanding_webpages(df_of_s3)
        print(f'oustanding webpages to scrape: {outstanding_webpages}')
        #create dataframe of all the newly-scraped data
        new_data_dataframe = self.save_images_from_multiple_webpages(outstanding_webpages, len(outstanding_webpages), r"C:\Users\marko\DS Projects\Data\Crypto_images")
        #use this method to update the dataframe
        DataHandler.save_dataframe_locally(new_data_dataframe, r"C:\Users\marko\DS Projects\Data\Crypto_images\crypto_images.csv", header_choice=False)
        #upload updated .csv file to s3
        DataHandler.rewrite_s3_file(r"C:\Users\marko\DS Projects\Data\Crypto_images\crypto_images.csv", bucket_name, s3)
        #re-upload any freshly scraped image data
        DataHandler.upload_folder_to_S3(local_folder_path, 'cmc-bucket-mo', s3)
    
        
    def __scrape_items_from_row(self):   
        ''' This function scrapes the data from one of the cryptocurrency rows generated in the function 'get_crypto_rows'. 
        
        In this function, the crypto name, price, ticker, market cap and circulating supply are stored in individual lists. Each value, 
        for example price, is stored in a list of each of the cryptocurrencies from that day. For example, all of the names of cryptocurrencies
        scraped from a particular webpage (corresponding to a particular date) would be contained in the list crypto_name_list. 

        syntax: scrape_item_from_row()
        
        Requires 0 arguments 
        '''
        logging.info('__scrape_items_from_row method called')
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
        ('__get_soup method called')
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
        logging.info('__get_crypto_rows method called')
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
            logging.info(f'Page scraped: {self.url_tag}')
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
        '''This method creates a list of user-friendly record tags which are unique to each record. This is achieved by combining the source url with the crypto name
        
        syntax __generate_user_friendly_tag()
        
        Takes 0 arguments'''

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
        logging.info('__scrape_items_from_row method called')
        #iterates for the number of elements in url_tag_list
        for i in range(len(self.crypto_url_tag_list)):
            self.daily_records_combined_list.append([self.user_friendly_tag_list[i], self.crypto_url_tag_list[i], self.crypto_rank_list[i], self.crypto_name_list[i],self.crypto_market_cap_list[i],self.crypto_price_list[i],self.crypto_circulating_supply_list[i],self.crypto_ticker_list[i], self.crypto_price_change_list[i]]) 
        self.total_entries_appended = len(self.daily_records_combined_list)
        return self.daily_records_combined_list  
    
    def get_crypto( self, 
                    url_list:list, 
                    num_pages:int):
        '''This method combines private methods in order to scrape daily data from coin market cap. This method returns the following data as a list of lists:
        User friendly ID, source url, crypto rank, name, daily market capitalisation ($), daily price ($), daily circulating supply ($), crypto ticker, 24 h price change (%)
        
        syntax: get_crypto(url_list:list, num_pages=None)

        Takes 1 argument and one optional argument
        url_list = the list of urls to iteratively scrape
        num_pages = the number of pages starting from the beginning of url_list to scrape. If = None, the entire url_list will be used
        '''
        if num_pages==None:
            num_pages=len(url_list)
        
        self.__get_crypto_rows(url_list, num_pages)
        self.__generate_user_friendly_tag()
        all_scraped_data_list = self.__daily_record_concatenater()
        assert self.total_entries_appended == self.average_entries, "The number of total entries in the appended list does not match the total_crypto_url_tag_entries"
        return all_scraped_data_list 
   
    def get_outstanding_webpages(self, dataframe):
        #creates a dataframe of all available urls from first date to present day
        all_available_entries = self.get_all_available_webpages()
        #comares both dataframes for differences and returns a list of urls yet to be scraped
        comparison = DataHandler.compare_dataframes(all_available_entries, 'source_url', dataframe, 'source_url')
        print(f'Webpages left to be scraped: {comparison}')
        return comparison
    
    def upload_tabular_data_to_pre_existing_RDS(self, 
                                        RDS_table_name:str, 
                                        engine):
        '''This method compares data on an RDS table to all available entries, and in doing ensures that only records which are outstanding are
        scraped and appended to the database. 

        syntax: upload_data_to_pre_existing_RDS(RDS_table_name:str)

        Takes 2 arguments
        RDS_table_name = the RDS table to compare to and append only required entries 
        engine = engine for RDS connection
        
        '''
        
        
        return df_of_fresh_data
        
    def get_more_tabular_data(self, RDS_table_name:str, bucket_name:str, engine, s3):
        logging.info('getting df of tabular')                                
        df_of_fresh_data = self.upload_tabular_data_to_pre_existing_RDS(RDS_table_name, engine)
        #update .csv of tabular data locally 
        DataHandler.save_dataframe_locally(df_of_fresh_data, r"C:\Users\marko\DS Projects\Data\crypto_tabular_data.csv")
        #make uuid dict of exixting data
        list_of_df= df_of_fresh_data.values.tolist()
        dictionary_of_new_data = DataHandler.crypto_data_UUID_list_dictionary(list_of_df)
        #update dictionary JSON locally
        DataHandler.update_JSON_dictionary(dictionary_of_new_data, r"C:\Users\marko\DS Projects\Data\crypto_tabular_data.json")
        #upload fresh files replacing the others
        DataHandler.rewrite_s3_file(r"C:\Users\marko\DS Projects\Data\crypto_tabular_data.csv", s3)
        DataHandler.rewrite_s3_file(r"C:\Users\marko\DS Projects\Data\crypto_tabular_data.json", s3)

if __name__ =="__main__":
     CMCScraper_inst = CMCScraper()
     with open('credentials.json') as cred:
            credentials = json.load(cred)
            DATABASE_TYPE = credentials['DATABASE_TYPE']
            DBAPI = credentials['DBAPI']
            USER = credentials['USER']
            PASSWORD = credentials['PASSWORD']
            ENDPOINT = credentials['ENDPOINT']
            PORT = credentials['PORT']
            DATABASE = credentials['DATABASE']
            AWS_ACCESS_KEY_ID= credentials['AWS_ACCESS_KEY_ID']
            AWS_SECRET_ACCESS_KEY= credentials['AWS_SECRET_ACCESS_KEY'] 


     print('CMCScraper called')
     engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
     s3_client = CMCScraper_inst.create_s3_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
     CMCScraper_inst.get_more_image_data(Path("/Data/Crypto_images", 'cmc-bucket-mo', 'crypto_images.csv'))
     #CMCScraper_inst.get_more_tabular_data('crypto_tabular_data', 'cmc-bucket-mo', engine)
    #print(sys.path)
    

    
