import os
import sys
import uuid
import logging
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from graph import create_graph
from user_profiles import get_user_profile, add_trip_to_profile

load_dotenv()
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def main():


    print("   TRAVEL PLANNING AGENT (CoALA Memory Demo)")


    graph = create_graph()

    # Accept session ID to resume, or create new
    if len(sys.argv) > 1:
        thread_id = sys.argv[1]
        print(f"\n ✓ Resuming session: {thread_id}")
    else:
        thread_id = f"travel_{uuid.uuid4().hex[:8]}"
        print(f"\n ✓ New session: {thread_id}")

    # Get user_id from thread_id
    user_id = thread_id.replace("travel_", "")

    # Load user profile (EPISODIC MEMORY)
    user_profile = get_user_profile(user_id)
    past_trips = user_profile.get("past_trips", [])
    if past_trips:
        print(f"User Profile Loaded!")
        print(f"    Past trips: {len(past_trips)}")
        for t in past_trips[-3:]:
            print(f"    - {t.get('destination')}")

    config = {"configurable": {"thread_id": thread_id}}

    # Check if session has existing state
    state = graph.get_state(config)

    if state.values:
        print(f"\n 📂 Session state found!")
        print(f"    Messages: {len(state.values.get('travel_chat', []))}")
        trip = state.values.get("trip_details")
        if trip:
            print(f"    Current trip: {trip.get('destination', 'N/A')}")

        # Show last AI response
        messages = state.values.get("travel_chat", [])
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                print(f"\n    Last response:")
                content = msg.content[:300] + "..." if len(msg.content) > 300 else msg.content
                for line in content.split("\n")[:5]:
                    print(f"    {line}")
                break
    else:
        print(f"Starting fresh session!")

    print("\n Commands: 'quit' to exit, 'save' to save trip to profile")

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        # Handle quit
        if user_input.lower() == "quit":
            break

        # Handle save - save current trip to profile
        if user_input.lower() == "save":
            state = graph.get_state(config)
            trip = state.values.get("trip_details") if state.values else None
            if trip:
                rating = input("Rate your trip planning (1-10): ").strip()
                feedback = input("Any feedback? (optional): ").strip()
                add_trip_to_profile(
                    user_id,
                    trip,
                    rating=int(rating) if rating.isdigit() else None,
                    feedback=feedback if feedback else None
                )
                print(f"Trip to {trip['destination']} saved to your profile!")
                print("    This will be remembered in future sessions.")
            else:
                print("\n No trip details to save yet.")
            continue

        # Check if first message or continuation
        state = graph.get_state(config)

        if not state.values:
            input_state = {
                "thread_id": thread_id,
                "travel_chat": [HumanMessage(content=user_input)],
                "trip_details": None,
                "current_step": "gathering_info",
                "flight_options": [],
                "hotel_options": [],
                "attractions": [],
                "itinerary_draft": None,
                "total_cost": None,
                "user_profile": user_profile,  # Pass loaded profile
                "retrieved_guides": None,
                "retrieved_reviews": None,
                "current_agent": None,
                "response_user": None,
            }
        else:
            input_state = {
                "travel_chat": [HumanMessage(content=user_input)],
            }

        # Run graph
        print("\n Processing...\n")

        for chunk in graph.stream(input_state, config):
            for agent_name, agent_output in chunk.items():
                if agent_name == "__root__":
                    continue

                response_text = agent_output.get("response_user")
                if response_text:
                    print(f"{agent_name.replace('_', ' ').title()}")
                    print(f"\n{response_text}\n")

    # Session end - offer to save trip
    state = graph.get_state(config)
    if state.values:
        trip = state.values.get("trip_details")

        print("\n" + "=" * 60)
        print(" SESSION SUMMARY")
        print("=" * 60)
        print(f" Thread ID: {thread_id}")
        if trip:
            print(f" Destination: {trip.get('destination', 'N/A')}")

            # Offer to save
            save = input("\n Save this trip to your profile? (y/n): ").strip().lower()
            if save == 'y':
                rating = input(" Rate trip planning (1-10): ").strip()
                feedback = input(" Feedback (optional): ").strip()
                add_trip_to_profile(
                    user_id,
                    trip,
                    rating=int(rating) if rating.isdigit() else None,
                    feedback=feedback if feedback else None
                )
                print(f" Saved! Next time you'll get personalized recommendations.")

        print(f"\n Messages: {len(state.values.get('travel_chat', []))}")
        print(f" Checkpoint: checkpoint.sqlite")
        print(f" Profile: user_profiles.json")
        print("=" * 60)

    print("\nGoodbye!\n")


if __name__ == "__main__":
    main()
