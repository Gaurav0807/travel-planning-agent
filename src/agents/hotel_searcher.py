
import json
from langchain_core.messages import SystemMessage, HumanMessage
from utils.bedrock_client import get_llm
from utils.prompt_loader import load_system_prompt

llm = get_llm()


def hotel_searcher(state):
    """Find hotels for the trip"""

    trip = state.get("trip_details")
    if not trip:
        return {"response_user": "Need trip details first"}

    # Load instructions
    prompt = load_system_prompt("hotel_searcher")

    # Add trip info
    context = f"""
        Trip Details:
        - Destination: {trip['destination']}
        - Dates: {trip['departure_date']} to {trip['return_date']}
        - Budget: ${trip['budget']}
        - Travelers: {trip['num_travelers']}
        """

    # Ask Claude for hotels
    response = llm.invoke([
        SystemMessage(prompt + context),
        HumanMessage(content=f"Find hotels in {trip['destination']}")
    ])

    # Get hotels from response
    hotels = extract_hotels(response.content)

    return {
        "travel_chat": [response],
        "hotel_options": hotels,
        "response_user": response.content,
        "current_step": "planning_itinerary"
    }


def extract_hotels(content):
    """Get hotels JSON from response"""

    try:
        start = content.find('[')
        end = content.rfind(']') + 1
        if start == -1 or end == 0:
            return []
        return json.loads(content[start:end])
    except:
        return []
