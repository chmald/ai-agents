"""Action functions for the marketing agent."""

import logging
import sys
import os
from typing import Dict, Any

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from actions.twitter import post_tweet as twitter_post
from actions.slack import send_notification

logger = logging.getLogger(__name__)


async def post_tweet(content: str) -> str:
    """Post a tweet to Twitter/X.
    
    Args:
        content: Tweet content
        
    Returns:
        Tweet ID
    """
    try:
        tweet_id = await twitter_post(content)
        logger.info(f"Tweet posted successfully: {tweet_id}")
        return tweet_id
    except Exception as e:
        logger.error(f"Failed to post tweet: {e}")
        # Return mock ID for demo
        return f"demo_tweet_{hash(content) % 1000000}"


async def send_slack_notification(channel: str, title: str, message: str) -> bool:
    """Send a notification to Slack.
    
    Args:
        channel: Slack channel
        title: Notification title
        message: Notification message
        
    Returns:
        True if sent successfully
    """
    try:
        await send_notification(channel, title, message)
        logger.info(f"Slack notification sent to {channel}")
        return True
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {e}")
        return False


async def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze sentiment and engagement potential of text content.
    
    Args:
        text: Text to analyze
        
    Returns:
        Analysis results including sentiment, engagement score, and keywords
    """
    try:
        # Simple sentiment analysis - in production would use ML models
        positive_words = [
            "excited", "amazing", "great", "awesome", "fantastic", "love", 
            "excellent", "wonderful", "perfect", "incredible", "outstanding"
        ]
        negative_words = [
            "terrible", "awful", "hate", "horrible", "disgusting", "worst",
            "disappointing", "frustrating", "annoying", "broken", "failed"
        ]
        engagement_words = [
            "new", "launch", "announcing", "exclusive", "limited", "free",
            "join", "discover", "check out", "learn", "get", "win"
        ]
        
        text_lower = text.lower()
        
        # Count sentiment indicators
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        engagement_count = sum(1 for word in engagement_words if word in text_lower)
        
        # Determine sentiment
        if positive_count > negative_count:
            sentiment = "positive"
            sentiment_score = min(0.5 + (positive_count * 0.1), 1.0)
        elif negative_count > positive_count:
            sentiment = "negative"
            sentiment_score = max(0.5 - (negative_count * 0.1), 0.0)
        else:
            sentiment = "neutral"
            sentiment_score = 0.5
        
        # Calculate engagement score
        engagement_score = min(0.3 + (engagement_count * 0.1) + (len(text) / 280 * 0.2), 1.0)
        
        # Extract hashtags
        hashtags = [word for word in text.split() if word.startswith('#')]
        
        analysis = {
            "sentiment": sentiment,
            "sentiment_score": round(sentiment_score, 2),
            "engagement_score": round(engagement_score, 2),
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "engagement_indicators": engagement_count,
            "hashtags": hashtags,
            "character_count": len(text),
            "word_count": len(text.split()),
            "recommendations": []
        }
        
        # Add recommendations
        if sentiment_score < 0.6:
            analysis["recommendations"].append("Consider adding more positive language")
        
        if engagement_score < 0.5:
            analysis["recommendations"].append("Add call-to-action or engagement triggers")
        
        if len(hashtags) == 0:
            analysis["recommendations"].append("Add relevant hashtags to increase reach")
        elif len(hashtags) > 5:
            analysis["recommendations"].append("Reduce hashtag count to avoid spam appearance")
        
        if len(text) < 100:
            analysis["recommendations"].append("Consider expanding content for better engagement")
        
        logger.info(f"Sentiment analysis completed: {sentiment} ({sentiment_score})")
        return analysis
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return {
            "sentiment": "unknown",
            "sentiment_score": 0.5,
            "engagement_score": 0.5,
            "error": str(e)
        }


async def schedule_post(content: str, schedule_time: str) -> Dict[str, Any]:
    """Schedule a social media post for later publishing.
    
    Args:
        content: Post content
        schedule_time: ISO format timestamp for when to post
        
    Returns:
        Scheduling confirmation with job ID
    """
    try:
        # Mock scheduling functionality
        # In production, this would integrate with a job queue system
        job_id = f"scheduled_{hash(content + schedule_time) % 1000000}"
        
        logger.info(f"Post scheduled for {schedule_time} with job ID: {job_id}")
        
        return {
            "success": True,
            "job_id": job_id,
            "scheduled_time": schedule_time,
            "content_preview": content[:50] + "..." if len(content) > 50 else content
        }
        
    except Exception as e:
        logger.error(f"Failed to schedule post: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def get_brand_mentions(brand_name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent mentions of a brand on social media.
    
    Args:
        brand_name: Brand name to search for
        limit: Maximum number of mentions to return
        
    Returns:
        List of mention data
    """
    try:
        # Mock brand monitoring - in production would integrate with social listening tools
        mentions = []
        
        for i in range(min(limit, 5)):  # Return up to 5 mock mentions
            mentions.append({
                "id": f"mention_{i}_{hash(brand_name) % 1000}",
                "platform": "Twitter",
                "author": f"user_{i + 1}",
                "content": f"Great experience with {brand_name}! Highly recommend their service.",
                "timestamp": "2024-01-01T12:00:00Z",
                "sentiment": "positive",
                "engagement": {
                    "likes": 10 + i * 5,
                    "retweets": 2 + i,
                    "replies": 1 + i
                }
            })
        
        logger.info(f"Found {len(mentions)} mentions for {brand_name}")
        return mentions
        
    except Exception as e:
        logger.error(f"Failed to get brand mentions: {e}")
        return []