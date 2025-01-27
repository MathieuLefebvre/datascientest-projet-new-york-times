"""transform module"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                     format='%(asctime)s - %(message)s')


def results_to_list(index_name: str,
                    results: List[Dict[str, Any]]) -> List[Dict[str, Dict[str, Any]]]:
    """Transform a list of documents from NTY API to dict to bulk on Elasticsearch

    Args:
        index_name (str): index_name to provide to bulk data to Elasticsearch
        results (list): A list of documents retrived by NYT API

    Retuns
        bulk_list (lits): A list of index_name / documents ready to bulk on Elasticsearch
    """
    logger.info(f'----- Start building bulk list for {index_name} index -----')

    actions = []

    for doc in results:
        if doc is not None:
            action = {
                "_index": index_name,
                "_source": doc
            }
        actions.append(action)

    return actions
