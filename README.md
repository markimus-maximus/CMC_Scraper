
# Data Collection Pipeline Project- Coin Market Cap Web Scraper

My third project with the aiCore workflow was to design and implement a data collection pipeline. To acquire data a webscraper was written to scrape coinmarketcap.com for cryptocurrency data.
The milestones in this project are below:  
Milestone 1: Deciding the website to scrape  

Milestone 2: Generating a list of unique URLs for each webpage  

Milestone 3: Retrieving data from each webpage  

Milestone 4: Refining and testing  

Milestone 5: Scalably storing the data  

Milestone 6: Preventing rescraping and getting more data  

Milestone 7.1: Containerising the scraper  

Milestone 7.2: Running the scraper on a cloud computer  

Milestone 8: Monitoring and alerting  

Milestone 9: Setting up a CI/CD pipeline for the docker image  


## Milestone 1: Deciding the website to scrape
-	The aim of this project is to collect data crypto currency data and using this data to characterise factors which may impact cryptocurrency market standing.
-	Coinmarketcap.com was selected for the following reasons:
    *	Consistent url naming including date-based permalinks means that the url for a particular date could be generated easily in a list format. This ability to predetermine urls negates the need for using webdrivers to click next pages etc., while also allowing scraping of data of pre-defined intervals e.g. monthly. 
    *	Rich historical data dating back to April 2013 providing greater potential for insights. 
    * Consistent structure of historical data allows for consistent scraping of data between urls.
    * Relatively simple website without need for login or cookies bypass.
-	In combination with pre-determined urls the `requests` package was imported to access webpages.
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

- The fact that coinmarketcap URLs are structured such that the permalink contains a date this allowed for generation of unique URLs based on the date. To generate the list of URLs, the `daterange(start_date:str, end_date:str, frequency:int=None` method was built which used the pandas library to generate a date range between 2 dates given to by the user. The `strftime` method was implemented to reformat the date to be used as a permalink. Additionally, slicing the daterange provides the user the optional opportunity to choose a frequency of dates by declaring the `frequency` argument (default frequency is daily).
- After generation of the desired daterange, the `__create_url_list_with_date_permalinks(root_url:str, date_list:list)` private method concatenates the dates (formatted as cmc permalinks) to a root URL thus generating a list of unique URLs which would be compatible with coinmarket cap.
- The `create_url_list_final(start_date:str, end_date:str, frequency:int, root_url:str` public method combines the two methods above to generate the list of URLs with which to use with the scraper.

## Milestone 3: Retrieving data from each webpage
**Tablular data**  
- There are different processes which are carried out to scrape the cryptocurrency tabular data from coinmarketcap:  
1. Navigating to the webpage and extracting HTML.  
The `__get_soup(url:str)` method uses `requests` and `url` from a list of URLS (Milestone 2) to access the webpage. A beutiful soup object is then generated to extract all of the HTML.
2. Extracting data from a row.  
Rows include data from one cryptocurrency. For example all of the data associated with bitcoin on one day is contained within a row. The method `__get_crypto_rows(url_list:list, num_page:int)` uses `soup.find_all('tr', attrs={'class':'cmc-table-row'})` to extract all rows. In addition, the `__get_crypto_rows` method generates a list of the URLS accessed.
3. Extracting individual data from each row.  
Individual data from one row includes `Rank, Name, Market Capitalisation, Price, Circulating Supply, Ticker, 24 h change`. These data are extracted using the `__scrape_items_from_row()` method. These data were extracted using the `td` tag, for example: `(row.find('td', attrs={'class': 'cmc-table__cell cmc-table__cell--sticky cmc-table__cell--sortable cmc-table__cell--left cmc-table__cell--sort-by__rank'}).text.strip())` where `.strip` extracts only the text. The extracted text was typed appropriately, e.g. `str` for names and `float` for price. To clean the data, `re.sub("[^\d\.]", "", <variable>)` was used on float data to remove any non-numerical data. This method then appends the data to an instance list variable. A user-friendly tag can be generated using the `__generate_user_friendly_tag()` method, which generates a unique ID by combining the name for a particular record with the source url.
4. Concatenating data into a list of lists according to the day of record. 
After all of the data across the desired number of webpages has been scraped, the result is a series of category lists with concatenated data e.g. name list. In order to match each record from a given list with its corresponding data (e.g. cryptocurrency name with price of the same day), the `__daily_record_concatenater()`' method combines each record category based on the index to create a list of all records e.g. `['Bitcoin https://coinmarketcap.com/historical/20130509/', 'https://coinmarketcap.com/historical/20130509/', 1, 'Bitcoin', 1254535361.61, 112.67, 11134600.0, 'BTC', 0.1]` which corresponds to `["ID", "source_url", "Rank", "Name", "Market Capitalisation", "Price", "Circulating Supply", "Ticker", "24 h change"]` for one record. This concatenation is carried out for every index in each list to return a list of lists.
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
In addition to prevent image rescraping using the above approach, a master .csv file was generated and updated every time data was scraped to keep an up-to-date record of all scraped data (later this was downloaded from the RDS). Using the `get_outstanding_webpages(dataframe)` method, all possible URLS to be scraped are generated using the method `get_all_available_webpages()` which take today's date and the earliest possible date to create a dataframe of these dates. This is then compared to the 'source_url' column of the master .csv file, and any URLS for image data which is left outstanding to be scraped is given to the `save_images_from_multiple_webpages url_list:list, num_pages:int, path:str)` method. A further means of rescrape prevention was by checking that the image (uniquely name) was not already in the s3 bucket with the below code: 
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
            logging.info(f'{file_name} uploaded')~~~
