"""Slack API integration for team communication."""

import os
import logging
from typing import Dict, Any, Optional, List
import httpx

logger = logging.getLogger(__name__)


class SlackClient:
    """Slack API client for team communication."""
    
    def __init__(self):
        self.token = os.getenv("SLACK_BOT_TOKEN")
        self.base_url = "https://slack.com/api"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        } if self.token else {}
    
    async def send_message(
        self, 
        channel: str, 
        text: str, 
        blocks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send a message to a Slack channel.
        
        Args:
            channel: Channel name (#general) or ID
            text: Message text
            blocks: Rich message blocks (optional)
            
        Returns:
            Message response data
        """
        if not self.token:
            logger.warning("SLACK_BOT_TOKEN not set, returning mock response")
            return {
                "ok": True,
                "ts": "1234567890.123456",
                "channel": channel,
                "message": {"text": text}
            }
        
        try:
            message_data = {
                "channel": channel,
                "text": text
            }
            if blocks:
                message_data["blocks"] = blocks
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat.postMessage",
                    headers=self.headers,
                    json=message_data
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            raise
    
    async def update_message(
        self, 
        channel: str, 
        ts: str, 
        text: str,
        blocks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Update an existing message.
        
        Args:
            channel: Channel name or ID
            ts: Message timestamp
            text: New message text
            blocks: Rich message blocks (optional)
            
        Returns:
            Update response data
        """
        if not self.token:
            logger.warning("SLACK_BOT_TOKEN not set, returning mock response")
            return {"ok": True, "ts": ts}
        
        try:
            message_data = {
                "channel": channel,
                "ts": ts,
                "text": text
            }
            if blocks:
                message_data["blocks"] = blocks
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat.update",
                    headers=self.headers,
                    json=message_data
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to update Slack message: {e}")
            raise
    
    async def get_channels(self) -> List[Dict[str, Any]]:
        """Get list of channels the bot has access to.
        
        Returns:
            List of channel data
        """
        if not self.token:
            logger.warning("SLACK_BOT_TOKEN not set, returning mock response")
            return [
                {"id": "C1234567890", "name": "general"},
                {"id": "C0987654321", "name": "marketing"}
            ]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/conversations.list",
                    headers=self.headers,
                    params={"types": "public_channel,private_channel"}
                )
                response.raise_for_status()
                result = response.json()
                return result.get("channels", [])
        except Exception as e:
            logger.error(f"Failed to get Slack channels: {e}")
            return []


# Default client instance
slack_client = SlackClient()


async def send_message(channel: str, text: str) -> str:
    """Send a message to a Slack channel.
    
    Args:
        channel: Channel name (#general) or ID
        text: Message text
        
    Returns:
        Message timestamp
    """
    response = await slack_client.send_message(channel, text)
    return response.get("ts", "")


async def send_notification(
    channel: str, 
    title: str, 
    message: str, 
    color: str = "good"
) -> str:
    """Send a formatted notification to Slack.
    
    Args:
        channel: Channel name
        title: Notification title
        message: Notification message
        color: Notification color (good, warning, danger)
        
    Returns:
        Message timestamp
    """
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{title}*\n{message}"
            }
        }
    ]
    
    # Add color bar using attachment fallback
    text_with_status = f"🔔 *{title}*\n{message}"
    
    response = await slack_client.send_message(
        channel=channel,
        text=text_with_status,
        blocks=blocks
    )
    return response.get("ts", "")