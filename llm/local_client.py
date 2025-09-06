"""Local LLM client for on-premise deployments."""

import os
import logging
from typing import List, Dict, Any, Optional
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_community.llms import Ollama

logger = logging.getLogger(__name__)


class LocalClient:
    """Local LLM client using Ollama or similar local models."""
    
    def __init__(self, model: str = "llama2:70b", base_url: str = "http://localhost:11434"):
        """Initialize local LLM client.
        
        Args:
            model: Local model name
            base_url: Ollama server URL
        """
        self.model = model
        self.base_url = base_url
        
        try:
            self.client = Ollama(
                model=model,
                base_url=base_url,
                temperature=0.7
            )
            self._available = True
        except Exception as e:
            logger.warning(f"Local LLM not available: {e}")
            self._available = False
    
    async def agenerate(self, messages: List[BaseMessage], **kwargs) -> List[AIMessage]:
        """Generate response from messages asynchronously.
        
        Args:
            messages: List of chat messages
            **kwargs: Additional generation parameters
            
        Returns:
            List of AI response messages
        """
        if not self._available:
            return [AIMessage(content="Local LLM service is not available.")]
        
        try:
            # Convert messages to prompt string for Ollama
            prompt = self._messages_to_prompt(messages)
            response = await self.client.agenerate([prompt], **kwargs)
            return [AIMessage(content=response.generations[0][0].text)]
        except Exception as e:
            logger.error(f"Local LLM error: {e}")
            return [AIMessage(content="I apologize, but I'm experiencing technical difficulties. Please try again later.")]
    
    def generate(self, messages: List[BaseMessage], **kwargs) -> List[AIMessage]:
        """Generate response from messages synchronously.
        
        Args:
            messages: List of chat messages
            **kwargs: Additional generation parameters
            
        Returns:
            List of AI response messages
        """
        if not self._available:
            return [AIMessage(content="Local LLM service is not available.")]
        
        try:
            # Convert messages to prompt string for Ollama
            prompt = self._messages_to_prompt(messages)
            response = self.client.generate([prompt], **kwargs)
            return [AIMessage(content=response.generations[0][0].text)]
        except Exception as e:
            logger.error(f"Local LLM error: {e}")
            return [AIMessage(content="I apologize, but I'm experiencing technical difficulties. Please try again later.")]
    
    def _messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """Convert LangChain messages to a prompt string."""
        prompt_parts = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                prompt_parts.append(f"System: {msg.content}")
            elif isinstance(msg, HumanMessage):
                prompt_parts.append(f"Human: {msg.content}")
            elif isinstance(msg, AIMessage):
                prompt_parts.append(f"Assistant: {msg.content}")
        
        return "\n\n".join(prompt_parts) + "\n\nAssistant:"