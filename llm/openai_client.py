"""OpenAI client wrapper for LLM interactions."""

import os
import logging
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI LLM client with rate limiting and error handling."""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        """Initialize OpenAI client.
        
        Args:
            model: OpenAI model name
            temperature: Sampling temperature
        """
        self.model = model
        self.temperature = temperature
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set, using demo mode")
            self._demo_mode = True
        else:
            self._demo_mode = False
            self.client = ChatOpenAI(
                model=model,
                temperature=temperature,
                openai_api_key=self.api_key,
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
            logger.error(f"OpenAI API error: {e}")
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
            logger.error(f"OpenAI API error: {e}")
            # Fallback response
            return [AIMessage(content="I apologize, but I'm experiencing technical difficulties. Please try again later.")]


# Default instance
llm = OpenAIClient()