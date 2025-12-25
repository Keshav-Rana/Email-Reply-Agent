from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn
from src.zendesk_webhook_handler import ZendeskWebhookHandler
from src.models import WebhookResponse
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Zendesk Email Reply Agent",
              description="Backend server for integrating with Zendesk and automating email replies",
              version="1.0.0")

# initialise webhook handler
webhook_handler = ZendeskWebhookHandler()

@app.get("/")
def read_root():
    return {
        "message": "Zendesk Email Reply Agent API",
        "status": "running",
        "endpoints": {
            "webhook": "/zendesk-webhook",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "zendesk-webhook-handler"}

@app.post("/zendesk-webhook", response_model=WebhookResponse)
async def receive_zendesk_webhook(request: Request):
    """
    Endpoint to receive Zendesk webhook notifications

    Expected payload from Zendesk trigger:
    {
        "ticket_id": "{{ticket.id}}",
        "subject": "{{ticket.title}}",
        "description": "{{ticket.description}}",
        "status": "{{ticket.status}}",
        "priority": "{{ticket.priority}}",
        "requester_email": "{{ticket.requester.email}}",
        "requester_name": "{{ticket.requester.name}}",
        "created_at": "{{ticket.created_at}}",
        "tags": "{{ticket.tags}}",
        "channel": "{{ticket.via}}"
    }
    """
    try:
        # get raw JSON data
        raw_data = await request.json()
        logger.info(f"Received webhook data: {raw_data}")

        # validate and parse the payload
        ticket_payload = webhook_handler.validate_webhook_data(raw_data)

        # process the ticket
        response = webhook_handler.process_ticket_created(ticket_payload)

        # return response
        if response.success:
            return response
        else:
            raise HTTPException(status_code=500, detail=response.message)
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(ve)}")
    
    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)