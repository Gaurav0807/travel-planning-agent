import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from utils.bedrock_client import get_llm
from utils.prompt_loader import load_system_prompt

logger = logging.getLogger(__name__)

llm = get_llm()


def hotel_searcher(state):
    """Search for hotels based on trip details"""

    logger.info("[hotel_searcher] Running...")

    trip = state.get("trip_details")
    if not trip:
        return {"response_user": "Need trip details first"}

    prompt = load_system_prompt("hotel_searcher")

    context = f"""
Trip Details:
- Destination: {trip['destination']}
- Dates: {trip['departure_date']} to {trip['return_date']}
- Budget: ${trip['budget']}
- Travelers: {trip['num_travelers']}
"""

    response = llm.invoke([
        SystemMessage(prompt + context),
        HumanMessage(content=f"Find hotels in {trip['destination']}")
    ])

    hotels = _extract_hotels(response.content)

    logger.info(f"[hotel_searcher] Found {len(hotels)} hotels")

    return {
        "travel_chat": [response],
        "hotel_options": hotels,
        "response_user": response.content,
        "current_step": "planning_itinerary"
    }


def _extract_hotels(content):
    """Extract hotels JSON array from response"""
    try:
        start = content.find('[')
        end = content.rfind(']') + 1
        if start == -1 or end == 0:
            return []
        return json.loads(content[start:end])
    except:
        return []
