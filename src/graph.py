"""

Flow:--> trip_analyzer -> flight_searcher -> hotel_searcher -> itinerary_planner
"""

import os
from langgraph.graph import START, END, StateGraph
from agents import trip_analyzer, flight_searcher, hotel_searcher, itinerary_planner
from memory import get_checkpointer
from state import TravelState



def after_analyzer(state):
    """After trip_analyzer: go to flights if we have trip details"""
    if state.get("trip_details"):
        return "flight_searcher"
    return END


def after_flights(state):
    """After flight_searcher: go to hotels if we have flights"""
    if state.get("flight_options"):
        return "hotel_searcher"
    return END


def after_hotels(state):
    """After hotel_searcher: go to itinerary if we have hotels"""
    if state.get("hotel_options"):
        return "itinerary_planner"
    return END


def create_graph():
    """Create the chatbot"""

    # Create empty graph
    graph = StateGraph(TravelState)

    # Add agents
    graph.add_node("trip_analyzer", trip_analyzer)
    graph.add_node("flight_searcher", flight_searcher)
    graph.add_node("hotel_searcher", hotel_searcher)
    graph.add_node("itinerary_planner", itinerary_planner)

    # Connect them
    graph.add_edge(START, "trip_analyzer")

    graph.add_conditional_edges(
        "trip_analyzer",
        after_analyzer,
        {"flight_searcher": "flight_searcher", END: END}
    )

    graph.add_conditional_edges(
        "flight_searcher",
        after_flights,
        {"hotel_searcher": "hotel_searcher", END: END}
    )

    graph.add_conditional_edges(
        "hotel_searcher",
        after_hotels,
        {"itinerary_planner": "itinerary_planner", END: END}
    )

    graph.add_edge("itinerary_planner", END)

    # Add memory (saves conversations)
    checkpointer = get_checkpointer("sqlite")

    return graph.compile(checkpointer=checkpointer)
