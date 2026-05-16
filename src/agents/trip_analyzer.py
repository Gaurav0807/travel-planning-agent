import json
import logging
from langchain_core.messages import SystemMessage
from utils.bedrock_client import get_llm
from utils.prompt_loader import load_system_prompt
from user_profiles import get_user_profile
from knowledge_base import get_destination_info, search_destination

logger = logging.getLogger(__name__)

llm = get_llm()


def trip_analyzer(state):
    """Analyze user's trip request and extract details"""

    logger.info("[trip_analyzer] Running...")

    # Load prompt
    prompt = load_system_prompt("trip_analyzer")

    # Get user messages
    messages = state.get("travel_chat", [])
    if not messages:
        return {
            "response_user": "Hi! Where would you like to travel?",
            "current_step": "gathering_info"
        }

    last_message = messages[-1]

    # Get user_id from thread_id (e.g., "travel_abc123" -> "abc123")
    thread_id = state.get("thread_id", "unknown")
    user_id = thread_id.replace("travel_", "")

    # Load user profile from file (EPISODIC MEMORY)
    user_profile = get_user_profile(user_id)
    print("User Profile")
    print(user_profile)

    # Build context from state + user profile
    context = _build_context(state, user_profile)
    if context:
        prompt += context

    # Add knowledge base info (SEMANTIC MEMORY)
    # Extract destination from user message and get facts about it
    kb_info = _get_kb_context(last_message.content)
    print("Kb Info Start")
    print(kb_info)
    print("Kb Info End")
    if kb_info:
        prompt += kb_info

    # Call LLM
    response = llm.invoke([
        SystemMessage(prompt),
        last_message
    ])

    # Try to extract trip details
    trip_details = _extract_trip(response.content)

    result = {
        "travel_chat": [response],
        "response_user": response.content,
        "current_step": "searching_flights" if trip_details else "gathering_info",
        "user_profile": user_profile  # Pass profile to state
    }

    if trip_details:
        result["trip_details"] = trip_details
        logger.info(f"[trip_analyzer] Got trip: {trip_details['destination']}")

    return result


def _build_context(state, user_profile):
    """Build context from state and user profile"""

    context_parts = []

    # 1. Current trip details (from this session)
    trip = state.get("trip_details")
    if trip:
        context_parts.append(f"""
        # Current Trip Being Planned:
        - Destination: {trip.get('destination')}
        - Dates: {trip.get('departure_date')} to {trip.get('return_date')}
        - Budget: ${trip.get('budget')}
        - Travelers: {trip.get('num_travelers')}
        - Interests: {', '.join(trip.get('interests', []))}
        """)

    # 2. Past trips from user profile (EPISODIC MEMORY)
    past_trips = user_profile.get("past_trips", [])
    if past_trips:
        context_parts.append("\n# User's Past Trips:")
        for t in past_trips[-5:]:  # Last 5 trips
            rating = f", rated {t.get('rating')}/10" if t.get('rating') else ""
            feedback = f" - {t.get('feedback')}" if t.get('feedback') else ""
            context_parts.append(f"- {t.get('destination')} ({t.get('departure_date')}){rating}{feedback}")

    # 3. User preferences (EPISODIC MEMORY)
    prefs = user_profile.get("preferences", {})
    if prefs:
        context_parts.append(f"\n# User Preferences: {prefs}")

    # 4. Lessons learned (EPISODIC MEMORY)
    lessons = user_profile.get("lessons_learned", [])
    if lessons:
        context_parts.append("\n# Lessons from Past Trips:")
        for lesson in lessons[-5:]:
            context_parts.append(f"- {lesson}")

    # 5. Session info
    flights = state.get("flight_options", [])
    hotels = state.get("hotel_options", [])
    if flights:
        context_parts.append(f"\n# Flights Found: {len(flights)} options")
    if hotels:
        context_parts.append(f"\n# Hotels Found: {len(hotels)} options")
    if state.get("itinerary_draft"):
        context_parts.append("\n# Itinerary: Created")

    if context_parts:
        return "\n\n--- USER CONTEXT ---" + "\n".join(context_parts)

    return ""


def _get_kb_context(user_message):
    """
    Get knowledge base info .

    This is SEMANTIC MEMORY - facts about destinations that help the LLM
    give accurate information instead of making things up.

    Example: If user says "I want to go to Tokyo", we search KB for Tokyo
    and return info about attractions, climate, hotels, etc.
    """
    # List of destinations we have in our knowledge base
    known_destinations = ["tokyo", "paris", "bali", "barcelona", "new york"]

    user_lower = user_message.lower()

    # Check if user mentioned any destination we know about
    for dest in known_destinations:
        if dest in user_lower:
            # Get full info from knowledge base
            kb_info = get_destination_info(dest)
            if kb_info:
                logger.info(f"[trip_analyzer] Found KB info for: {dest}")
                return f"\n\n--- KNOWLEDGE BASE (Use these facts) ---{kb_info}"

    # Also try searching by keywords (beach, temples, etc.)
    keywords = ["beach", "temple", "museum", "food", "adventure", "romantic"]
    for keyword in keywords:
        if keyword in user_lower:
            results = search_destination(keyword)
            if results:
                # Format search results
                dest_names = [r["name"] for r in results[:3]]
                logger.info(f"[trip_analyzer] KB search for '{keyword}': {dest_names}")
                return f"\n\n--- KNOWLEDGE BASE SUGGESTIONS ---\nDestinations matching '{keyword}': {', '.join(dest_names)}"

    return ""


def _extract_trip(content):
    """Extract trip details JSON from response"""
    try:
        start = content.find('{')
        end = content.rfind('}') + 1
        if start == -1 or end == 0:
            return None

        data = json.loads(content[start:end])

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
