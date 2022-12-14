import sys
import os
sys.path.append(r"C:\Users\marko\DS Projects\CMC_Scraper\CMC_Scraper")#defines the path to the modules which contain the classes
import unittest
from unittest.mock import patch, Mock
from CMCScraper import CMCScraper
from datetime import date, timedelta
import pathlib
from hypothesis import given, example, settings, strategies as st
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import glob
import boto3


class CMCScraperTestCase(unittest.TestCase):
     

    @unittest.skip
    def test_create_url_list_final(self):
        '''This method tests the coin market cap url generator by taking today's date and the first day on record and comparing to the actual number of days.
        Additionally this test checks that the concatenation of permalink to date was correct accross the whole range of urls'''
        #Initialise the class
        obj_scraper = CMCScraper()
        #define date variables of first day of records and today's date to test all range of dates 
        first_day_on_record = date(2013, 4, 29)
        today = date.today()
        #get difference between the 2 dates
        delta_daterange = (today - first_day_on_record).days
        #turn into strings to allow input to the method
        first_day_on_record = str(first_day_on_record)
        today = str(today)
        #run the daterange method
        daterange = list(obj_scraper.daterange(first_day_on_record, today, 1))
        #run the final method create_url_list_final
        
        url_list_with_date_permalinks = obj_scraper.create_url_list_final(first_day_on_record, today, 1, 'https://coinmarketcap.com/historical/')
        #get len daterange
        daterange_len = len(daterange)
        #assert delta_daterange -1 because delta calculates the difference between not every distinct day
        self.assertEqual(delta_daterange, daterange_len-1)
        #get len of final url list
        self.url_list_len = len(url_list_with_date_permalinks)
        #assert both lists are the same length
        self.assertEqual(daterange_len, self.url_list_len)
        #Check that the permalink is contained within the same index of the concatenated url
        for i in range(len(daterange)):
            loop = daterange[i] in url_list_with_date_permalinks[i]
            #assert that the correct permalink is contained within the url for every index
            self.assertIs(loop, True)
        
       
    
    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=2, deadline=None)
    @unittest.skip
    def test_image_scraper(self, test_int):
        '''Tests the image scraper across a number of instances and varied webpages within each instance. The test makes sure that the correct number
        of images were downloaded and converts the list to a set to ensure that there were no rescrapes of data. There is a known minimum 7 images from 
        1 page so this is used as a benchmark to ensure that images have been downloaded.'''
        #run the method  
        obj_scraper = CMCScraper()
        #Informs how the test_int value
        print(f'test_int is {test_int}')
        #Create date object tested above
        url_list = obj_scraper.create_url_list_final('04-29-2013', '09-21-2022', 1, 'https://coinmarketcap.com/historical/')
        #Create instance of image scraping public class
        obj_scraper.save_images_from_multiple_webpages(url_list, test_int, r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data")
        #Counts the number of files in the path
        image_download_count = 0
        for element in pathlib.Path(r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data").iterdir():
            if element.is_file():
                image_download_count += 1
        list_of_files_in_directory = os.listdir(r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data")
        #can't convert a list straight to a set so first converting to a tuple (immutable/hashable data type)
        get_image_tuple = tuple(list_of_files_in_directory)
        #convert from tuple to set
        get_image_set = set(get_image_tuple)
        #get length of the set (no duplicates in a set) 
        set_length = len(get_image_set)
        #if no rescraping has occurred, the set length and the original list length should be the same
        self.assertEqual(image_download_count, set_length)
        #There should always be at least 7 downloads
        self.assertGreater(image_download_count, 6)

    @given(st.integers(min_value=1, max_value=30))
    @settings(max_examples=5, deadline=None)
    @unittest.skip
    def test_data_scraper(self, test_int):
        '''Tests the crytpo data scraper across a number of instances and varied webpages within each instance. This method ensures that the number of 
        page scrapes is the same as the average number of all data downloads, if this number is different then there was likely incomplete scraping. 
        Conversely, the list of lists containing all scraped data is converted to a set to ensure no rescraping of a record has occured. '''
        #redefining the class instance to a local variable otherwise the variable is stored from the previous iteration
        obj_scraper = CMCScraper()
        #Creating instance to create url_list (doesn't work to store as instance variable of the class)
        url_list = obj_scraper.create_url_list_final('04-29-2013', str(date.today()), 1, 'https://coinmarketcap.com/historical/')
        #create an instance of the crypto data scraping method
        get_crypto = obj_scraper.get_crypto(url_list, test_int)
        #Informs the test_int for checking puproses
        print(f'test_int is {test_int}')
        #checks that the average number of entries in each category (for name and crypto ticker) are the same as the average of all categories
        self.assertEqual(obj_scraper.average_entries, obj_scraper.total_name_entries, obj_scraper.total_CT_entries)
        #checks that the resulting list of each  concatenated record (e.g. BTC of a particular date) matches the average number of entries for each category 
        self.assertEqual(obj_scraper.total_entries_appended, obj_scraper.average_entries)
        #can't convert a list straight to a set so first converting to a tuple (tuple is immutable/hashable data type). Need the tuple(tuple) approach as converting a list of lists
        get_crypto_tuple = tuple(tuple(sub) for sub in get_crypto)
        #Convert tuple to a set 
        get_crypto_set = set(get_crypto_tuple)
        #get the length of the set
        set_length = len(get_crypto_set)
        #if no rescraping has occurred, the set length and the original list length should be the same
        self.assertEqual(len(get_crypto), set_length)
    
    @given(st.integers(min_value=1, max_value=30))
    @settings(max_examples=4, deadline=None)
    @unittest.skip
    def test_dictionary_create_and_save(self, test_int):
        '''Test methods which first generate a dictionary and then store it locally. The test checks that the dictionary is the appropriate length  and
        that the file exists locally. This test is implemented for both image and tabular data.'''
        # Create an instance of the class
        obj_scraper = CMCScraper()
        #create instance of url_list public method
        url_list = obj_scraper.create_url_list_final('28-04-2013', str(date.today()), 30, 'https://coinmarketcap.com/historical/')
        #create an instance of crypto data scraper public method
        get_crypto = obj_scraper.get_crypto(url_list, test_int)
        #Create a UUID list
        UUID_list = obj_scraper.create_UUID_list(len(get_crypto))
        #ceate UUID dictionary
        UUID_dictionary = obj_scraper.create_dict_from_2_lists(UUID_list, get_crypto)
        #save the dictionary loaclly 
        save_data_locally = obj_scraper.turn_data_into_file(r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data\data_dict.json", UUID_dictionary)
        #Get the dictionary length
        data_dictionary_length = len(UUID_dictionary)
        #get the length of the returned scraped crypto data
        combined_crypto_list_length = len(get_crypto)
        #check that the length of the dictionary is equal to the length of the concatenated list
        self.assertEqual(data_dictionary_length, combined_crypto_list_length) 
        #checks that the json file exists and in target directory
        check_file_exists = pathlib.Path(r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data\data_dict.json").exists() 
        self.assertIs(check_file_exists, True)
        #Now do the same thing for the image dictionary
        get_images = obj_scraper.save_images_from_multiple_webpages(url_list, test_int, r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data")
        #Create a UUID list
        UUID_list_2 = obj_scraper.create_UUID_list(len(get_images))
        #ceate UUID dictionary
        UUID_dictionary_2 = obj_scraper.create_dict_from_2_lists(UUID_list_2, get_images)
        #save the dictionary loaclly 
        save_data_locally_2 = obj_scraper.turn_data_into_file(r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data\image_dict.json", UUID_dictionary_2)
        #Get the dictionary length
        image_dictionary_length = len(UUID_dictionary_2)
        #get the length of the returned scraped crypto data
        combined_image_list_length = len(get_images)
        #check that the length of the dictionary is equal to the length of the concatenated list
        self.assertEqual(image_dictionary_length, combined_image_list_length) 
        #checks that the json file exists and in target directory
        check_file_exists = pathlib.Path(r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data\image_dict.json").exists() 
        self.assertIs(check_file_exists, True)
    
    @given(st.integers(min_value=1, max_value=30))
    @settings(max_examples=4, deadline=None)
    @unittest.skip
    def test_create_dataframe_and_save_locally(self, test_int):
        '''Test methods which first generate dataframes and then stores the methods locally. The test checks that the dataframe is the appropriate length
        and width and that the file exists locally. This test is implemented for both image and tabular data.'''
        # Create an instance of the class
        obj_scraper = CMCScraper()
        #create instance of url_list public method
        url_list = obj_scraper.create_url_list_final('04-28-2013', str(date.today()), test_int, 'https://coinmarketcap.com/historical/')
        #create an instance of crypto data scraper public method
        get_crypto = obj_scraper.get_crypto(url_list, 10)
        #Create dataframe
        dataframe = obj_scraper.create_dataframe(get_crypto, "ID", "source_url", "Rank", "Name", "Market Capitalisation", "Price", "Circulating Supply", "Ticker", "24 h change") 
        #Save dataframe locally
        obj_scraper.save_dataframe_locally(dataframe, r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data\test.csv")
        #get the length of the list which was converted to df
        original_list_length = len(get_crypto)
        #Get the number of columns in the dataframe (conversely [1] would be number of rows)
        data_frame_length = dataframe.shape[0]
        #check that the df length and orignal list are the same 
        self.assertEqual(original_list_length, data_frame_length) 
        #check that the number of columns is equal to 9
        data_frame_width = dataframe.shape[1]
        self.assertEqual(9, data_frame_width) 
        #check that the file exists
        check_file_exists = pathlib.Path(r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data\test.csv").exists() 
        self.assertIs(check_file_exists, True)

    @patch('CMCScraper.CMCScraper.upload_file_to_s3')
    @patch('CMCScraper.CMCScraper.upload_folder_to_S3')
    @patch('CMCScraper.CMCScraper.upload_table_from_csv_to_RDS')
    #@unittest.skip
    def test_interaction_with_S3_bucket(self,
                                        Mock_upload_file_to_s3: Mock, 
                                        Mock_upload_folder_to_S3: Mock,
                                        Mock_upload_table_from_csv_to_RDS: Mock):
        '''Tests that files are uploaded to S3 bucket correctly and in the right numbers. Also checks that this method and other methods which interact with 
        the cloud are called once. '''
        #Check methods called once
        assert Mock_upload_file_to_s3.called_once
        assert Mock_upload_folder_to_S3.called_once
        assert Mock_upload_table_from_csv_to_RDS.called_once
        #Connect to the host
        s3_client = boto3.client('s3')
        #Counts the number of files in the path
        source_directory_count = 0
        for element in pathlib.Path(r"C:\Users\marko\DS Projects\Data\Crypto_images").iterdir():
            if element.is_file():
                source_directory_count += 1
        #counts the number of files in the S3 bucket
        S3_bucket_count = 0
        for root,dirs,files in os.walk(r"C:\Users\marko\DS Projects\Data\Crypto_images"):
            for file in files:
                file =str(file)
                already_uploaded = s3_client.list_objects_v2(Bucket='cmc-bucket-mo', Prefix=file)
                if 'Contents' in already_uploaded:
                    S3_bucket_count += 1
        #If the number of files in the S3 bucket is different to the local directory, then there was an error uploading 
        self.assertEqual(source_directory_count, S3_bucket_count)

    def tearDown(self):
        files = glob.glob(r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data\*")
        for file in files:
            os.remove(file)
   
         

if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=3, exit=False)
        


    