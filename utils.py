import re

def extract_video_id(url):
    from urllib.parse import urlparse, parse_qs
    query = urlparse(url)
    return parse_qs(query.query).get("v", [None])[0]
