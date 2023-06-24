"""Extract module"""


import logging

import requests
from elasticsearch import Elasticsearch
from load import bulk_to_elasticsearch
from transform import results_to_list
from utils import build_query


def get_news_sections(self, con: Elasticsearch,
                          api_key: str) -> List(str):
        """ Get list of news section from NYT API

        Args:
            con (Elasticsearch): Connector object used to connect to database
            api_key (str): Used NYT api key to retrieve data

        Returns:
            sections (list): List of news sections retrieved from NYT API
        """
        logging.info('----- Retrieving news sections -----')
        query = build_query(index_name='news_sections', api_key=api_key)
        results = requests.get(query)
        sections = [item['section'] for item in results.json()['results']]
        logging.info(f'----- News sections: \n {sections} \n')

        self.api_calls += 1

        return sections


def get_news_data(self, con: Elasticsearch, api_key: str,
                    api_calls: int) -> None:
    """Get news documents from NYT newswire API

    Args:
        con (Elasticsearch): Connector object used to connect to database
        api_key (str): Used NYT api key to retrieve data
        api_calls (int): Number of API calls used by the script
    
    Returns:
        None
    """

    logging.info('----- Start geting news data from NYT API -----')

    sections = self.get_news_sections(con=con, api_key=api_key, api_calls=api_calls)

    for section in sections:

        logging.info(f'----- Start retriving data from section: {section} -----')

        #Request the Api
        query = build_query(index_name='news', news_section=section, api_key=api_key)
        content = requests.get(query)

        #save into the ES DB
        res = content.json()
        logging.info(f'----- Retrieved results: \n {res} \n -----')       

        docs = res['results']

        # Prepare the documents for bulk indexing
        actions = results_to_list(index_name='news', results=docs)

        # Perform the bulk indexing
        response = bulk_to_elasticsearch(con=con, bulk_list=actions)

        # Check the response
        if not response[1]:
            print(f'{section} saved successfully')
        else:
            print('Failed to save content.')

        self.api_calls += 1
        
        ######################################################
        time.sleep(13) ##### TO MODIFY ACCORDING API ALLOWANCE
        #################### 5 requests max per minute ######
        ######################################################


def get_books_or_movies_data(self, con: Elasticsearch, index_name: str,
                start_offset: int, results_by_page: int, api_cals: int,
                max_api_calls: int, api_key: str) -> None:
    """Get books or movies documents from books API
        For both logic is the same due to API calls limites

    Args:
        con (Elasticsearch): Connector object used to connect to database
        content_type (str): Name of the Elasticsearch index where documents
            are added
        enpoint_hits (int): Number of returned hits from NYT API books
        start_offset (int): Offset number to pass to the API call in
            order to specify where to start retrieving data
        api_calls (int): Number of API calls since start of the script 
        results_by_page (int): Number of results of each reponse from NYT API calls
        max_api_calls (int): Maximum of dailly calls allowed by the NYT API
        api_key (str): Used NYT api key to retrieve data

    Returns:
        None
    """
    logging.info(f'----- Start getting {index_name} from NYT API -----')

    internal_api_calls = 0

    while (self.api_calls < max_api_calls):

        now = datetime.datetime.now()
        logging.info(f'----- Number of NYT API calls {internal_api_calls} \n -----')
        logging.info(f'----- query starts at offset:{internal_api_calls} at: {now} -----')

        # Request the Api
        query = build_query(index_name=index_name, start_offset=start_offset)
        content = requests.get(query)

        # save into the ES DB
        res = content.json()
        endpoint_hits = res['num_results']

        logging.info(f"----- Json response page regarding start_offset: {start_offset} \n {res} -----")

        docs = res['results']
        actions = results_to_list(index_name=index_name, results=docs)

        # Perform the bulk indexing
        response = bulk_to_elasticsearch(con=con, bulk_list=actions)

        # Check the response
        if not response[1]:
            saved_books = internal_api_calls * results_by_page
            logging.info(f'----- {saved_books} books saved successfully  -----')
            logging.info(f'----- Remaining books save regarding endpoints hits: {endpoint_hits - saved_books} -----')
        else:
            logging.warning('----- Failed to save content. -----')

        start_offset += results_by_page

        self.api_calls += 1
        internal_api_calls += 1

        ######################################################
        time.sleep(12)  ##### TO MODIFY ACCORDING API ALLOWANCE
        ######################################################

    logging.info(f'----- Next offset to use on API call: {start_offset} -----')
