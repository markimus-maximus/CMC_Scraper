
# Data Collection Pipeline Project- Coin Market Cap 

My third project for AiCore. Webscraping coinmarketcap.com for cryptocurrency data.
The milestones in this project are below:  
Milestone 1: Deciding the website to scrape
Milestone 2: Generating a list of unique URLs for each webpage
Milestone 3: Retrieving data from each webpage
Milestone 4: Refining and testing
Milestone 5: Scalably storing the data 
Milestone 6: 
Milestone 7:


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
**Tablular data**  
- There are different processes which are carried out to scrape the cryptocurrency tabular data from coinmarketcap:  
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
<img width="587" alt="image" src="https://user-images.githubusercontent.com/107410852/194768649-a52bfc34-2947-46b3-b2d0-6fd55fe5e031.png">
Example of a dataframe generated using the above methods
7. Creating a dictionary of records.  
Using the method `create_uuid_list(list_length:int)`, a UUID is generated using `str(uuid.uuid4())` syntax. The length of the UUID list is given as an argument to the method. After this uuid list object has been generated, the method `create_dict_from_2_lists(list_1:list, list_2:list)` takes the UUID list and the crypto data list of lists to make a dicitionary.
8. Store the data locally.  
The dataframe object generated in number 6 can be converted to a `.csv` file using the `save_dataframe_locally(dataframe, path:str)` method which takes the dataframe object and the path for the .csv file as arguments, thus saving these data locally. Additionally, the `turn_data_into_file(path:str, data_to_convert_into_file)` method saves the dictionary from point 7 into a `.json` file, again saving this locally based on a provided path.  
**Image data**
- Similarly to tabular data, there are different processes which are carried out to scrape the cryptocurrency image data from coinmarketcap. The prliminary parts of image scraping uses the same methods as scraping tabular data: 
1. Navigating to the webpage and extracting HTML.  
The `__get_soup(url:str)` method uses `requests` and `url` from a list of URLS (Milestone 2) to access the webpage. A beutiful soup object is then generated to extract all of the HTML.
2. Extracting data from a row.  
Similarly to the `get rows` method for tabular data above, the `__get_image_data_from_webpage(url:str)` method extracts data from each row, taking the url of the page to scrape as an argument. These data include the name of the record in the row, concatenating these names into a list. The next piece of information scraped from the row is .img data, which is refined to contain only src data (these are specifically the images from the cryptocurrencies as opposed to other website images) and appended into an image list. The name and the src are combined into a user-friendly name tag for each image.
3. Retrieve the images 
The `__retrieve_images_from_webpage(path:str, image_list:list)` method iterates through the image_list generated above to retrieve all images and save them locally. This is achieved by taking the path for file storage, and the image list from one webpage (from point 2) to iterate through. Each crypto currency image has a unique number and accordingly this number was taken as the naming convention for the images. The number was obtained by iteratively slicing the image name and renaming the file accordingly.
4. Iterate through multiple pages
The `save_images_from_multiple_webpages url_list:list, num_pages:int, path:str)` method combines the 2 methods above, taking arguments for the list containing URLs (code generated in Milestone 2), the number of URLs to iterate through and the path for file saving.
<img width="494" alt="image" src="https://user-images.githubusercontent.com/107410852/194769829-152b8414-e9c9-4992-9a6a-2e77b9bd8ca9.png">
Example images scraped using this technique
## Milestone 4: Refining and testing
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
-Unittest took 91 seconds to pass all of the tests. 
-A `tearDown()` method deletes all test files in the test data folder.

## Milestone 5: Scalably storing the data  
- For cloud-based services, Amazon Web Services (AWS) was chosen. To connect to the various serves, ssh key pairs were generated and connection was configured via Ubuntu terminal (WSL).
- An amazon S3 bucket was generated for use as a data lake and the bucket cmc-bucket-mo was generated to store data into. To generate a client connection instance the `create_s3_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)` method was generated, impementing the AWS development library `boto3`.   To upload local data into the S3 bucket, either a file or a directory can be uploaded using the `upload_file_to_s3` or `upload_folder_to_s3` methods of the `DataHandler` class. Both of these methods were again generated with the use of `boto3`. 
- Also on AWS, a Relational Database Service (RDS) was generated with which to upload tabular data. `sqlalchemy` was chosen as the python library to interact with the SQL-based server. The `create_engine_RDS` creates an instance of an RDS connection. The `upload_table_from_csv_to_RDS(path_to_csv:str, name_of_table:str` method was written to upload data in .csv to the data scraper. The data were converted to a type such that is was compatible with sql data types.
<img width="570" alt="image" src="https://user-images.githubusercontent.com/107410852/195643479-8e326661-3b4d-45d1-a6a6-d65583deb66f.png">
Example data from the RDS table  

## Milstone 6: Preventing rescraping and getting more data  

To prevent rescraping a number of approaches were employed. At the level of data acquisition, and `if` statement was implemented to ensure that scraped image data from a given page was not already scraped (each image should have a unique numerical ID):
~~~
if crypto_name_and_image_single not in self.image_data_combined_list:
                self.image_data_combined_list.append(crypto_name_and_image_single)
            #prevent_rescrape of image_list elements
            if image not in self.image_list:
                self.image_list.append(image)
                ~~~
In addition to prevent image rescraping using the above approach, a master .csv file was generated and updated every time data was scraped to keep an up-to-date record of all scraped data. Using the `get_outstanding_webpages(dataframe)` method, all possible URLS to be scraped are generated using the method `get_all_available_webpages()` which take today's date and the earliest possible date to create a dataframe of these dates. This is then compared to the 'source_url' column of the master .csv file, and any URLS for image data which is left outstanding to be scraped is given to the `save_images_from_multiple_webpages url_list:list, num_pages:int, path:str)` method. A further means of rescrape prevention was by checking that the image (uniquely name) was not already in the s3 bucket with the below code: 
~~~
file_name = str(ntpath.basename(file_path))
        logging.info(f'{file_name} check') 
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = file_name 
        #Get S3 contents and narrow down by Prefix=file_name
        already_uploaded = s3.list_objects_v2(Bucket=bucket, Prefix=file_name)
        #Convert path data type to str, needed for below
        file_path = str(file_path)
        #If 'Contents' exists in the search then there must be a match
        if 'Contents' in already_uploaded:
             print(f'{file_name} already in bucket, file not uploaded')
        elif 'Content' not in already_uploaded:
            s3.upload_file(file_path, bucket, object_name) 
            logging.info(f'{file_name} uploaded')
~~~
The above code was used in the uploading of both single files and an entire folder. In addition to the elements, rescraping could be prevented by converting the master .csv files (both in s3 bucket and local) to dataframes and using the `drop_duplicates(subset='ID')` method fom the  pandas library.

In terms of tabular data data










