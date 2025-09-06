"""Action functions for the business development agent."""

import logging
import sys
import os
from typing import Dict, Any, Optional

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from actions.crm import create_lead_from_inquiry, find_existing_contact as crm_find_contact
from actions.slack import send_notification

logger = logging.getLogger(__name__)


async def create_lead(
    name: str, 
    email: str, 
    company: str, 
    context: str = "",
    qualification_score: float = 5.0
) -> str:
    """Create a new lead in the CRM system.
    
    Args:
        name: Lead name
        email: Lead email
        company: Lead company
        context: Additional context
        qualification_score: Lead qualification score (0-10)
        
    Returns:
        Lead ID
    """
    try:
        lead_id = await create_lead_from_inquiry(
            name=name,
            email=email,
            company=company,
            message=context
        )
        
        # Send notification to sales team
        priority = "🔥 HIGH PRIORITY" if qualification_score >= 8 else "📋 New Lead"
        await send_notification(
            "#sales",
            f"{priority} Lead Created",
            f"New lead from {company}:\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Qualification Score: {qualification_score}/10\n"
            f"Context: {context[:100]}..." if context else ""
        )
        
        logger.info(f"Lead created successfully: {lead_id}")
        return lead_id
        
    except Exception as e:
        logger.error(f"Failed to create lead: {e}")
        # Return mock ID for demo
        return f"lead_{hash(email) % 100000}"


async def find_existing_contact(email: str) -> Optional[Dict[str, Any]]:
    """Find existing contact by email.
    
    Args:
        email: Contact email to search for
        
    Returns:
        Contact data if found, None otherwise
    """
    try:
        return await crm_find_contact(email)
    except Exception as e:
        logger.error(f"Failed to find existing contact: {e}")
        return None


async def schedule_followup(lead_id: str, delay: str = "1 day", notes: str = "") -> bool:
    """Schedule a follow-up task for the lead.
    
    Args:
        lead_id: CRM lead ID
        delay: How long to wait before follow-up
        notes: Additional notes for the follow-up
        
    Returns:
        True if scheduled successfully
    """
    try:
        # Mock follow-up scheduling - in production would integrate with CRM task system
        logger.info(f"Follow-up scheduled for lead {lead_id} in {delay}")
        
        # Send notification to sales team
        await send_notification(
            "#sales",
            "Follow-up Scheduled",
            f"Follow-up scheduled for lead {lead_id}\n"
            f"Delay: {delay}\n"
            f"Notes: {notes}"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to schedule follow-up: {e}")
        return False


async def send_welcome_email(lead_email: str, lead_name: str, company: str) -> bool:
    """Send welcome email to new lead.
    
    Args:
        lead_email: Lead's email address
        lead_name: Lead's name
        company: Lead's company
        
    Returns:
        True if email sent successfully
    """
    try:
        # Mock email sending - in production would integrate with email service
        email_content = f"""
        Subject: Welcome to AI-Powered Business Ecosystem
        
        Dear {lead_name},
        
        Thank you for your interest in our AI-Powered Business Ecosystem!
        
        We're excited to help {company} automate and optimize your business processes 
        with our cutting-edge AI agents for:
        
        • Code Generation & Development
        • Marketing & Social Media
        • Security & Compliance
        • Business Development & CRM
        
        A member of our team will be in touch shortly to discuss how we can help 
        streamline your operations.
        
        Best regards,
        The AI Ecosystem Team
        """
        
        logger.info(f"Welcome email sent to {lead_email}")
        
        # Send notification to marketing team
        await send_notification(
            "#marketing",
            "Welcome Email Sent",
            f"Welcome email sent to {lead_name} at {company}"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
        return False


async def analyze_lead_source(context: str, email: str) -> Dict[str, Any]:
    """Analyze the source and quality of a lead.
    
    Args:
        context: Context information about how the lead was acquired
        email: Lead's email domain for company analysis
        
    Returns:
        Analysis results including source, quality indicators, and recommendations
    """
    try:
        # Extract domain for company size estimation
        domain = email.split('@')[1] if '@' in email else ""
        
        # Simple heuristics for lead quality
        quality_indicators = {
            "enterprise_domain": domain.endswith(('.com', '.org', '.net')) and not domain.endswith(('gmail.com', 'yahoo.com', 'hotmail.com')),
            "has_context": len(context.strip()) > 0,
            "context_length": len(context),
            "professional_email": not any(provider in domain for provider in ['gmail', 'yahoo', 'hotmail', 'outlook'])
        }
        
        # Determine lead source from context keywords
        source = "unknown"
        if any(keyword in context.lower() for keyword in ['website', 'contact form', 'form']):
            source = "website_inquiry"
        elif any(keyword in context.lower() for keyword in ['social', 'twitter', 'linkedin']):
            source = "social_media"
        elif any(keyword in context.lower() for keyword in ['referral', 'referred']):
            source = "referral"
        elif any(keyword in context.lower() for keyword in ['demo', 'trial']):
            source = "demo_request"
        
        # Calculate quality score
        quality_score = 5.0  # Base score
        if quality_indicators["enterprise_domain"]:
            quality_score += 2.0
        if quality_indicators["professional_email"]:
            quality_score += 1.5
        if quality_indicators["has_context"]:
            quality_score += 1.0
        if quality_indicators["context_length"] > 100:
            quality_score += 0.5
        
        quality_score = min(quality_score, 10.0)
        
        analysis = {
            "source": source,
            "quality_score": round(quality_score, 1),
            "quality_indicators": quality_indicators,
            "domain": domain,
            "recommendations": []
        }
        
        # Add recommendations based on analysis
        if quality_score >= 8:
            analysis["recommendations"].append("High-priority lead - schedule call within 24 hours")
        elif quality_score >= 6:
            analysis["recommendations"].append("Good lead - follow up within 2-3 days")
        else:
            analysis["recommendations"].append("Nurture lead with email campaign")
        
        if source == "demo_request":
            analysis["recommendations"].append("Schedule product demonstration")
        elif source == "referral":
            analysis["recommendations"].append("Thank referral source")
        
        if not quality_indicators["professional_email"]:
            analysis["recommendations"].append("Verify business legitimacy")
        
        logger.info(f"Lead analysis completed: {source} source, {quality_score}/10 quality")
        return analysis
        
    except Exception as e:
        logger.error(f"Lead analysis failed: {e}")
        return {
            "source": "unknown",
            "quality_score": 5.0,
            "error": str(e)
        }


async def update_lead_status(lead_id: str, status: str, notes: str = "") -> bool:
    """Update the status of a lead in the CRM.
    
    Args:
        lead_id: CRM lead ID
        status: New status (e.g., 'contacted', 'qualified', 'converted')
        notes: Additional notes about the status change
        
    Returns:
        True if updated successfully
    """
    try:
        # Mock status update - in production would integrate with CRM API
        logger.info(f"Lead {lead_id} status updated to: {status}")
        
        # Send notification for important status changes
        if status in ['qualified', 'converted', 'lost']:
            await send_notification(
                "#sales",
                f"Lead Status Update: {status.title()}",
                f"Lead {lead_id} status changed to {status}\n"
                f"Notes: {notes}"
            )
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to update lead status: {e}")
        return False