"""Security agent implementation using LangGraph."""

import logging
from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain.schema import HumanMessage, SystemMessage
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from llm.openai_client import llm
from .actions import scan_vulnerabilities, check_compliance, generate_security_report

logger = logging.getLogger(__name__)


class SecurityState(TypedDict):
    """State for the security agent workflow."""
    target: str
    scan_type: str
    vulnerabilities: List[Dict[str, Any]]
    compliance_status: Dict[str, Any]
    security_report: str
    risk_score: float
    recommendations: List[str]
    error: str


class SecurityAgent:
    """AI agent for security analysis and compliance monitoring."""
    
    def __init__(self):
        """Initialize the security agent with StateGraph workflow."""
        self.graph = StateGraph(SecurityState)
        self._build_graph()
        self.workflow = self.graph.compile()
    
    def _build_graph(self):
        """Build the StateGraph workflow."""
        
        async def perform_security_scan(state: SecurityState) -> SecurityState:
            """Perform security vulnerability scanning."""
            try:
                logger.info(f"Starting security scan for: {state['target']}")
                
                target = state["target"]
                scan_type = state["scan_type"]
                
                # Use LLM to analyze security context
                system_prompt = (
                    "You are a cybersecurity expert analyzing potential security vulnerabilities. "
                    "Identify common security issues and provide specific remediation guidance."
                )
                
                user_prompt = f"""
                Analyze the security posture for: {target}
                Scan type: {scan_type}
                
                Focus on:
                1. Common vulnerabilities (OWASP Top 10)
                2. Configuration issues
                3. Access control problems
                4. Data protection concerns
                
                Provide specific findings and remediation steps.
                """
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]
                
                response = await llm.agenerate(messages)
                llm_analysis = response[0].content
                
                # Perform actual vulnerability scan
                vulnerabilities = await scan_vulnerabilities(target, scan_type)
                
                # Add LLM insights to vulnerabilities
                for vuln in vulnerabilities:
                    vuln["llm_analysis"] = llm_analysis[:200] + "..."
                
                logger.info(f"Found {len(vulnerabilities)} potential vulnerabilities")
                return {**state, "vulnerabilities": vulnerabilities}
                
            except Exception as e:
                logger.error(f"Security scan failed: {e}")
                return {**state, "error": str(e)}
        
        async def check_compliance_standards(state: SecurityState) -> SecurityState:
            """Check compliance against security standards."""
            try:
                logger.info("Checking compliance standards")
                
                target = state["target"]
                vulnerabilities = state["vulnerabilities"]
                
                # Check compliance status
                compliance_status = await check_compliance(target, vulnerabilities)
                
                logger.info(f"Compliance check completed: {compliance_status.get('overall_score', 0)}% compliant")
                return {**state, "compliance_status": compliance_status}
                
            except Exception as e:
                logger.error(f"Compliance check failed: {e}")
                return {**state, "error": str(e)}
        
        async def generate_report(state: SecurityState) -> SecurityState:
            """Generate comprehensive security report."""
            try:
                logger.info("Generating security report")
                
                vulnerabilities = state["vulnerabilities"]
                compliance_status = state["compliance_status"]
                
                # Use LLM to generate executive summary
                system_prompt = (
                    "You are a security analyst writing an executive summary for a security assessment. "
                    "Create a concise, business-focused summary that highlights key risks and recommendations."
                )
                
                findings_summary = f"""
                Target: {state['target']}
                Vulnerabilities found: {len(vulnerabilities)}
                Compliance score: {compliance_status.get('overall_score', 0)}%
                
                Top vulnerabilities: {', '.join([v.get('title', 'Unknown') for v in vulnerabilities[:3]])}
                """
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f"Create an executive summary for these security findings: {findings_summary}")
                ]
                
                response = await llm.agenerate(messages)
                executive_summary = response[0].content
                
                # Generate detailed report
                security_report = await generate_security_report(
                    target=state["target"],
                    vulnerabilities=vulnerabilities,
                    compliance_status=compliance_status,
                    executive_summary=executive_summary
                )
                
                # Calculate risk score
                high_risk_count = len([v for v in vulnerabilities if v.get("severity") == "high"])
                medium_risk_count = len([v for v in vulnerabilities if v.get("severity") == "medium"])
                compliance_score = compliance_status.get("overall_score", 100) / 100
                
                risk_score = min(
                    (high_risk_count * 0.3 + medium_risk_count * 0.1) * (1 - compliance_score) * 10,
                    10.0
                )
                
                # Generate recommendations
                recommendations = []
                if high_risk_count > 0:
                    recommendations.append("Immediately address high-severity vulnerabilities")
                if compliance_score < 0.8:
                    recommendations.append("Improve compliance posture to meet industry standards")
                if len(vulnerabilities) > 10:
                    recommendations.append("Implement automated security scanning in CI/CD pipeline")
                
                recommendations.extend([
                    "Conduct regular security training for development team",
                    "Implement security monitoring and alerting",
                    "Schedule quarterly security assessments"
                ])
                
                logger.info(f"Security report generated. Risk score: {risk_score}")
                return {
                    **state, 
                    "security_report": security_report,
                    "risk_score": round(risk_score, 2),
                    "recommendations": recommendations
                }
                
            except Exception as e:
                logger.error(f"Report generation failed: {e}")
                return {**state, "error": str(e)}
        
        # Add nodes to the graph
        self.graph.add_node("scan", perform_security_scan)
        self.graph.add_node("compliance", check_compliance_standards)
        self.graph.add_node("report", generate_report)
        
        # Add edges
        self.graph.add_edge(START, "scan")
        self.graph.add_edge("scan", "compliance")
        self.graph.add_edge("compliance", "report")
        self.graph.add_edge("report", END)
    
    async def process(self, target: str, scan_type: str = "comprehensive") -> Dict[str, Any]:
        """Process security analysis for a target system.
        
        Args:
            target: Target system/URL/repository to analyze
            scan_type: Type of scan to perform
            
        Returns:
            Result dictionary with security findings and recommendations
        """
        initial_state = SecurityState(
            target=target,
            scan_type=scan_type,
            vulnerabilities=[],
            compliance_status={},
            security_report="",
            risk_score=0.0,
            recommendations=[],
            error=""
        )
        
        try:
            final_state = await self.workflow.ainvoke(initial_state)
            
            if final_state.get("error"):
                return {"success": False, "error": final_state["error"]}
            
            return {
                "success": True,
                "target": final_state["target"],
                "vulnerabilities_found": len(final_state["vulnerabilities"]),
                "risk_score": final_state["risk_score"],
                "compliance_score": final_state["compliance_status"].get("overall_score", 0),
                "security_report": final_state["security_report"],
                "recommendations": final_state["recommendations"],
                "detailed_findings": final_state["vulnerabilities"]
            }
            
        except Exception as e:
            logger.error(f"Security agent workflow failed: {e}")
            return {"success": False, "error": str(e)}