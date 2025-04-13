import os
import json
import logging
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_DETAILS_URL = "https://www.googleapis.com/youtube/v3/videos"

def get_youtube_api_key():
    secret_name = os.getenv("YOUTUBE_API_SECRET_NAME", "youtube/api/key")
    region_name = os.getenv("AWS_REGION", "us-east-1")

    client = boto3.client("secretsmanager", region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])["YOUTUBE_API_KEY"]

def fetch_json(url, params):
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"

    logger.info(f"Fetching URL: {full_url}")
    with urllib.request.urlopen(full_url) as response:
        data = response.read()
        return json.loads(data)

def search_videos(query, days=7, max_results=5):
    api_key = get_youtube_api_key()
    published_after = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"

    search_params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "publishedAfter": published_after,
        "order": "viewCount",
        "key": api_key,
    }

    search_response = fetch_json(YOUTUBE_SEARCH_URL, search_params)
    items = search_response.get("items", [])
    video_ids = [item["id"]["videoId"] for item in items]

    if not video_ids:
        return []

    details_params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": api_key,
    }

    details_response = fetch_json(YOUTUBE_VIDEO_DETAILS_URL, details_params)
    details = details_response.get("items", [])
    results = []

    for item in details:
        results.append({
            "id": item["id"],
            "title": item["snippet"]["title"],
            "channelTitle": item["snippet"]["channelTitle"],
            "publishedAt": item["snippet"]["publishedAt"],
            "viewCount": item["statistics"].get("viewCount", "0"),
            "likeCount": item["statistics"].get("likeCount", "0"),
            "url": f"https://www.youtube.com/watch?v={item['id']}"
        })

    return results

def lambda_handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        query = params.get("q", "genAI")  # Default query
        days = int(params.get("days", "7"))
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }

    try:
        videos = search_videos(query, days=days)
        return {
            "statusCode": 200,
            "body": json.dumps(videos)
        }
    except Exception as e:
        logger.error(str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "YouTube search failed"})
        }
