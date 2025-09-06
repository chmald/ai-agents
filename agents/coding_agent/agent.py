"""Coding agent implementation using LangGraph."""

import logging
from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain.schema import HumanMessage, SystemMessage
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from llm.openai_client import llm
from .actions import analyze_code, generate_code, create_merge_request

logger = logging.getLogger(__name__)


class CodingState(TypedDict):
    """State for the coding agent workflow."""
    repo: str
    branch: str
    requirements: str
    analysis: Dict[str, Any]
    generated_code: List[Dict[str, str]]
    merge_request_url: str
    error: str


class CodingAgent:
    """AI agent for automated code generation and repository management."""
    
    def __init__(self):
        """Initialize the coding agent with StateGraph workflow."""
        self.graph = StateGraph(CodingState)
        self._build_graph()
        self.workflow = self.graph.compile()
    
    def _build_graph(self):
        """Build the StateGraph workflow."""
        
        async def analyze_requirements(state: CodingState) -> CodingState:
            """Analyze code requirements and repository structure."""
            try:
                logger.info(f"Analyzing requirements for repo: {state['repo']}")
                
                # Use LLM to analyze requirements
                system_prompt = (
                    "You are a senior software engineer analyzing code requirements. "
                    "Break down the requirements into specific implementation tasks."
                )
                user_prompt = f"Requirements: {state['requirements']}"
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]
                
                response = await llm.agenerate(messages)
                analysis_text = response[0].content
                
                # Perform repository analysis
                analysis = await analyze_code(state['repo'], state['branch'])
                analysis['llm_analysis'] = analysis_text
                
                return {**state, "analysis": analysis}
                
            except Exception as e:
                logger.error(f"Failed to analyze requirements: {e}")
                return {**state, "error": str(e)}
        
        async def generate_implementation(state: CodingState) -> CodingState:
            """Generate code implementation based on analysis."""
            try:
                logger.info("Generating code implementation")
                
                analysis = state['analysis']
                
                # Use LLM to generate code
                system_prompt = (
                    "You are an expert programmer. Generate clean, well-documented code "
                    "that implements the given requirements. Follow best practices and "
                    "include error handling."
                )
                
                context_prompt = f"""
                Repository: {state['repo']}
                Branch: {state['branch']}
                Requirements: {state['requirements']}
                Analysis: {analysis.get('llm_analysis', '')}
                
                Generate code files that implement these requirements.
                Respond with a JSON-like format showing file paths and content.
                """
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=context_prompt)
                ]
                
                response = await llm.agenerate(messages)
                generated_text = response[0].content
                
                # Generate actual code files
                generated_code = await generate_code(state['requirements'], analysis)
                
                # Add LLM-generated insights to the code
                generated_code.append({
                    "file_path": "AI_IMPLEMENTATION_NOTES.md",
                    "content": f"# AI Implementation Notes\n\n{generated_text}",
                    "action": "create"
                })
                
                return {**state, "generated_code": generated_code}
                
            except Exception as e:
                logger.error(f"Failed to generate code: {e}")
                return {**state, "error": str(e)}
        
        async def create_pull_request(state: CodingState) -> CodingState:
            """Create a pull request with the generated code."""
            try:
                logger.info("Creating merge request")
                
                generated_code = state['generated_code']
                
                if not generated_code:
                    return {**state, "error": "No code generated to commit"}
                
                # Create merge request
                title = f"AI-Generated Implementation: {state['requirements'][:50]}..."
                description = f"""
# AI-Generated Code Implementation

## Requirements
{state['requirements']}

## Analysis Summary
{state['analysis'].get('summary', 'Code analysis completed')}

## Generated Files
{', '.join([file['file_path'] for file in generated_code])}

This code was automatically generated by the AI Coding Agent.
Please review carefully before merging.
                """
                
                mr_url = await create_merge_request(
                    repo=state['repo'],
                    branch=state['branch'],
                    title=title,
                    description=description,
                    files=generated_code
                )
                
                logger.info(f"Created merge request: {mr_url}")
                return {**state, "merge_request_url": mr_url}
                
            except Exception as e:
                logger.error(f"Failed to create merge request: {e}")
                return {**state, "error": str(e)}
        
        # Add nodes to the graph
        self.graph.add_node("analyze", analyze_requirements)
        self.graph.add_node("generate", generate_implementation)
        self.graph.add_node("create_pr", create_pull_request)
        
        # Add edges
        self.graph.add_edge(START, "analyze")
        self.graph.add_edge("analyze", "generate")
        self.graph.add_edge("generate", "create_pr")
        self.graph.add_edge("create_pr", END)
    
    async def process(self, repo: str, branch: str, requirements: str) -> Dict[str, Any]:
        """Process coding requirements and create a merge request.
        
        Args:
            repo: Repository name (e.g., "owner/repo")
            branch: Target branch name
            requirements: Code requirements description
            
        Returns:
            Result dictionary with merge request URL or error
        """
        initial_state = CodingState(
            repo=repo,
            branch=branch,
            requirements=requirements,
            analysis={},
            generated_code=[],
            merge_request_url="",
            error=""
        )
        
        try:
            final_state = await self.workflow.ainvoke(initial_state)
            
            if final_state.get("error"):
                return {"success": False, "error": final_state["error"]}
            
            return {
                "success": True,
                "merge_request_url": final_state["merge_request_url"],
                "files_created": len(final_state["generated_code"]),
                "analysis": final_state["analysis"]
            }
            
        except Exception as e:
            logger.error(f"Coding agent workflow failed: {e}")
            return {"success": False, "error": str(e)}