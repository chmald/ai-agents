"""Marketing agent implementation using LangGraph."""

import logging
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain.schema import HumanMessage, SystemMessage
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from llm.openai_client import llm
from .actions import post_tweet, send_slack_notification, analyze_sentiment

logger = logging.getLogger(__name__)


class MarketingState(TypedDict):
    """State for the marketing agent workflow."""
    content: Dict[str, str]
    tweet: str
    tweet_id: str
    slack_message: str
    sentiment_analysis: Dict[str, Any]
    error: str


class MarketingAgent:
    """AI agent for marketing automation and social media management."""
    
    def __init__(self):
        """Initialize the marketing agent with StateGraph workflow."""
        self.graph = StateGraph(MarketingState)
        self._build_graph()
        self.workflow = self.graph.compile()
    
    def _build_graph(self):
        """Build the StateGraph workflow."""
        
        async def generate_tweet(state: MarketingState) -> MarketingState:
            """Generate a tweet from the provided content."""
            try:
                logger.info("Generating tweet content")
                
                content = state["content"]
                title = content.get("title", "")
                body = content.get("body", "")
                
                system_prompt = (
                    "You are a professional social media manager. Create engaging tweets "
                    "that are concise, on-brand, and likely to drive engagement. "
                    "Keep tweets under 280 characters and include relevant hashtags. "
                    "Use a friendly but professional tone."
                )
                
                user_prompt = f"""
                Create a tweet based on this content:
                Title: {title}
                Body: {body}
                
                Make it engaging and include 2-3 relevant hashtags.
                """
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]
                
                response = await llm.agenerate(messages)
                tweet = response[0].content.strip()
                
                # Ensure tweet is under 280 characters
                if len(tweet) > 280:
                    tweet = tweet[:277] + "..."
                
                logger.info(f"Generated tweet: {tweet[:50]}...")
                return {**state, "tweet": tweet}
                
            except Exception as e:
                logger.error(f"Failed to generate tweet: {e}")
                return {**state, "error": str(e)}
        
        async def publish_content(state: MarketingState) -> MarketingState:
            """Publish the tweet and send notifications."""
            try:
                logger.info("Publishing content to social media")
                
                tweet = state["tweet"]
                if not tweet:
                    return {**state, "error": "No tweet content to publish"}
                
                # Post tweet
                tweet_id = await post_tweet(tweet)
                
                # Create Slack notification
                slack_message = f"✅ Tweet published successfully!\n\nContent: {tweet}\nTweet ID: {tweet_id}"
                await send_slack_notification("#marketing", "Tweet Published", slack_message)
                
                logger.info(f"Content published. Tweet ID: {tweet_id}")
                return {**state, "tweet_id": tweet_id, "slack_message": slack_message}
                
            except Exception as e:
                logger.error(f"Failed to publish content: {e}")
                return {**state, "error": str(e)}
        
        async def analyze_content(state: MarketingState) -> MarketingState:
            """Analyze the sentiment and engagement potential of the content."""
            try:
                logger.info("Analyzing content sentiment and engagement potential")
                
                tweet = state["tweet"]
                if not tweet:
                    return {**state, "error": "No content to analyze"}
                
                # Perform sentiment analysis
                analysis = await analyze_sentiment(tweet)
                
                logger.info(f"Content analysis completed: {analysis.get('sentiment', 'unknown')} sentiment")
                return {**state, "sentiment_analysis": analysis}
                
            except Exception as e:
                logger.error(f"Failed to analyze content: {e}")
                return {**state, "error": str(e)}
        
        # Add nodes to the graph
        self.graph.add_node("generate", generate_tweet)
        self.graph.add_node("analyze", analyze_content)
        self.graph.add_node("publish", publish_content)
        
        # Add edges
        self.graph.add_edge(START, "generate")
        self.graph.add_edge("generate", "analyze")
        self.graph.add_edge("analyze", "publish")
        self.graph.add_edge("publish", END)
    
    async def process(self, title: str, body: str) -> Dict[str, Any]:
        """Process marketing content and publish to social media.
        
        Args:
            title: Content title
            body: Content body/description
            
        Returns:
            Result dictionary with tweet ID and analysis
        """
        initial_state = MarketingState(
            content={"title": title, "body": body},
            tweet="",
            tweet_id="",
            slack_message="",
            sentiment_analysis={},
            error=""
        )
        
        try:
            final_state = await self.workflow.ainvoke(initial_state)
            
            if final_state.get("error"):
                return {"success": False, "error": final_state["error"]}
            
            return {
                "success": True,
                "tweet": final_state["tweet"],
                "tweet_id": final_state["tweet_id"],
                "sentiment_analysis": final_state["sentiment_analysis"],
                "engagement_score": final_state["sentiment_analysis"].get("engagement_score", 0)
            }
            
        except Exception as e:
            logger.error(f"Marketing agent workflow failed: {e}")
            return {"success": False, "error": str(e)}