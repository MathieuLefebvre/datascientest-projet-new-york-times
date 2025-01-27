"""load module"""

import logging
from typing import Any, Dict, List

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s')


def create_index(con: Elasticsearch, name: str,
                 mapping: Dict[str, Dict[str, str]],
                 settings: Dict[str, int]) -> None:

    """Create an index in Elasticsearch database

    Args:
        con (Elasticsearch): Connector object used to connect to database
        name (str): Index name
        mapping (dict): Index mapping
        settings (dict): Index settings

    Returns:
        None
    """

    logger.info(f'----- Start index {name} creation -----')

    try:
        response = con.indices.create(index=name, mappings=mapping,
                                      settings=settings)

        if response['acknowledged']:
            logger.info(f'----- Index {name} created successfully. -----')

        else:
            logger.warning(f'----- Failed to create {name} index. -----')

    except Exception as e:
        logger.warning(f"-----Error:{e}-----")


def delete_index(name: str, con: Elasticsearch) -> None:
    """Drop an index in Elastiseacrh

    Args:
            con (Elasticsearch): Connector object used to connect to database
            name (str): Index name

    Return:
        None
    """

    logger.info(f'----- deleting {name} index -----')

    try:
        con.indices.delete(index=name)
    except Exception as e:
        logger.warning(f"-----Error:{e}-----")

    logger.info(f'----- {name} index deleted -----')


def bulk_to_elasticsearch(
                          con: Elasticsearch,
                          bulk_list: List[Dict[str, Dict[str, Any]]],
                        ) -> None:
    """ Run Elasticsearch Bulk API with results from NYT API

    Args:
        con (Elasticsearch):
        bult_list (list): A list of documents with index_names from NYT API results

    Returns:
        ObjectApiREsponse : Response from Elasticsearh Bulk API call
    """
    logger.info('----- Start saving documents ----')

    try:
        response = bulk(con, bulk_list)

        if not response[1]:
            saved_documents = len(bulk_list)
            logger.info(f'----- {saved_documents} documents saved successfully  -----')

        else:
            logger.warning('----- Failed to save documents. -----')

    except Exception as e:
        logger.warning(f"-----Error:{e}-----")

    logger.info('----- Finish saving documents from bulk -----')
