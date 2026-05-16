"""
GRAPH.PY - Creates the agent workflow

This file does 3 things:
1. Adds agents as nodes
2. Connects agents with edges
3. Adds routing logic (which agent runs next)

FLOW:
START -> trip_analyzer -> flight_searcher -> hotel_searcher -> itinerary_planner -> END
"""

import os
import logging
from langgraph.graph import START, END, StateGraph

from agents import trip_analyzer, flight_searcher, hotel_searcher, itinerary_planner
from memory import get_checkpointer
from state import TravelState

logger = logging.getLogger(__name__)


# ============================================================
# ROUTING FUNCTIONS
# These decide which agent runs next
# ============================================================

def route_after_analyzer(state):
    """
    Called after trip_analyzer finishes.

    If trip_details exists (user gave complete info):
        -> Go to flight_searcher
    Else:
        -> Stop and wait for more user input
    """
    if state.get("trip_details"):
        return "flight_searcher"
    return END


def route_after_flights(state):
    """
    Called after flight_searcher finishes.

    If flight_options exists:
        -> Go to hotel_searcher
    Else:
        -> Stop
    """
    if state.get("flight_options"):
        return "hotel_searcher"
    return END


def route_after_hotels(state):
    """
    Called after hotel_searcher finishes.

    If hotel_options exists:
        -> Go to itinerary_planner
    Else:
        -> Stop
    """
    if state.get("hotel_options"):
        return "itinerary_planner"
    return END


# ============================================================
# CREATE GRAPH
# ============================================================

def create_graph():
    """Create and return the compiled graph"""

    # Step 1: Create empty graph with our state type
    graph = StateGraph(TravelState)

    # Step 2: Add nodes (each node is an agent function)
    graph.add_node("trip_analyzer", trip_analyzer)
    graph.add_node("flight_searcher", flight_searcher)
    graph.add_node("hotel_searcher", hotel_searcher)
    graph.add_node("itinerary_planner", itinerary_planner)

    # Step 3: Add edges (connections)

    # START always goes to trip_analyzer
    graph.add_edge(START, "trip_analyzer")

    # After trip_analyzer, check routing function
    graph.add_conditional_edges(
        "trip_analyzer",          # From this node
        route_after_analyzer,     # Call this function
        {                         # Map return value to next node
            "flight_searcher": "flight_searcher",
            END: END
        }
    )

    # After flight_searcher, check routing function
    graph.add_conditional_edges(
        "flight_searcher",
        route_after_flights,
        {
            "hotel_searcher": "hotel_searcher",
            END: END
        }
    )

    # After hotel_searcher, check routing function
    graph.add_conditional_edges(
        "hotel_searcher",
        route_after_hotels,
        {
            "itinerary_planner": "itinerary_planner",
            END: END
        }
    )

    # itinerary_planner always goes to END
    graph.add_edge("itinerary_planner", END)

    # Step 4: Add checkpointer (saves state to SQLite)
    checkpointer_type = os.getenv("CHECKPOINTER_MEMORY", "sqlite")
    checkpointer = get_checkpointer(checkpointer_type)

    # Step 5: Compile and return
    app = graph.compile(checkpointer=checkpointer)
    logger.info("Graph compiled")

    return app
