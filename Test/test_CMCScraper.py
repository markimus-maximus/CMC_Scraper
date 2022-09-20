import sys
sys.path.append(r"C:\Users\marko\OneDrive\Desktop\CMC_Scraper_1\CMC_Scraper")#defines the path to the modules which contain the classes
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


class CMCScraperTestCase(unittest.TestCase):
     
    def setUp(self):
       self.obj_scraper = CMCScraper()
       

    unittest.skip
    def test_create_url_list_final(self):
        #define date variables of first day of records and today's date to test all range of dates 
        first_day_on_record = date(2013, 4, 28)
        today = date.today()
        #get difference between the 2 dates
        self.delta_daterange = (today - first_day_on_record).days
        #turn into strings to allow imput to the method
        first_day_on_record = str(first_day_on_record)
        today = str(today)
        #run the daterange method
        self.daterange = list(self.obj_scraper.daterange(first_day_on_record, today, 1))
        #run the final method create_url_list_final
        
        CMCScraperTestCase.url_list_with_date_permalinks = self.obj_scraper.create_url_list_final(first_day_on_record, today, 1, 'https://coinmarketcap.com/historical/')
        #get len daterange
        self.daterange_len = len(self.daterange)
        #assert delta_daterange -1 because delta calculates the difference between not every distinct day
        self.assertEqual(self.delta_daterange, self.daterange_len-1)
        #get len of final url list
        self.url_list_len = len(CMCScraperTestCase.url_list_with_date_permalinks)
        #assert both lists are the same length
        self.assertEqual(self.daterange_len, self.url_list_len)
        #Check that the permalink is contained within the same index of the concatenated url
        for i in range(len(self.daterange)):
            loop = self.daterange[i] in CMCScraperTestCase.url_list_with_date_permalinks[i]
            #assert that the correct permalink is contained within the url for every index
            self.assertIs(loop, True)
        
        return CMCScraperTestCase.url_list_with_date_permalinks
    
    @given(st.integers(min_value=1, max_value=50))
    @settings(max_examples=5, deadline=None)
    @unittest.skip
    def test_image_scraper(self, test_int):
        #run the method  
        self.obj_scraper.save_images_from_multiple_webpages(CMCScraperTestCase.url_list_with_date_permalinks, test_int, r"C:\Users\marko\OneDrive\Desktop\Web_Scraping\New folder (2)")
        
        #Counts the number of files in the path
        count = 0
        for element in pathlib.Path(r'C:\Users\marko\OneDrive\Desktop\Web_Scraping\New folder (2)').iterdir():
            if element.is_file():
                count += 1
        #checks that the number of files in the path is the same as the number of expected downloads
        self.assertEqual(self.obj_scraper.number_of_downloads, count)

    @given(st.integers(min_value=1, max_value=1000))
    @settings(max_examples=5, deadline=None)
    @unittest.skip
    def test_data_scraper(self, test_int):
        #redefining the class instance to a local variable otherwise the variable is stored from the previous iteration
        obj_scraper = CMCScraper()
        get_crypto = obj_scraper.get_crypto(CMCScraperTestCase.url_list_with_date_permalinks, test_int)
        print(f'test_int is {test_int}')
        #checks that the average number of entries in each category (for name and crypto ticker) are the same as the average of all categories
        self.assertEqual(obj_scraper.average_entries, obj_scraper.total_name_entries, obj_scraper.total_CT_entries)
        #checks that the resulting list of each  concatenated record (e.g. BTC of a particular date) matches the average number of entries for each category 
        self.assertEqual(obj_scraper.total_entries_appended, obj_scraper.average_entries)

    def test_dictionary_create_and_save(self):
        obj_scraper = CMCScraper()
        get_crypto = obj_scraper.get_crypto(CMCScraperTestCase.url_list_with_date_permalinks, 10)
        dictionary_generation = obj_scraper.crypto_data_UUID_list_dictionary(get_crypto, r"C:\Users\marko\OneDrive\Desktop\Web_Scraping\New folder (2)\dict.json")
        dictionary_length = len(dictionary_generation)
        combined_date_list_length = len(get_crypto)
        #check that the length of the dictionary is equal to the length of the concatenated list
        self.assertEqual(dictionary_length, combined_date_list_length) 
        #checks that the json file exists and in target directory
        check_file_exists = pathlib.Path(r"C:\Users\marko\OneDrive\Desktop\Web_Scraping\New folder (2)\dict.json").exists() 
        self.assertIs(check_file_exists, True)



    def tearDown(self):
        del self.obj_scraper

if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=3, exit=False)
        


    