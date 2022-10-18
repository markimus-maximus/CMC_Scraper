from CMCScraper import CMCScraper
from pathlib import Path
import json
import pandas as pd

if __name__ == '__main__':
    print('starting....')
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

    CMCScraper_inst = CMCScraper()
    engine = CMCScraper_inst.create_engine_RDS(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
    s3 = CMCScraper_inst.create_s3_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    #reads the sql table and converts to dataframe.
    sql_df = pd.read_sql_table('crypto_tabular_data', engine)
    print(sql_df)
    outstanding_webpages = CMCScraper_inst.get_outstanding_webpages(sql_df)
    #retrieves the remaining data to be scraped
    get_remaining_data = CMCScraper_inst.get_crypto(outstanding_webpages, len(outstanding_webpages))
    #Creates a dataframe of the freshly-scraped data
    df_of_fresh_data = CMCScraper_inst.create_dataframe(get_remaining_data, "ID", "source_url", "Rank", "Name", "Market Capitalisation", "Price", "Circulating Supply", "Ticker", "24 h change") 
    df_of_fresh_data = df_of_fresh_data.drop_duplicates(subset='ID')
    print(f'df of fresh data {df_of_fresh_data}')
    #uploads to RDS
    df_of_fresh_data.to_sql('crypto_tabular_data', engine, if_exists='append', index= False)
    #update .csv of tabular data locally 
    CMCScraper_inst.save_dataframe_locally(df_of_fresh_data, str(Path("Data/crypto_tabular_data.csv"))) 
    #make uuid dict of exixting data
    list_of_df= df_of_fresh_data.values.tolist()
    dictionary_of_new_data = CMCScraper_inst.crypto_data_UUID_list_dictionary(list_of_df)
    #update dictionary JSON locally
    CMCScraper_inst.update_JSON_dictionary(dictionary_of_new_data, str(Path("Data/crypto_tabular_data.json")))
    #upload fresh files replacing the others
    CMCScraper_inst.rewrite_s3_file(str(Path("Data/crypto_tabular_data.csv")), 'cmc-bucket-mo', s3)
    CMCScraper_inst.rewrite_s3_file(str(Path("Data/crypto_tabular_data.json")), 'cmc-bucket-mo', s3)

    #IMAGE DATA
    #create csv object obtained from s3
    csv_obj = s3.get_object(Bucket='cmc-bucket-mo', Key='crypto_images.csv')
    # turn csv object into df
    df_of_s3 = pd.read_csv(csv_obj['Body'])
    #remove any duplicates from the .csv dataframe
    df_of_s3 = df_of_s3.drop_duplicates()
    #print contents of df
    print(f'all_s3: {df_of_s3}')
    #Calculate webpages which need to be scraped
    outstanding_webpages = CMCScraper_inst.get_outstanding_webpages(df_of_s3)
    #create dataframe of all the newly-scraped data
    new_data_dataframe = CMCScraper_inst.save_images_from_multiple_webpages(outstanding_webpages, len(outstanding_webpages), str(Path("Data/Crypto_images")))
    #remove any duplicates from the .csv dataframe
    new_data_dataframe = df_of_s3.drop_duplicates()
    #use this method to update the dataframe
    CMCScraper_inst.save_dataframe_locally(new_data_dataframe, str(Path("Data/Crypto_images/crypto_images.csv")), header_choice=False)
    #upload updated .csv file to s3
    CMCScraper_inst.rewrite_s3_file(str(Path("Data/Crypto_images/crypto_images.csv")), 'cmc-bucket-mo', s3)
    #re-upload any freshly scraped image data
    CMCScraper_inst.upload_folder_to_S3(str(Path("Data/Crypto_images/crypto_images.csv")), 'cmc-bucket-mo', s3)

  
    

