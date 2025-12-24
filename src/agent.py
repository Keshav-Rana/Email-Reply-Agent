from dotenv import load_dotenv
import uuid
from typing import Literal, TypedDict
from IPython.display import Image, display
from langchain_openai import ChatOpenAI
from langgraph.types import Command, interrupt
from langgraph.graph import END, START, StateGraph

load_dotenv()

class TicketClassification(TypedDict):
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str

class TicketAgentState(TypedDict):
    email_content: str
    sender_email: str
    email_id: str

    # classification
    classification: TicketClassification | None

    # raw search results
    search_results: list[str] | None
    customer_history: dict | None

    # generated content
    draft_response: str | None

def read_ticket(state: TicketAgentState) -> TicketAgentState:
    """Fetch and process ticket content"""
    pass    

llm = ChatOpenAI(model="gpt-5-mini")

def classify_intent(state: TicketAgentState) -> TicketAgentState:
    """Use LLM to classify ticket intent and urgency"""
    pass

