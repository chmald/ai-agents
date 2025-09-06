"""Twitter/X API integration for social media marketing."""

import os
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)


class TwitterClient:
    """Twitter/X API client for social media operations."""
    
    def __init__(self):
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        } if self.bearer_token else {}
    
    async def post_tweet(self, text: str, reply_to: Optional[str] = None) -> Dict[str, Any]:
        """Post a tweet.
        
        Args:
            text: Tweet content (max 280 chars)
            reply_to: Tweet ID to reply to
            
        Returns:
            Tweet data with ID and URL
        """
        if not self.bearer_token:
            logger.warning("TWITTER_BEARER_TOKEN not set, returning mock response")
            return {
                "id": "1234567890",
                "text": text[:280],
                "url": "https://twitter.com/demo/status/1234567890"
            }
        
        try:
            # Truncate text to fit Twitter's limit
            if len(text) > 280:
                text = text[:277] + "..."
            
            tweet_data = {"text": text}
            if reply_to:
                tweet_data["reply"] = {"in_reply_to_tweet_id": reply_to}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/tweets",
                    headers=self.headers,
                    json=tweet_data
                )
                response.raise_for_status()
                result = response.json()
                
                tweet_id = result["data"]["id"]
                return {
                    "id": tweet_id,
                    "text": text,
                    "url": f"https://twitter.com/i/web/status/{tweet_id}"
                }
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            raise
    
    async def search_tweets(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for tweets.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of tweet data
        """
        if not self.bearer_token:
            logger.warning("TWITTER_BEARER_TOKEN not set, returning mock response")
            return [
                {
                    "id": "1111111111",
                    "text": f"Mock tweet matching '{query}'",
                    "author_id": "demo_user"
                }
            ]
        
        try:
            params = {
                "query": query,
                "max_results": min(max_results, 100),
                "tweet.fields": "author_id,created_at,public_metrics"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/tweets/search/recent",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                result = response.json()
                
                return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to search tweets: {e}")
            return []


# Default client instance
twitter_client = TwitterClient()


async def post_tweet(text: str, reply_to: Optional[str] = None) -> str:
    """Post a tweet and return the tweet ID.
    
    Args:
        text: Tweet content
        reply_to: Tweet ID to reply to
        
    Returns:
        Tweet ID
    """
    tweet_data = await twitter_client.post_tweet(text, reply_to)
    return tweet_data["id"]


async def search_mentions(brand_name: str) -> List[Dict[str, Any]]:
    """Search for mentions of a brand or product.
    
    Args:
        brand_name: Brand or product name to search for
        
    Returns:
        List of tweets mentioning the brand
    """
    query = f'"{brand_name}" OR @{brand_name}'
    return await twitter_client.search_tweets(query)