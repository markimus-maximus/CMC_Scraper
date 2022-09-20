import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


class Web_Scraper: 

    def __init__(self):
        self.driver = webdriver
        self.url = str
    
    def webdriver_init(self, url):
        ''' 
        Method for initialising webdriver and requesting url.

        Implementing this method saves repeating code in subsequent methods, and 
        streamlines declaring url variable to one method. By default this method will
        not allow push notifications and will maximise the screen.
        
        syntax: webdriver_init(url) 
        
        1 argument required
        url argument = url to be accessed by Selenium
          '''
        
        chrome_options = webdriver.ChromeOptions()#create object to implement options
        prefs = {"profile.default_content_setting_values.notifications" : 2} #preference to not allow push notifications
        chrome_options.add_experimental_option("prefs",prefs) #implements notifications preference
        self.driver = webdriver.Chrome(executable_path=r'C:\Users\marko\chromedriver.exe', chrome_options=chrome_options)
        self.driver.get(url)
        
    
    def cookies_bypass(self, XPath):
        '''
        Method for bypassing cookies by clicking accept cookies button.
        
        syntax: cookies_bypass(XPath)
        
        1 argument required
        XPath argument = XPath for clicking cookies bypass
        '''
        try: 
            accept_cookies_button = self.driver.find_element(by=By.XPATH, value= XPath)
            accept_cookies_button.click()
            print('Xpath clicked')

        except: pass

    def auto_login(self, email_address, password):
        '''   
        Method for logging into webpage using user inputted login and password credentials.
        
        syntax: auto_login(email_address, password)

        2 arguments required
        email_address argument = login email
        password argument = login password
       '''
        time.sleep(2)
        #click the login field 
        XPath_click_to_login = '//*[@id="__next"]/div/div[1]/div[1]/div[1]/div/div[1]/div/div[3]/button[1]'
        click_login = self.driver.find_element(by=By.XPATH, value= XPath_click_to_login)
        click_login.click()
        time.sleep(1)
        

        # input the username string
        XPath_email_field =  '/html/body/div[3]/div/div/div/div/div[2]/div[1]/input'
        username = self.driver.find_element(by=By.XPATH, value= XPath_email_field)
        username.send_keys(email_address)

        # # click continue to send username- this part is not needed for coinmarketcap
        # XPath_click_conitnue_login = '//*[@id="continue"]'
        # username_send_click = self.driver.find_element(by=By.XPATH, value= XPath_click_conitnue_login)
        # username_send_click.click()
        # time.sleep(2) # Delay to avoid looking like a bot to server

        #input the password string
        XPath_input_password = '/html/body/div[3]/div/div/div/div/div[2]/div[2]/div[2]/input'
        password_enter = self.driver.find_element(by=By.XPATH, value= XPath_input_password)
        password_enter.send_keys(password)

        #click continue to send password
        XPath_click_login = '/html/body/div[3]/div/div/div/div/div[2]/div[3]/button[1]' 
        password_send_click = self.driver.find_element(by=By.XPATH, value= XPath_click_login)
        password_send_click.click()

    def scroll_page(self, x, y):
        '''
        This method scrolls a webpage in the x, y orientations. using selenium. 
        
        Input the url, and the x,y coordinaytes for the location to scroll to. Simply 
        scrolling down would leave x as 0. A full HD monitor is 1080 in the y plane, so 
        to scroll to the bottom would be (0,1080)
        
        syntax: scroll_page(x, y)

        2 arguments required
        x argument = x coordinate to scroll to
        y argument = y coordinate to scroll to'''
        

        self.driver.execute_script(f"window.scrollTo({x},{y})")

        time.sleep(2) # Delay to avoid looking like a bot to server

    
    def maximise_window(self):
        '''
        Method to maximise the webdriver window
        
        syntax: maximise_window()
        
        0 arguments required
        '''
        self.driver.set_window_size(1024, 600)
        self.driver.maximize_window()

    
    def bypass_initial_popup(self):
        time.sleep(2) #hang on a sec for the banner to appear
        click_menu_button_Xpath = '/html/body/div[3]/div[2]/div[4]/button'
        menu_click = self.driver.find_element(by=By.XPATH, value= click_menu_button_Xpath)
        menu_click.click()
        #print('clicked')


if __name__ =="__main__":
    cmc_url = Web_Scraper()
    cmc_url.webdriver_init('https://coinmarketcap.com')
    cmc_url.maximise_window()
    cmc_url.bypass_initial_popup()
    cmc_url.auto_login('markowen90@hotmail.co.uk', 'Spoofpassword123!')


    123