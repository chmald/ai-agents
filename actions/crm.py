"""CRM API integration for business development."""

import os
import logging
from typing import Dict, Any, Optional, List
import httpx

logger = logging.getLogger(__name__)


class SalesforceClient:
    """Salesforce API client for CRM operations."""
    
    def __init__(self):
        self.instance_url = os.getenv("SALESFORCE_INSTANCE_URL")
        self.access_token = os.getenv("SALESFORCE_ACCESS_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        } if self.access_token else {}
    
    async def create_lead(
        self, 
        first_name: str, 
        last_name: str, 
        email: str,
        company: str,
        source: str = "AI Agent"
    ) -> Dict[str, Any]:
        """Create a new lead in Salesforce.
        
        Args:
            first_name: Lead first name
            last_name: Lead last name
            email: Lead email
            company: Lead company
            source: Lead source
            
        Returns:
            Created lead data
        """
        if not self.access_token:
            logger.warning("SALESFORCE_ACCESS_TOKEN not set, returning mock response")
            return {
                "id": "00Q1234567890ABCDE",
                "success": True,
                "url": f"{self.instance_url or 'https://demo.salesforce.com'}/00Q1234567890ABCDE"
            }
        
        try:
            lead_data = {
                "FirstName": first_name,
                "LastName": last_name,
                "Email": email,
                "Company": company,
                "LeadSource": source,
                "Status": "Open - Not Contacted"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.instance_url}/services/data/v58.0/sobjects/Lead",
                    headers=self.headers,
                    json=lead_data
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "id": result["id"],
                    "success": result["success"],
                    "url": f"{self.instance_url}/{result['id']}"
                }
        except Exception as e:
            logger.error(f"Failed to create lead: {e}")
            raise
    
    async def create_opportunity(
        self,
        name: str,
        account_id: str,
        stage: str = "Prospecting",
        amount: Optional[float] = None,
        close_date: str = "2024-12-31"
    ) -> Dict[str, Any]:
        """Create a new opportunity.
        
        Args:
            name: Opportunity name
            account_id: Related account ID
            stage: Sales stage
            amount: Opportunity amount
            close_date: Expected close date (YYYY-MM-DD)
            
        Returns:
            Created opportunity data
        """
        if not self.access_token:
            logger.warning("SALESFORCE_ACCESS_TOKEN not set, returning mock response")
            return {
                "id": "0061234567890ABCDE",
                "success": True,
                "url": f"{self.instance_url or 'https://demo.salesforce.com'}/0061234567890ABCDE"
            }
        
        try:
            opp_data = {
                "Name": name,
                "AccountId": account_id,
                "StageName": stage,
                "CloseDate": close_date
            }
            if amount:
                opp_data["Amount"] = amount
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.instance_url}/services/data/v58.0/sobjects/Opportunity",
                    headers=self.headers,
                    json=opp_data
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "id": result["id"],
                    "success": result["success"],
                    "url": f"{self.instance_url}/{result['id']}"
                }
        except Exception as e:
            logger.error(f"Failed to create opportunity: {e}")
            raise
    
    async def search_contacts(self, email: str) -> List[Dict[str, Any]]:
        """Search for contacts by email.
        
        Args:
            email: Email to search for
            
        Returns:
            List of matching contacts
        """
        if not self.access_token:
            logger.warning("SALESFORCE_ACCESS_TOKEN not set, returning mock response")
            return [
                {
                    "Id": "0031234567890ABCDE",
                    "FirstName": "John",
                    "LastName": "Doe",
                    "Email": email,
                    "AccountId": "0011234567890ABCDE"
                }
            ]
        
        try:
            query = f"SELECT Id, FirstName, LastName, Email, AccountId FROM Contact WHERE Email = '{email}'"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.instance_url}/services/data/v58.0/query",
                    headers=self.headers,
                    params={"q": query}
                )
                response.raise_for_status()
                result = response.json()
                
                return result.get("records", [])
        except Exception as e:
            logger.error(f"Failed to search contacts: {e}")
            return []


# Default client instance
crm_client = SalesforceClient()


async def create_lead_from_inquiry(
    name: str, 
    email: str, 
    company: str,
    message: str = ""
) -> str:
    """Create a lead from a customer inquiry.
    
    Args:
        name: Customer name
        email: Customer email
        company: Customer company
        message: Inquiry message
        
    Returns:
        Lead ID
    """
    # Split name into first/last
    name_parts = name.split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""
    
    lead_data = await crm_client.create_lead(
        first_name=first_name,
        last_name=last_name,
        email=email,
        company=company,
        source="Website Inquiry"
    )
    
    return lead_data["id"]


async def find_existing_contact(email: str) -> Optional[Dict[str, Any]]:
    """Find existing contact by email.
    
    Args:
        email: Contact email
        
    Returns:
        Contact data if found, None otherwise
    """
    contacts = await crm_client.search_contacts(email)
    return contacts[0] if contacts else None