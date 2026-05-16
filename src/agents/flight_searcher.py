"""
FLIGHT_SEARCHER.PY - Second agent

Suggests flight options based on trip details.
"""

import json
from langchain_core.messages import SystemMessage, HumanMessage
from utils.bedrock_client import get_llm
from utils.prompt_loader import load_system_prompt

llm = get_llm()


def flight_searcher(state):
    """Find flights for the trip"""

    trip = state.get("trip_details")
    if not trip:
        return {"response_user": "Need trip details first"}

    # Load instructions
    prompt = load_system_prompt("flight_searcher")

    # Add trip info
    context = f"""
        Trip Details:
        - Destination: {trip['destination']}
        - Dates: {trip['departure_date']} to {trip['return_date']}
        - Budget: ${trip['budget']}
        - Travelers: {trip['num_travelers']}
        """

    # Ask Claude for flights
    response = llm.invoke([
        SystemMessage(prompt + context),
        HumanMessage(content=f"Find flights to {trip['destination']}")
    ])

    # Get flights from response
    flights = extract_flights(response.content)

    return {
        "travel_chat": [response],
        "flight_options": flights,
        "response_user": response.content,
        "current_step": "searching_hotels"
    }


def extract_flights(content):
    """Get flights JSON from response"""

    try:
        start = content.find('[')
        end = content.rfind(']') + 1
        if start == -1 or end == 0:
            return []
        return json.loads(content[start:end])
    except:
        return []
