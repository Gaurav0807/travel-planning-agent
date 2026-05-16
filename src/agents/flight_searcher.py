import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from utils.bedrock_client import get_llm
from utils.prompt_loader import load_system_prompt

logger = logging.getLogger(__name__)

llm = get_llm()


def flight_searcher(state):
    """Search for flights based on trip details"""

    logger.info("[flight_searcher] Running...")

    trip = state.get("trip_details")
    if not trip:
        return {"response_user": "Need trip details first"}

    prompt = load_system_prompt("flight_searcher")

    # Add trip context to prompt
    context = f"""
        Trip Details:
        - Destination: {trip['destination']}
        - Dates: {trip['departure_date']} to {trip['return_date']}
        - Budget: ${trip['budget']}
        - Travelers: {trip['num_travelers']}
        """

    response = llm.invoke([
        SystemMessage(prompt + context),
        HumanMessage(content=f"Find flights to {trip['destination']}")
    ])

    # Extract flight options from response
    flights = _extract_flights(response.content)

    logger.info(f"[flight_searcher] Found {len(flights)} flights")

    return {
        "travel_chat": [response],
        "flight_options": flights,
        "response_user": response.content,
        "current_step": "searching_hotels"
    }


def _extract_flights(content):
    """Extract flights JSON array from response"""
    try:
        start = content.find('[')
        end = content.rfind(']') + 1
        if start == -1 or end == 0:
            return []
        return json.loads(content[start:end])
    except:
        return []
