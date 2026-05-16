from langchain_core.messages import SystemMessage, HumanMessage
from utils.bedrock_client import get_llm
from utils.prompt_loader import load_system_prompt

llm = get_llm()


def itinerary_planner(state):
    """Create the final itinerary"""

    trip = state.get("trip_details")
    if not trip:
        return {"response_user": "Need trip details first"}

    # Load instructions
    prompt = load_system_prompt("itinerary_planner")

    # Add trip info
    context = f"""
        Trip Details:
        - Destination: {trip['destination']}
        - Dates: {trip['departure_date']} to {trip['return_date']}
        - Budget: ${trip['budget']}
        - Travelers: {trip['num_travelers']}
        - Interests: {', '.join(trip.get('interests', []))}
        """

    # Ask Claude for itinerary
    response = llm.invoke([
        SystemMessage(prompt + context),
        HumanMessage(content=f"Create itinerary for {trip['destination']}")
    ])

    return {
        "travel_chat": [response],
        "itinerary_draft": response.content,
        "response_user": response.content,
        "current_step": "finalizing"
    }