The above code was used in the uploading of both single files and an entire folder. In addition to these approaches, rescraping is prevented by converting the master .csv files (both in s3 bucket and local) to dataframes and using the `drop_duplicates(subset='ID')` method fom the  pandas library.

In terms of tabular data, rescraping was similarly implemented by using the `get_all_available_webpages()` method to get only fresh data and preclude scraping of any unnecessary data, and accordingly that the RDS does not contain duplicate data. As a failsafe, the `drop_duplicates(subset='ID')` method fom the pandas library ensures that no duplicates are re-added to the RDS.  An altrnative strategy to preventing rescraping would be to create a SQL query with the `psycopg2` library:
`with conn.cursor() as cur: 
                     ~~~
                    # check if the record exists using unique ID. If it does then do nothing, if it doesn't then upload the new record. 
                    cur.execute("SELECT ID FROM crypto_tabular_data WHERE ID=%s",(ID,))`
                    ~~~
This approach was not selected here since the other approach generates and updates .csv files which can be stored both locally and on the cloud as backup master copies.

## Milestone 7.1: Containerising the scraper  
In order to easily facilitate running of the scraper on any machine, the scraper and all files were containerised into a docker image. A `__main__.py` file was created which would run the necessary methods from the `CMCScraper.py` and `DataHandler.py` classes in order to run the scraper from a container. A requirements.txt file was also created to allow for dependencies to be installed on the image. A credentials JSON file was created which holds all of the authentication data for connecting to RDS and s3 databases.

- A docker file was created with the instructions to build the container (below). `Ubuntu` was taken as the base image, and the scraper folder was copied to the image.

~~~
FROM ubuntu:latest

RUN apt update
RUN apt install python3 -y
RUN set -xe \
    && apt-get update -y \
    && apt-get install -y python3-pip

COPY . .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

CMD ["python3", "__main__.py"]
~~~

- The docker container was built using the syntax `docker build -t docker build -t markimusmaximus/cmc_scraper_1 .` 

The docker image was pushed to dockerhub with `docker push [OPTIONS] NAME[:TAG]`

