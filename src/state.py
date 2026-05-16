import operator
from typing import Annotated, Literal, Optional, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class TripDetails(TypedDict):
    #Trip detail
    destination: str
    departure_date: str
    return_date: str
    budget: float
    num_travelers: int
    interests: list[str]

class UserProfile(TypedDict):
    #kind of Episodic Memory
    past_trips: list[dict]
    preferences: dict
    lessons_learned: list[dict]


class TravelState(TypedDict):
      """Central state for travel planning workflow
      
      WORKING MEMORY:
      - travel_chat: Current conversation history
      - trip_details: Trip being planned
      - flight_options, hotel_options: Fetched results
      
      EPISODIC MEMORY:
      - user_profile: Learned from past sessions
      
      SEMANTIC MEMORY:
      - retrieved_guides, retrieved_reviews: From Knowledge Base
      """

      # ========== WORKING MEMORY ==========
      # Current conversation
      travel_chat: Annotated[Sequence[BaseMessage], add_messages]

      # Trip being planned
      trip_details: Optional[TripDetails]

      # Current step in workflow
      current_step: Literal[
          "gathering_info",
          "searching_flights",
          "searching_hotels",
          "planning_itinerary",
          "finalizing"
      ]

      # Data fetched in this session
      flight_options: Annotated[list[dict], operator.add]
      hotel_options: Annotated[list[dict], operator.add]
      attractions: Annotated[list[dict], operator.add]
      itinerary_draft: Optional[str]
      total_cost: Optional[float]

      # ========== EPISODIC MEMORY ==========
      # Persistent user profile (saved to AgentCore)
      user_profile: Optional[UserProfile]

      # ========== SEMANTIC MEMORY ==========
      # Retrieved from Knowledge Base
      retrieved_guides: Optional[str]
      retrieved_reviews: Optional[str]

      # ========== CONTROL FLOW ==========
      thread_id: str
      current_agent: Optional[str]
      response_user: Optional[str]
