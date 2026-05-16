import operator
from typing import Annotated, Optional, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class TravelState(dict):
    """All the data for one conversation"""

    # Conversation ID
    thread_id: str

    # Chat messages
    travel_chat: Annotated[Sequence[BaseMessage], add_messages]

    # Trip info from user
    trip_details: Optional[dict]

    # Current step
    current_step: str

    # Search results
    flight_options: Annotated[list, operator.add]
    hotel_options: Annotated[list, operator.add]
    attractions: Annotated[list, operator.add]

    # Final plan
    itinerary_draft: Optional[str]

    # User's saved preferences
    user_profile: Optional[dict]

    # Bot's response to show user
    response_user: Optional[str]