-The image was run directly from the CLI.
`docker run -it --rm \`

## Milestone 7.2: Running the scraper on a cloud computer
An Elastic Cloud Computing (EC2) instance was established on the AWS platform to run the scraper program remotely. The operating system chosen was `Amazon Linux 2 AMI` with `t2-micro` instance type. 
- A security group was established and configure as below:
   - HTTP: Anywhere IPv4
	- HTTPS: Anywhere IPv4
   - SSH: My IP
- An ssh key pair was generated to authenticate the connection. The priveleges were changed in the terminal to 'read only' using the syntax `chmod 400 <key.pem>` 
- To connect to the EC2 instance through the CLI, `ssh -i /<path to key> ec2-user@<public-dns>` was used.
- To add the directory of the scraper to the EC2 instance, `scp -i <path/ec2_key.pem> -r <directory path> /home/ec2-user` was run.
- Docker was then installed to this EC2 instance
~~~
sudo yum update -y
sudo amazon-linux-extras install docker
sudo service docker start
sudo systemctl enable docker
~~~
- The scraper image was pulled from dockerhub by using `docker run` again.
-In order to call the scraper at regular intervals on the EC2 instance, a cronjob was established in the EC2 instance OS. To create and configure the cronjob, `cronjob -e` was run in the CLI.
-To set the timing to 10:30 every day, the cronjob was edited in vim editor as follows `30 10 * * *`

## Milestone 8: Monitoring and alerting

Prometheus allows real time montoring of various programmatic metrics by pulling data from the apllication of interest at specific time-intervals, and coupling these data with time stamps. This can be accessed by specifying the IP address and the port in a web browser. Similarly to the scraper files, prometheus was containerised on the same EC2 instance. The prometheus config file was written as follows:
~~~
global:
  scrape_interval: 15s 
  
  external_labels:
    monitor: 'codelab-monitor'

scrape_configs:
  
  - job_name: 'prometheus'
    
    scrape_interval: '5s'
    static_configs:
      - targets: ['localhost:9090', '<EC2 instance IP:9090']

  - job_name: 'docker'
    
    scrape_interval: '5s'
    static_configs:
      - targets: ['<Docker IP>:9323']~~~
- Permissions of the EC2 instance were modified such that port 9090 was accessible as shown in the image below:
<img width="680" alt="image" src="https://user-images.githubusercontent.com/107410852/196372807-4f78fe83-9213-4f48-a12a-4946e4ce405b.png">

- Node exporter is a single static binary that facilitates tracking metrics from the local OS system. This was set up in the CLI with the following:
~~~
wget https://github.com/prometheus/node_exporter/releases/download/v1.1.2/node_exporter-1.1.2.linux-amd64.tar.gz
tar xvfz node_exporter-1.1.2.linux-amd64.tar.gz
rm node_exporter-1.1.2.linux-amd64.tar.gz~~~
- Node exporter was run in the CLI with `./node_exporter-1.1.2.linux-amd64/node_exporter`  
The prometheus container was run with the following command in the CLI: 
~~~
	sudo docker run --rm -d \
    --network=host \
    --name prometheus\
    -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
    prom/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --web.enable-lifecycle ~~~
-d: runs the container in detached mode. This runs the container in the background (terminal not occupied by the cotainer).  
-rm: removes the container when the process is killed.  
-network=host: configures the ports on the local machine with the ports inside the Docker container (when localhost host is specified in prometheus.yml).  
--name: name of the container.  
-v: mounts the prometheus config in the container to your local config, allowing post-hoc configurations.  
--config.file: the Docker container path for the prometheus.yml config file.  
~~~	
- Grafana was used to aggregate prometheus metrics into an at-a-glance dashboard. Below is an example dashboard while the scraper was running in the EC2 instance.
<img width="693" alt="image" src="https://user-images.githubusercontent.com/107410852/196400100-eff13994-6386-4506-bbe9-bfe63d0c46cb.png">

## Milestone 9: Setting up a CI/CD pipeline for the docker image  
Continuous integration (CI) of software ensures that changes can be integrated from mutltiple contributors, while coninuous deployment allows for integration of many small changes over time as opposed to infrequent large changes which could be associated with difficulties such as unforeseen bugs or end-user difficulties due to too many changes at once.  
- Github Actions provides a tool to facilitate a CI/CD pipeline by integrating automated actions once a particular event has occurred. For example, this could be updating a server every time new code of a particular script has been uploaded to GitHub. Using Github Actions, a new Docker image was instructed to be generated and pushed to Dockerhub every time a new push occurred in the associated repository. 
- To keep Docker hub credentials private, Github Secrets was utilised in which the appropriate information was stored. 
- The .yaml file which configures the Github Action:

name: CI

#triggers jobs on
on: 
#when a push happens
  push:
#on the master branch
    branches:
      - 'master'
  #OR triggers jobs when dispatched manually
  workflow_dispatch:
#The jobs which are carried out
jobs: 
#how it's executed
  build:
  #local virtual machine running ubuntu 
    runs-on: ubuntu-latest
    #steps to be carried out
    steps:
    -
      name: Checkout
      uses: functions/checkout@v2
    -
      name: Login to Docker Hub
      uses: docker/login-action@v1
      with:
        username: ${{ secrets.DOCKER_HUB_USERNAME }}
        password: ${{ secrets.DOCKER_HUB_ACCESS_TOKEN }}
    -
      name: Set up Docker Build
      uses: docker/setup-build-action@v1
    -
      name: Build and push
      uses: docker/build-push-action@v2
      with:
        context: .
        file: ../CMC_Scraper/Dockerfile
        push: true
        tags: ${{ secrets.DOCKER_HUB_USERNAME }}/cmc_scraper_1:latest~~~
	
- The EC2 instance which runs the docker scraper image was operated with a crontab file (written in vim editor in the CLI) in order to run the scraper on the instance at a regular time interval. A job was written to run the docker image and another to ensure that all images had been removed from the server consequently.

~~~
0 16 * * * sudo docker run --rm <dockerhub_identifier>:latest
30 16 * * * sudo docker ps -aq~~~














