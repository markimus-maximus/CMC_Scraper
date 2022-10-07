
# Data Collection Pipeline Project- Coin Market Cap 

My third project for AiCore. Webscraping coinmarketcap.com for cryptocurrency data.

## Milestone 1: Deciding the website to scrape
-	The aim of this project is to collect data crypto currency data and using this data to characterise factors which may impact cryptocurrency market standing.
-	Coinmarketcap.com was selected for the following reasons:
    *	Consistent url naming including date-based permalinks means that the url for a particular date could be generated easily in a list format. This ability to predetermine urls negates the need for using webdrivers to click next pages etc., while also allowing scraping of data of pre-defined intervals e.g. monthly. 
    *	Rich historical data dating back to April 2013 providing greater potential for insights. 
    * Consistent structure of historical data allows for consistent scraping of data between urls.
    * Relatively simple website without need for login or cookies bypass.
-	In combination with pre-determined urls the Requests package will be imported to access webpages.
-	Git branches were generated locally before being pushed to github.
- Assetions were used to monitor scraper progress and return errors if the scraper's behaviour was not as expected.
-	Logging was implemented to record events and store these events in a log file. Additionally, the events are printed to the console to track the status of the scraper as it runs. Usage of logging as opposed to print statements makes post-hoc tracking much easier and keeps a record for later reference.  Below are the logger configuration settings. Using StreamHandler in conjunction with sys facilitated printing to the console in addition to recording in a log.

~~~~
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    handlers=[
                    logging.FileHandler("CMCScraper_log.log"),
                    logging.StreamHandler(sys.stdout)])
~~~~

- A `requirements.txt` file was generated with pip freeze.

![image](https://user-images.githubusercontent.com/107410852/194552910-cf77a3e6-363c-4bb3-ab2f-c6aacf732a02.png)

A historical data webpage example.

## Scraper code structure

The code for the scraper has been split into 3 components. The CMCScraper class contains scraping methods which, although could be adapted, are designed for coinmarketcap specifically. DataHandler class contains methods which are inherited by CMCScraper but are broadly applicable to different applications (e.g. create dictionary from 2 lists, create data frame from list, save files locally, upload files/folders to differenet cloud-based services, compare dataframes, etc.). Web_Scraper is a class containing a collection of methods which are not necessary for scraping coinmarketcap.com but would likely be helpful for other websites (e.g. bypass cookies, log in, scroll page, etc.)

## Milestone 2: Generating a list of unique URLs for each webpage

- Given that coinmarketcap URLs are structured such that the permalink contains a date, this allowed for generation of unique URLs based on the date. To achieve this, the `daterange(start_date:str, end_date:str, frequency:int=None` method was built which used the pandas library to generate a date range between 2 dates given to by the user. The strftime method was implemented to reformat the date to be used as a permalink. Additionally, slicing the daterange provides the user the optional opportunity to choose a frequency of dates (default frequency is daily)
- After generation of the desired daterange, the `__create_url_list_with_date_permalinks(root_url:str, date_list:list)` private method concatenates the dates (formatted as cmc permalinks) to a root URL using the private in order to generate a list of unique URLs which would be compatible with coinmarket cap.
- The `create_url_list_final(start_date:str, end_date:str, frequency:int, root_url:str` public method combines the two methods above to generate the list of URLs with which to use with the scraper.

## Milestone 3: Retrieving data from each webpage

- There are different elements to scraping the cryptocurrency data:  
1. Navigating to the webpage and extracting HTML.  
The `__get_soup(url:str)` method uses `requests` and `url` from a list of URLS (Milestone 2) to access the webpage. A beutiful soup object is then generated to extract all of the HTML.
2. Extracting data from a row.  
Rows include data from one cryptocurrency. For example all of the data associated with bitcoin on one day is contained within a row. The method `__get_crypto_rows(url_list:list, num_page:int)` uses `soup.find_all('tr', attrs={'class':'cmc-table-row'})` to extract all rows. In addition, the `__get_crypto_rows` method generates a list of the URLS accessed.
3. Extracting individual data from each row.  
Individual data from one row includes `Rank, Name, Market Capitalisation, Price, Circulating Supply, Ticker, 24 h change`. These data are extracted using the `__scrape_items_from_row()` method. These data were extracted using the `td` tag, for example: `(row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sticky cmc-table__cell--sortable cmc-table__cell--left cmc-table__cell--sort-by__rank'}).text.strip())` where `.strip` extracts only the text. The extracted text was typed appropriately, e.g. `str` for names and `float` for price. To clean the data, `re.sub("[^\d\.]", "", <variable>)` was used on float data to remove any non-numerical data. This method then appends the data to a instance list variable. A user-friendly tag can be generated using the `__generate_user_friendly_tag()` method, which generates a unique ID by combining the name for a particular record with the source url.
4. Concatenating into a list of lists.  
After all of the data across the desired number of webpages has been scraped, the result is a series of category lists with concatenated data e.g. name list. In order to match each record from a given list with its corresponding data (e.g. cryptocurrency name with price of the same day), the `__daily_record_concatenater()`' method combines each record category based on the index to create a list of all records e.g. `['Bitcoin https://coinmarketcap.com/historical/20130509/', 'https://coinmarketcap.com/historical/20130509/', 1, 'Bitcoin', 1254535361.61, 112.67, 11134600.0, 'BTC', 0.1]` which corresponds to `["ID", "source_url", "Rank", "Name", "Market Capitalisation", "Price", "Circulating Supply", "Ticker", "24 h change"]` for one record. This concatenation is carried out for every index in each of the lists to return a list of lists.
5. Bringing the private methods together.  
The `get_crypto(url_list:list, num_pages=None)` method uses all of the crypto scraping and processing methods discussed above together under one method. The arguments which can be passed to this method include the url list (Milestone 2) and an optional argument which is the number of pages to scrape from the list (the default is all pages).
6. Converting data to a dataframe.  
The method `create_dataframe(list_for_dataframe:list, *headings)` takes the list of lists generated above and converts to a dataframe. The list of lists is taken as an argument and a flexible number of headings can be optionally passed as arguments.
7. Creating a dictionary of records.  
Using the method `create_uuid_list(list_length:int)`, a UUID is generated using `str(uuid.uuid4())` syntax. The length of the UUID list is given as an argument to the method. After this uuid list object has been generated, the method `create_dict_from_2_lists(list_1:list, list_2:list)` takes the UUID list and the crypto data list of lists to make a dicitionary.
8. Store the data locally.  
The dataframe object generated in number 6 can be converted to a `.csv` file using the `save_dataframe_locally(dataframe, path:str)` method which takes the dataframe object and the path for the .csv file as arguments, thus saving these data locally. Additionally, the `turn_data_into_file(path:str, data_to_convert_into_file)` method saves the dictionary from point 7 into a `.json` file, again saving this locally based on a provided path.

## Milestone 4: Refining and Testing
**Refining**  
- Docstrings were added to all methods, as well as more # comments to improve user readability.
- Where possible methods were made private.
- Where possible code was refactored into smaller/simpler methods.
- Were possible nested loops were removed to decrease computational demand.
- Code was restructured into separate files as appropriate.  
**Testing**  
- A new file test_CMCScraper was created to implement unittest. During this process of testing some bugs were fixed:
      -  A 0.5 second pause was included between each webpage to prevent skipping webpages when multiple webpages were scraped iteratively.
      - Replacement of some instance variables to method-returned variables where possible.
      - Three exceptions to assertions were created where the scraper should have passed the assertions but the data did not follow canonical patterns.
-Unittest took 66 seconds to pass all of the tests. 
-A `tearDown()` method deletes all test files.









