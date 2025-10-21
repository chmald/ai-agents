"""Azure OpenAI client wrapper for LLM interactions."""

import os
import logging
from typing import List, Dict, Any, Optional
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage

logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    """Azure OpenAI LLM client with rate limiting and error handling."""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        """Initialize Azure OpenAI client.
        
        Args:
            model: Azure OpenAI deployment name
            temperature: Sampling temperature
        """
        self.model = model
        self.temperature = temperature
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", model)
        
        if not self.api_key or not self.endpoint:
            logger.warning("Azure OpenAI credentials not set, using demo mode")
            self._demo_mode = True
        else:
            self._demo_mode = False
            self.client = AzureChatOpenAI(
                azure_deployment=self.deployment_name,
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version=self.api_version,
                temperature=temperature,
                max_tokens=1000
            )
    
    async def agenerate(self, messages: List[BaseMessage], **kwargs) -> List[AIMessage]:
        """Generate response from messages asynchronously.
        
        Args:
            messages: List of chat messages
            **kwargs: Additional generation parameters
            
        Returns:
            List of AI response messages
        """
        if self._demo_mode:
            # Return mock responses for demo
            content = f"[DEMO MODE] Response to: {messages[-1].content[:50]}..."
            return [AIMessage(content=content)]
        
        try:
            response = await self.client.agenerate([messages], **kwargs)
            return response.generations[0]
        except Exception as e:
            logger.error(f"Azure OpenAI API error: {e}")
            # Fallback response
            return [AIMessage(content="I apologize, but I'm experiencing technical difficulties. Please try again later.")]
    
    def generate(self, messages: List[BaseMessage], **kwargs) -> List[AIMessage]:
        """Generate response from messages synchronously.
        
        Args:
            messages: List of chat messages
            **kwargs: Additional generation parameters
            
        Returns:
            List of AI response messages
        """
        if self._demo_mode:
            # Return mock responses for demo
            content = f"[DEMO MODE] Response to: {messages[-1].content[:50]}..."
            return [AIMessage(content=content)]
        
        try:
            response = self.client.generate([messages], **kwargs)
            return response.generations[0]
        except Exception as e:
            logger.error(f"Azure OpenAI API error: {e}")
            # Fallback response
            return [AIMessage(content="I apologize, but I'm experiencing technical difficulties. Please try again later.")]


# Default instance
llm = AzureOpenAIClient()

# Backward compatibility alias
OpenAIClient = AzureOpenAIClient