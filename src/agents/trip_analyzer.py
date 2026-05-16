
import json
from langchain_core.messages import SystemMessage
from utils.bedrock_client import get_llm
from utils.prompt_loader import load_system_prompt
from user_profiles import get_user_profile
from knowledge_base import get_destination_info, search_destination

llm = get_llm()


def trip_analyzer(state):
    """Ask questions and extract trip details"""

    # Load instructions
    prompt = load_system_prompt("trip_analyzer")

    # Get messages
    messages = state.get("travel_chat", [])
    if not messages:
        return {
            "response_user": "Hi! Where would you like to travel?",
            "current_step": "gathering_info"
        }

    last_message = messages[-1]

    # Get user ID
    thread_id = state.get("thread_id", "unknown")
    user_id = thread_id.replace("travel_", "")

    # Load user's past trips
    user_profile = get_user_profile(user_id)

    # Add user info to prompt
    context = build_context(state, user_profile)
    if context:
        prompt += context

    # Add destination facts
    kb_info = get_kb_context(last_message.content)
    if kb_info:
        prompt += kb_info

    # Ask Claude
    response = llm.invoke([
        SystemMessage(prompt),
        last_message
    ])

    # Try to get trip details from response
    trip_details = extract_trip(response.content)

    result = {
        "travel_chat": [response],
        "response_user": response.content,
        "current_step": "searching_flights" if trip_details else "gathering_info",
        "user_profile": user_profile
    }

    if trip_details:
        result["trip_details"] = trip_details

    return result


def build_context(state, user_profile):
    """Add user's past trips to prompt"""

    parts = []

    # Current trip
    trip = state.get("trip_details")
    if trip:
        parts.append(f"""
Current Trip:
- Destination: {trip.get('destination')}
- Dates: {trip.get('departure_date')} to {trip.get('return_date')}
- Budget: ${trip.get('budget')}
""")

    # Past trips
    past_trips = user_profile.get("past_trips", [])
    if past_trips:
        parts.append("\nPast Trips:")
        for t in past_trips[-3:]:
            parts.append(f"- {t.get('destination')}")

    if parts:
        return "\n\n--- USER INFO ---" + "\n".join(parts)

    return ""


def get_kb_context(user_message):
    """Get facts about destinations"""

    known = ["tokyo", "paris", "bali", "barcelona", "new york"]
    user_lower = user_message.lower()

    # Check if user mentioned a destination
    for dest in known:
        if dest in user_lower:
            kb_info = get_destination_info(dest)
            if kb_info:
                return f"\n\n--- FACTS ---{kb_info}"

    # Check for keywords
    keywords = ["beach", "temple", "museum", "food", "adventure"]
    for keyword in keywords:
        if keyword in user_lower:
            results = search_destination(keyword)
            if results:
                names = [r["name"] for r in results[:3]]
                return f"\n\n--- SUGGESTIONS ---\nFor '{keyword}': {', '.join(names)}"

    return ""


def extract_trip(content):
    """Get trip details JSON from response"""

    try:
        start = content.find('{')
        end = content.rfind('}') + 1
        if start == -1 or end == 0:
            return None

        data = json.loads(content[start:end])

        # Need destination and dates
        if not all([data.get("destination"), data.get("departure_date"), data.get("return_date")]):
            return None

        return {
            "destination": data.get("destination", ""),
            "departure_date": data.get("departure_date", ""),
            "return_date": data.get("return_date", ""),
            "budget": float(data.get("budget", 0)),
            "num_travelers": int(data.get("num_travelers", 1)),
            "interests": data.get("interests", [])
        }
    except:
        return None
