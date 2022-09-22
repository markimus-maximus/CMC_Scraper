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


class CMCScraperTestCase(unittest.TestCase):
     

    @unittest.skip
    def test_create_url_list_final(self):
        #Initialise the class
        obj_scraper = CMCScraper()
        #define date variables of first day of records and today's date to test all range of dates 
        first_day_on_record = date(2013, 4, 28)
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
        #run the method  
        obj_scraper = CMCScraper()
        #Informs how the test_int value
        print(f'test_int is {test_int}')
        #Create date object tested above
        url_list = obj_scraper.create_url_list_final('28-04-2013', '21-09-2022', 1, 'https://coinmarketcap.com/historical/')
        #Create instance of image scraping public class
        get_images = obj_scraper.save_images_from_multiple_webpages(url_list, test_int, r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data")
        #Counts the number of files in the path
        count = 0
        for element in pathlib.Path(r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data").iterdir():
            if element.is_file():
                count += 1
        #checks that the number of files in the path is the same as the number of expected downloads
        self.assertEqual(obj_scraper.number_of_downloads, count)
        #can't convert a list straight to a set so first converting to a tuple (immutable/hashable data type)
        get_image_tuple = tuple(get_images)
        #convert from tuple to set
        get_image_set = set(get_image_tuple)
        #get length of the set (no duplicates in a set) 
        set_length = len(get_image_set)
        #if no rescraping has occurred, the set length and the original list length should be the same
        self.assertEqual(len(get_images), set_length)

    @given(st.integers(min_value=1, max_value=30))
    @settings(max_examples=2, deadline=None)
    @unittest.skip
    def test_data_scraper(self, test_int):
        #redefining the class instance to a local variable otherwise the variable is stored from the previous iteration
        obj_scraper = CMCScraper()
        #Creating instance to create url_list (doesn't work to store as instance variable of the class)
        url_list = obj_scraper.create_url_list_final('28-04-2013', str(date.today()), 1, 'https://coinmarketcap.com/historical/')
        #create an instance of the crypto data scraping method
        get_crypto = obj_scraper.get_crypto(url_list, test_int)
        #Informs the test_int for checking puproses
        print(f'test_int is {test_int}')
        #checks that the average number of entries in each category (for name and crypto ticker) are the same as the average of all categories
        self.assertEqual(obj_scraper.average_entries, obj_scraper.total_name_entries, obj_scraper.total_CT_entries)
        #checks that the resulting list of each  concatenated record (e.g. BTC of a particular date) matches the average number of entries for each category 
        self.assertEqual(obj_scraper.total_entries_appended, obj_scraper.average_entries)
        #can't convert a list straight to a set so first converting to a tuple (immutable/hashable data type). Need the tuple(tuple) approach as converting a list of lists
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
        # Create an instance of the class
        obj_scraper = CMCScraper()
        #create instance of url_list public method
        url_list = obj_scraper.create_url_list_final('28-04-2013', str(date.today()), test_int, 'https://coinmarketcap.com/historical/')
        #create an instance of crypto data scraper public method
        get_crypto = obj_scraper.get_crypto(url_list, 10)
        #Create an instance of dictionary generation method
        dictionary_generation_with_crypto_data = obj_scraper.crypto_data_UUID_list_dictionary(get_crypto, r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data\data_dict.json")
        #Get the dictionary length
        data_dictionary_length = len(dictionary_generation_with_crypto_data)
        #get the length of the returned scraped crypto data
        combined_crypto_list_length = len(get_crypto)
        #check that the length of the dictionary is equal to the length of the concatenated list
        self.assertEqual(data_dictionary_length, combined_crypto_list_length) 
        #checks that the json file exists and in target directory
        check_file_exists = pathlib.Path(r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data\data_dict.json").exists() 
        self.assertIs(check_file_exists, True)
        #Now do the same thing for the image dictionary
        get_images = obj_scraper.save_images_from_multiple_webpages(url_list, test_int, r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data")
        #create instance of the dictionary generator with the returned image list
        dictionary_generation_with_image_data = obj_scraper.crypto_data_UUID_list_dictionary(get_images, r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data\image_dict.json")
        #Get the dictionary length
        image_dictionary_length = len(dictionary_generation_with_image_data)
        #get the length of the returned scraped crypto data
        combined_image_list_length = len(get_images)
        #check that the length of the dictionary is equal to the length of the concatenated list
        self.assertEqual(image_dictionary_length, combined_image_list_length) 
        #checks that the json file exists and in target directory
        check_file_exists = pathlib.Path(r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data\image_dict.json").exists() 
        self.assertIs(check_file_exists, True)
    
    @given(st.integers(min_value=1, max_value=30))
    @settings(max_examples=4, deadline=None)
    #@unittest.skip
    def test_create_dataframe_and_save_locally(self, test_int):
        # Create an instance of the class
        obj_scraper = CMCScraper()
        #create instance of url_list public method
        url_list = obj_scraper.create_url_list_final('28-04-2013', str(date.today()), test_int, 'https://coinmarketcap.com/historical/')
        #create an instance of crypto data scraper public method
        get_crypto = obj_scraper.get_crypto(url_list, 10)
        #Create an instance of dataframe
        dataframe = obj_scraper.create_dataframe_and_save_locally(get_crypto, r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data\dataframe.csv" ) 
        
        original_list_length = len(get_crypto)
        data_frame_length = dataframe.shape[0]
        
        self.assertEqual(original_list_length, data_frame_length) 

    @patch('CMC_Scraper.CMC_Scraper.method')
    @patch('CMC_Scraper.CMC_Scraper.method')
    @patch('CMC_Scraper.CMC_Scraper.method')
    def test_login(self,
                   Mock_webdriver_init: Mock, 
                   Mock_maximise_window: Mock,
                   Mock_auto_login: Mock):

    def tearDown(self):
        files = glob.glob(r"C:\Users\marko\DS Projects\CMC_Scraper\Test\Test_data\*")
        for file in files:
            os.remove(file)
         

if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=3, exit=False)
        


    