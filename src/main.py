"""
MAIN.PY - Entry point for Travel Planning Agent

This file:
1. Creates the agent graph
2. Handles user input/output
3. Manages sessions (new or resume)
4. Saves trips to user profile
"""

import sys
import uuid
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from graph import create_graph
from user_profiles import get_user_profile, add_trip_to_profile

# Load environment variables from .env file
load_dotenv()


def main():
    """Main function - runs the travel planning agent"""

    print("\n" + "=" * 50)
    print("  TRAVEL PLANNING AGENT")
    print("=" * 50)

    # STEP 1: Create the graph (connects all agents)
    graph = create_graph()

    # STEP 2: Get or create session ID
    # If user passes session ID as argument, resume that session
    # Otherwise, create a new session
    if len(sys.argv) > 1:
        thread_id = sys.argv[1]
        print(f"\nResuming session: {thread_id}")
    else:
        thread_id = f"travel_{uuid.uuid4().hex[:8]}"
        print(f"\nNew session: {thread_id}")

    # User ID is derived from thread ID (for storing user profile)
    user_id = thread_id.replace("travel_", "")

    # STEP 3: Load user profile (past trips, preferences)
    # This is EPISODIC MEMORY - remembers user across sessions
    user_profile = get_user_profile(user_id)
    past_trips = user_profile.get("past_trips", [])

    if past_trips:
        print(f"\nUser Profile Loaded:")
        print(f"  Past trips: {len(past_trips)}")
        for trip in past_trips[-3:]:
            print(f"  - {trip.get('destination')}")

    # STEP 4: Config tells LangGraph which session to use
    config = {"configurable": {"thread_id": thread_id}}

    # STEP 5: Check if session has existing state (resuming conversation)
    state = graph.get_state(config)

    if state.values:
        # Session exists - show previous data
        print(f"\nSession state found:")
        print(f"  Messages: {len(state.values.get('travel_chat', []))}")

        trip = state.values.get("trip_details")
        if trip:
            print(f"  Current trip: {trip.get('destination')}")
    else:
        print("\nStarting fresh session")

    print("\nCommands: 'quit' to exit, 'save' to save trip")
    print("-" * 50)

    # STEP 6: Main conversation loop
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()

        # Skip empty input
        if not user_input:
            continue

        # Handle 'quit' command
        if user_input.lower() == "quit":
            break

        # Handle 'save' command - saves trip to user profile
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
                print(f"\nTrip to {trip['destination']} saved to your profile!")
            else:
                print("\nNo trip details to save yet.")
            continue

        # STEP 7: Prepare input for the graph
        state = graph.get_state(config)

        if not state.values:
            # First message - create full initial state
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
                "user_profile": user_profile,
                "retrieved_guides": None,
                "retrieved_reviews": None,
                "current_agent": None,
                "response_user": None,
            }
        else:
            # Continuation - just add new message
            input_state = {
                "travel_chat": [HumanMessage(content=user_input)],
            }

        # STEP 8: Run graph and show responses
        print("\nProcessing...\n")

        # graph.stream() runs agents and yields output as each completes
        for chunk in graph.stream(input_state, config):
            # chunk = {"agent_name": {"response_user": "...", ...}}

            for agent_name, agent_output in chunk.items():
                # Skip internal LangGraph nodes
                if agent_name == "__root__":
                    continue

                # Get agent's response text
                response_text = agent_output.get("response_user")

                # Print response if exists
                if response_text:
                    print("=" * 50)
                    print(f"Agent: {agent_name}")
                    print("=" * 50)
                    print(f"\n{response_text}\n")

    # STEP 9: Session end - show summary and offer to save
    state = graph.get_state(config)

    if state.values:
        trip = state.values.get("trip_details")

        print("\n" + "=" * 50)
        print("SESSION SUMMARY")
        print("=" * 50)
        print(f"Thread ID: {thread_id}")

        if trip:
            print(f"Destination: {trip.get('destination')}")

            # Offer to save trip
            save = input("\nSave this trip to your profile? (y/n): ").strip().lower()
            if save == 'y':
                rating = input("Rate trip planning (1-10): ").strip()
                feedback = input("Feedback (optional): ").strip()

                add_trip_to_profile(
                    user_id,
                    trip,
                    rating=int(rating) if rating.isdigit() else None,
                    feedback=feedback if feedback else None
                )
                print("\nSaved! This will be remembered next time.")

        print(f"\nMessages: {len(state.values.get('travel_chat', []))}")
        print("=" * 50)

    print("\nGoodbye!\n")


if __name__ == "__main__":
    main()
