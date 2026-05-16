"""
KNOWLEDGE_BASE.PY - Semantic Memory

This is the agent's knowledge about destinations, hotels, flights, etc.
Data is stored in data/mock_kb.json

SEMANTIC MEMORY = Facts and knowledge (not personal to user)

Example:
- "Tokyo has Senso-ji Temple"
- "Bali is best visited April-October"
- "Paris hotels cost $35-250/night"
"""

import json
from pathlib import Path


# Load data once when module is imported
KB_PATH = Path(__file__).parent / "data" / "mock_kb.json"

try:
    with open(KB_PATH, "r") as f:
        KB_DATA = json.load(f)
except:
    KB_DATA = {"destinations": [], "hotels": [], "flights": [], "experiences": []}


def search_destination(query):
    """
    Search for destination info by name or keyword

    Input: "Tokyo" or "beach" or "temples"
    Output: List of matching destinations
    """
    query = query.lower()
    results = []

    for dest in KB_DATA.get("destinations", []):
        # Check name, description, attractions, best_for
        if (
            query in dest["name"].lower()
            or query in dest["description"].lower()
            or any(query in attr.lower() for attr in dest.get("attractions", []))
            or any(query in cat.lower() for cat in dest.get("best_for", []))
        ):
            results.append(dest)

    return results


def search_hotels(destination="", budget=""):
    """
    Search for hotels by destination and budget

    Input: destination="Tokyo", budget="low" / "medium" / "high"
    Output: List of matching hotels
    """
    results = []

    for hotel in KB_DATA.get("hotels", []):
        # Check destination match
        dest_match = not destination or destination.lower() in hotel["destination"].lower()

        # Check budget match
        price = hotel.get("price_per_night", 0)
        if budget == "low":
            budget_match = price < 100
        elif budget == "medium":
            budget_match = 100 <= price < 250
        elif budget == "high":
            budget_match = price >= 250
        else:
            budget_match = True

        if dest_match and budget_match:
            results.append(hotel)

    return results


def search_flights(destination=""):
    """
    Search for flights to a destination

    Input: destination="Tokyo"
    Output: List of matching flights
    """
    results = []

    for flight in KB_DATA.get("flights", []):
        if not destination or destination.lower() in flight["route"].lower():
            results.append(flight)

    return results


def search_experiences(destination="", interests=None):
    """
    Search for experiences/activities

    Input: destination="Bali", interests=["food", "adventure"]
    Output: List of matching experiences
    """
    interests = interests or []
    results = []

    for exp in KB_DATA.get("experiences", []):
        # Check destination
        dest_match = not destination or destination.lower() in exp["destination"].lower()

        # Check interests
        if interests:
            interest_match = any(
                interest.lower() in cat.lower()
                for interest in interests
                for cat in exp.get("best_for", [])
            )
        else:
            interest_match = True

        if dest_match and interest_match:
            results.append(exp)

    return results


def get_destination_info(destination):
    """
    Get full info about a destination for the LLM

    Input: "Tokyo"
    Output: Formatted string with all KB info about Tokyo
    """
    dest_name = destination.lower()

    # Find destination
    dest_info = None
    for dest in KB_DATA.get("destinations", []):
        if dest_name in dest["name"].lower():
            dest_info = dest
            break

    if not dest_info:
        return None

    # Find hotels
    hotels = search_hotels(destination=dest_info["name"])

    # Find experiences
    experiences = search_experiences(destination=dest_info["name"])

    # Format output
    output = f"""
KNOWLEDGE BASE INFO FOR: {dest_info['name']}

ABOUT:
{dest_info['description']}

CLIMATE:
{dest_info.get('climate', 'N/A')}

TOP ATTRACTIONS:
{', '.join(dest_info.get('attractions', []))}

CUISINE:
{dest_info.get('cuisine', 'N/A')}

BUDGET LEVEL: {dest_info.get('budget_level', 'N/A')}

BEST FOR: {', '.join(dest_info.get('best_for', []))}
"""

    if hotels:
        output += "\nHOTELS IN KB:\n"
        for h in hotels:
            output += f"- {h['name']}: ${h['price_per_night']}/night, Rating {h['rating']}/5\n"

    if experiences:
        output += "\nEXPERIENCES IN KB:\n"
        for e in experiences:
            output += f"- {e['title']}: {e['duration_hours']}h, {e['price']}\n"

    return output
