import os
import base64
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()


class ZendeskClient:
    """
    Zendesk API client for interacting with Zendesk Support tickets.
    Uses API Token authentication for simplicity in POC environments.
    """

    def __init__(self, subdomain: Optional[str] = None, email: Optional[str] = None, api_token: Optional[str] = None):
        """
        initialise zendesk client with API token authentication.

        Args:
            subdomain, email, api_token
        """
        self.subdomain = subdomain
        self.email = email
        self.api_token = api_token

        # validate required configuration
        if not all([self.subdomain, self.email, self.api_token]):
            raise ValueError(
                "Missing required Zendesk configuration. ",
                "Provide subdomain, email, and api_token either as parameters "
                "or set ZENDESK_SUBDOMAIN, ZENDESK_EMAIL, and ZENDESK_API_TOKEN "
                "environment variables."
            ) 
        
        self.base_url = f"https://{self.subdomain}.zendesk.com/api/v2"
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with API token auth.

        Returns:
            Configured requests.Session object
        """
        session = requests.Session()

        # format: email/token:api_token
        credentials = f"{self.email}/token:{self.api_token}"

        # Base64 encode for basic auth
        encoded_credentials=  base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        # Set authentication header
        session.headers.update({
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

        return session
    
    def get_ticket(self, ticket_id: int) -> Dict[str, Any]:
        """
        Retrieve a specific ticket by ID.

        GET /api/v2/tickets/{ticket_id}

        Args:
            ticket_id: The ID of the ticket to retrieve

        Returns:
            Dictionary containing the ticket data

        Raises:
            requests.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/tickets/{ticket_id}.json"

        response = self.session.get(url)
        response.raise_for_status()

        return response.json()
    
    def update_ticket(
            self,
            ticket_id: int,
            ticket_data: Dict[str, Any],
            safe_update: bool = False,
            updated_stamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a specific ticket by ID.

        PUT /api/v2/tickets/{ticket_id}

        All properties in ticket_data are optional. Only the properties you
        include will be updated.

        Args:
            ticket_id: The ID of the ticket to update
            ticket_data: Dictionary of ticket properties to update.
                        Common properties include:
                        - status: "new", "open", "pending", "hold", "solved", "closed"
                        - priority: "low", "normal", "high", "urgent"
                        - subject: Ticket subject line
                        - comment: Dict with "body" and optional "public" (bool)
                        - assignee_id: ID of the agent to assign
                        - tags: List of tags
            safe_update: If True, prevents update conflicts using updated_stamp
            updated_stamp: The last known updated_at value (for safe updates)

        Returns:
            Dictionary containing the updated ticket data and audit information

        Raises:
            requests.HTTPError: If the API request fails

        Example:
            client.update_ticket(
                ticket_id=123,
                ticket_data={
                    "status": "open",
                    "priority": "high",
                    "comment": {
                        "body": "Working on this issue now",
                        "public": False
                    }
                }
            )
        """
        url = f"{self.base_url}/tickets/{ticket_id}.json"

        payload = {"ticket": ticket_data}

        # Add safe update parameters if requested
        params = {}
        if safe_update and updated_stamp:
            params["safe_update"] = "true"
            params["updated_stamp"] = updated_stamp

        response = self.session.put(url, json=payload, params=params)
        response.raise_for_status()

        return response.json()
    
    def close(self):
        """Close the HTTP session."""
        if self.session:
            self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()