import sys
sys.path.append(r"C:\Users\marko\OneDrive\Desktop\CMC_Scraper_1\CMC_Scraper")#defines the path to the modules which contain the classes
from Web_Scraper import Web_Scraper
import unittest
import unittest
from unittest.mock import patch, Mock
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

class ScraperTestCase(unittest.TestCase):
    
    @classmethod
    def setUp(self):

        self.Scraper = Web_Scraper()
        
    #unittest.skip  
    def test_webdriver_init(self):
        self.Scraper.webdriver_init('https://coinmarketcap.com/')

        actual_url = self.Scraper.driver.current_url
        
        expected_url = 'https://coinmarketcap.com/'
       
        print(actual_url)

        self.assertEqual(actual_url, expected_url)

        self.Scraper.driver.quit
        
    
    #unittest.skip
    def test_cookies_bypass(self):
        scraper = Web_Scraper()
        
        scraper.webdriver_init('https://www.amazon.co.uk') # needs to be https:// version to work

        time.sleep(2)
        
        scraper.cookies_bypass('//*[@id="sp-cc-accept"]')

        time.sleep(2)

        XPath_click_to_login = '/html/body/div[1]/header/div/div[1]/div[3]/div/a[2]'
        click_login = scraper.driver.find_element(by=By.XPATH, value= XPath_click_to_login)
        click_login.click()

        time.sleep(2)

        actual_url = str(scraper.driver.current_url)

        print(actual_url)
        
        expected_url = 'https://www.amazon.co.uk/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.co.uk%2F%3Fref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=gbflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&'

        self.assertEqual(actual_url, expected_url), "the actual url is not the same as expected url, cookies not bypassed"

    @patch('Web_Scraper.Web_Scraper.webdriver_init')
    @patch('Web_Scraper.Web_Scraper.maximise_window')
    @patch('Web_Scraper.Web_Scraper.auto_login')
    def test_login(self,
                   Mock_webdriver_init: Mock, 
                   Mock_maximise_window: Mock,
                   Mock_auto_login: Mock):
        scraper = Web_Scraper()
        scraper.webdriver_init('https://coinmarketcap.com/')
        scraper.maximise_window()
        scraper.auto_login('markowen90@hotmail.co.uk', 'Spoofaccount123!')
        actual_url = scraper.driver.current_url
        
        expected_url = 'https://coinmarketcap.com/'
       
        print(actual_url)

        self.assertEqual(actual_url, expected_url)
        assert Mock_webdriver_init.called_once
        assert Mock_maximise_window.called_once
        assert Mock_auto_login.called_once

    @classmethod
    def tearDown(self):
        # self.Scraper.driver.quit()
        del self.Scraper 

if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=3, exit=False)
