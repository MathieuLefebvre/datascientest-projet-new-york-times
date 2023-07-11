from pydantic import BaseModel
from fastapi import FastAPI
from elasticsearch import AsyncElasticsearch
from datetime import date, timedelta
from typing import Optional
import json
import asyncio


api = FastAPI()
es = AsyncElasticsearch(hosts="http://@localhost:9200")


class elasticResponse(BaseModel):
    data: str


def get_time_scale(time_scale: str) -> tuple[Optional[date], Optional[date]]:
    """Return datetimes to use in queries filters

    Args:
        time_scale (str): Time scale used to define datetimes
    Returns:
        tuple(date, date): Dates corresponding of start and end of a time scale
    """

    if time_scale == "yesterday":
        today = date.today()
        start_date = today - timedelta(days=1)
        end_date = today
        return start_date, end_date

    elif time_scale == "week_ago":
        today = date.today()
        start_date = today - timedelta(days=7)
        end_date = today
        return start_date, end_date

    elif time_scale == "month_ago":
        today = date.today()
        start_date = today - timedelta(days=30)
        end_date = today
        return start_date, end_date

    else:
        return None, None


@api.get('/news/top-journalists')
async def get_top_journalists(section: str, time_scale: str) -> elasticResponse:
    """Returns top 10 journalist for a section / period filter
        It returns 10 journalists who have published most articles

    Args:
        section (str): Name of the section used in filter clause
        time_scale (str): Time scale used in the filter clause
            values can be : "yesterday", "week_ago" or "month_ago"
    Returns:
        Item : Object that embebeds elasticsearch response 
    """

    start_date, end_date = get_time_scale(time_scale=time_scale)

    query_body = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "term":
                        {
                            "section": f"{section}"
                        }
                    },
                    {
                        "range":
                            {
                                "first_published_date":
                                    {
                                        "gte": f"{start_date}",
                                        "lte": f"{end_date}"
                                    }
                            }
                    }
                ]
            }
        },
        "size": 0,
        "aggs": {
            "articles_per_author":
                {
                    "terms":
                        {
                            "field": "byline.keyword",
                            "size": 10
                        }
                }
            }
    }

    result = await es.search(index="news", body=query_body)
    result = json.dumps(result["aggregations"]["articles_per_author"]["buckets"])   

    return elasticResponse(data=result)


@api.get('/news/top-persons')
async def get_top_persons(section: str, time_scale: str) -> elasticResponse:
    """Returns top 5 persons for a section / period filter
        It returns 5 most represented persons on per_facet facet
    
    Args:
        section (str): Name of the section used in filter clause
        time_scale (str): Time scale used in the filter clause
            values can be : "yesterday", "week_ago" or "month_ago"
    Returns:
        Item : Object that embebeds elasticsearch response
    """
    start_date, end_date = get_time_scale(time_scale=time_scale)

    query_body = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "term":
                        {
                            "section": f"{section}"
                        }
                    },
                    {
                        "range":
                            {
                                "first_published_date":
                                    {
                                        "gte": f"{start_date}",
                                        "lte": f"{end_date}"
                                    }
                            }
                    }
                ]
            }
        },
        "size": 0,
        "aggs": {
            "persons":
                {
                    "terms":
                        {
                            "field": "per_facet",
                            "size": 5
                        }
                }
            }
    }

    result = await es.search(index="news", body=query_body)
    result = json.dumps(result["aggregations"]["persons"]["buckets"])   

    return elasticResponse(data=result)


@api.get('/news/articles-count')
async def get_articles_count(section: str, step: str) -> elasticResponse:
    """Returns artciles count for a section / time scale step parameter
        step parameter can be "day", "month", "quarter", "year"

    Args:
        section (str): Name of the section used in filter clause
        step (str): Step used in calendar_interval aggregation clause
            values can be "day", "month", "quarter", "year"
    Returns:
        Item : Object that embebeds elasticsearch response
    """

    query_body = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "term":
                        {
                            "section": f"{section}"
                        }
                    }
                ]
            }
        },
        "size": 0,
        "aggs": {
            "articles_over_time":
                {
                    "date_histogram":
                        {
                            "field": "first_published_date",
                            "calendar_interval": f"{step}"
                        }
                }
            }
    }

    result = await es.search(index="news", body=query_body)
    result = json.dumps(result["aggregations"]["articles_over_time"]["buckets"])   

    return elasticResponse(data=result)
