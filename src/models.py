from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ZendeskTicketPayload(BaseModel):
    """Model for Zendesk webhook ticket payload"""
    ticket_id: str = Field(..., description="Zendesk ticket ID")
    subject: str = Field(..., description="Ticket subject/title")
    description: str = Field(..., description="Ticket description/body")
    status: str = Field(..., description="Ticket status (new, open, pending, solved, closed)")
    priority: Optional[str] = Field(None, description="Ticket priority (low, normal, high, urgent)")
    requester_email: str = Field(..., description="Email of the ticket requester")
    requester_name: str = Field(..., description="Name of the ticket requester")
    created_at: str = Field(..., description="Ticket creation timestamp")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    channel: Optional[str] = Field(None, description="Channel through which ticket was created")

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": "12345",
                "subject": "Need help with product",
                "description": "I am having issues with...",
                "status": "new",
                "priority": "normal",
                "requester_email": "customer@example.com",
                "requester_name": "John Doe",
                "created_at": "2025-12-25T10:00:00Z",
                "tags": "support,urgent",
                "channel": "email"
            }
        }

class WebhookResponse(BaseModel):
    """Standard response model for webhook"""
    success: bool
    message: str
    ticket_id: Optional[str] = None
    processed_at: Optional[str] = None