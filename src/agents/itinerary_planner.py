import logging
from langchain_core.messages import SystemMessage, HumanMessage
from utils.bedrock_client import get_llm
from utils.prompt_loader import load_system_prompt

logger = logging.getLogger(__name__)

llm = get_llm()


def itinerary_planner(state):
    """Create day-by-day itinerary"""

    logger.info("[itinerary_planner] Running...")

    trip = state.get("trip_details")
    if not trip:
        return {"response_user": "Need trip details first"}

    prompt = load_system_prompt("itinerary_planner")

    context = f"""
        Trip Details:
        - Destination: {trip['destination']}
        - Dates: {trip['departure_date']} to {trip['return_date']}
        - Budget: ${trip['budget']}
        - Travelers: {trip['num_travelers']}
        - Interests: {', '.join(trip.get('interests', []))}
        """

    response = llm.invoke([
        SystemMessage(prompt + context),
        HumanMessage(content=f"Create itinerary for {trip['destination']}")
    ])

    logger.info("[itinerary_planner] Created itinerary")

    return {
        "travel_chat": [response],
        "itinerary_draft": response.content,
        "response_user": response.content,
        "current_step": "finalizing"
    }
