"""Business development agent implementation using LangGraph."""

import logging
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain.schema import HumanMessage, SystemMessage
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from llm.openai_client import llm
from .actions import create_lead, find_existing_contact, schedule_followup, send_welcome_email

logger = logging.getLogger(__name__)


class BizDevState(TypedDict):
    """State for the business development agent workflow."""
    lead_name: str
    lead_email: str
    lead_company: str
    context: str
    existing_contact: Dict[str, Any]
    lead_id: str
    followup_scheduled: bool
    welcome_sent: bool
    qualification_score: float
    recommendations: list
    error: str


class BizDevAgent:
    """AI agent for business development and lead management."""
    
    def __init__(self):
        """Initialize the business development agent with StateGraph workflow."""
        self.graph = StateGraph(BizDevState)
        self._build_graph()
        self.workflow = self.graph.compile()
    
    def _build_graph(self):
        """Build the StateGraph workflow."""
        
        async def analyze_lead(state: BizDevState) -> BizDevState:
            """Analyze and qualify the lead."""
            try:
                logger.info(f"Analyzing lead: {state['lead_name']} from {state['lead_company']}")
                
                # Use LLM to analyze lead quality and potential
                system_prompt = (
                    "You are a business development expert analyzing sales leads. "
                    "Assess the lead quality, identify key opportunities, and provide "
                    "qualification insights based on the available information."
                )
                
                lead_info = f"""
                Name: {state['lead_name']}
                Email: {state['lead_email']}
                Company: {state['lead_company']}
                Context: {state['context']}
                """
                
                user_prompt = f"""
                Analyze this lead and provide:
                1. Lead qualification score (0-10)
                2. Key opportunities and pain points
                3. Recommended next steps
                4. Timeline estimate for potential deal
                
                Lead information: {lead_info}
                """
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]
                
                response = await llm.agenerate(messages)
                analysis = response[0].content
                
                # Extract qualification score from LLM response
                # Simple heuristic - in production would use more sophisticated parsing
                qualification_score = 7.5  # Default score
                if "score" in analysis.lower():
                    try:
                        # Look for patterns like "score: 8" or "8/10"
                        import re
                        score_match = re.search(r'score[:\s]*(\d+(?:\.\d+)?)', analysis.lower())
                        if score_match:
                            qualification_score = float(score_match.group(1))
                            if qualification_score > 10:
                                qualification_score = qualification_score / 10
                    except:
                        pass
                
                recommendations = [
                    "Schedule discovery call within 48 hours",
                    "Send relevant case studies and product information",
                    "Connect with decision makers",
                    "Identify budget and timeline requirements"
                ]
                
                logger.info(f"Lead qualification completed: {qualification_score}/10")
                return {
                    **state, 
                    "qualification_score": qualification_score,
                    "recommendations": recommendations
                }
                
            except Exception as e:
                logger.error(f"Lead analysis failed: {e}")
                return {**state, "error": str(e)}
        
        async def check_existing_contact(state: BizDevState) -> BizDevState:
            """Check if contact already exists in CRM."""
            try:
                logger.info(f"Checking for existing contact: {state['lead_email']}")
                
                existing_contact = await find_existing_contact(state['lead_email'])
                
                if existing_contact:
                    logger.info(f"Found existing contact: {existing_contact.get('Id', 'Unknown')}")
                else:
                    logger.info("No existing contact found")
                
                return {**state, "existing_contact": existing_contact or {}}
                
            except Exception as e:
                logger.error(f"Contact lookup failed: {e}")
                return {**state, "error": str(e)}
        
        async def create_crm_record(state: BizDevState) -> BizDevState:
            """Create or update CRM record."""
            try:
                existing_contact = state["existing_contact"]
                
                if existing_contact:
                    logger.info("Updating existing contact record")
                    # In a real implementation, would update the existing record
                    lead_id = existing_contact.get("Id", "")
                else:
                    logger.info("Creating new lead record")
                    lead_id = await create_lead(
                        name=state["lead_name"],
                        email=state["lead_email"],
                        company=state["lead_company"],
                        context=state["context"],
                        qualification_score=state["qualification_score"]
                    )
                
                logger.info(f"CRM record processed: {lead_id}")
                return {**state, "lead_id": lead_id}
                
            except Exception as e:
                logger.error(f"CRM record creation failed: {e}")
                return {**state, "error": str(e)}
        
        async def setup_followup_actions(state: BizDevState) -> BizDevState:
            """Setup follow-up actions and communications."""
            try:
                logger.info("Setting up follow-up actions")
                
                lead_id = state["lead_id"]
                qualification_score = state["qualification_score"]
                
                # Schedule follow-up based on qualification score
                followup_delay = "1 day" if qualification_score >= 8 else "3 days"
                followup_scheduled = await schedule_followup(
                    lead_id=lead_id,
                    delay=followup_delay,
                    notes=f"High-priority lead (score: {qualification_score})" if qualification_score >= 8 else "Standard follow-up"
                )
                
                # Send welcome email
                welcome_sent = await send_welcome_email(
                    lead_email=state["lead_email"],
                    lead_name=state["lead_name"],
                    company=state["lead_company"]
                )
                
                logger.info(f"Follow-up actions completed. Follow-up scheduled: {followup_scheduled}, Welcome sent: {welcome_sent}")
                return {
                    **state, 
                    "followup_scheduled": followup_scheduled,
                    "welcome_sent": welcome_sent
                }
                
            except Exception as e:
                logger.error(f"Follow-up setup failed: {e}")
                return {**state, "error": str(e)}
        
        # Add nodes to the graph
        self.graph.add_node("analyze", analyze_lead)
        self.graph.add_node("check_contact", check_existing_contact)
        self.graph.add_node("create_record", create_crm_record)
        self.graph.add_node("setup_followup", setup_followup_actions)
        
        # Add edges
        self.graph.add_edge(START, "analyze")
        self.graph.add_edge("analyze", "check_contact")
        self.graph.add_edge("check_contact", "create_record")
        self.graph.add_edge("create_record", "setup_followup")
        self.graph.add_edge("setup_followup", END)
    
    async def process(self, lead_name: str, lead_email: str, lead_company: str, context: str = "") -> Dict[str, Any]:
        """Process a new lead through the business development workflow.
        
        Args:
            lead_name: Lead's name
            lead_email: Lead's email
            lead_company: Lead's company
            context: Additional context about the lead
            
        Returns:
            Result dictionary with lead processing results
        """
        initial_state = BizDevState(
            lead_name=lead_name,
            lead_email=lead_email,
            lead_company=lead_company,
            context=context,
            existing_contact={},
            lead_id="",
            followup_scheduled=False,
            welcome_sent=False,
            qualification_score=0.0,
            recommendations=[],
            error=""
        )
        
        try:
            final_state = await self.workflow.ainvoke(initial_state)
            
            if final_state.get("error"):
                return {"success": False, "error": final_state["error"]}
            
            return {
                "success": True,
                "lead_id": final_state["lead_id"],
                "qualification_score": final_state["qualification_score"],
                "existing_contact": bool(final_state["existing_contact"]),
                "followup_scheduled": final_state["followup_scheduled"],
                "welcome_sent": final_state["welcome_sent"],
                "recommendations": final_state["recommendations"]
            }
            
        except Exception as e:
            logger.error(f"BizDev agent workflow failed: {e}")
            return {"success": False, "error": str(e)}