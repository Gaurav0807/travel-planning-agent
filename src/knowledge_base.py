"""
KNOWLEDGE_BASE.PY - Facts about destinations

This has info about Tokyo, Paris, Bali, etc.
The bot uses this to give accurate information.
"""

import json
from pathlib import Path

# load data json file
KB_PATH = Path(__file__).parent / "data" / "mock_kb.json"

try:
    with open(KB_PATH, "r") as f:
        DATA = json.load(f)
except:
    DATA = {"destinations": [], "hotels": [], "flights": [], "experiences": []}


def search_destination(query):
    """Find destinations by name or keyword"""

    query = query.lower()
    results = []

    for dest in DATA.get("destinations", []):
        # Check if query matches name, description, or attractions
        if (
            query in dest["name"].lower()
            or query in dest["description"].lower()
            or any(query in attr.lower() for attr in dest.get("attractions", []))
            or any(query in cat.lower() for cat in dest.get("best_for", []))
        ):
            results.append(dest)

    return results


def search_hotels(destination="", budget=""):
    """Find hotels by destination and budget (low/medium/high)"""

    results = []

    for hotel in DATA.get("hotels", []):
        # Check destination
        dest_ok = not destination or destination.lower() in hotel["destination"].lower()

        # Check budget
        price = hotel.get("price_per_night", 0)
        if budget == "low":
            budget_ok = price < 100
        elif budget == "medium":
            budget_ok = 100 <= price < 250
        elif budget == "high":
            budget_ok = price >= 250
        else:
            budget_ok = True

        if dest_ok and budget_ok:
            results.append(hotel)

    return results


def search_flights(destination=""):
    """Find flights to a destination"""

    results = []

    for flight in DATA.get("flights", []):
        if not destination or destination.lower() in flight["route"].lower():
            results.append(flight)

    return results


def search_experiences(destination="", interests=None):
    """Find activities and tours"""

    interests = interests or []
    results = []

    for exp in DATA.get("experiences", []):
        # Check destination
        dest_ok = not destination or destination.lower() in exp["destination"].lower()

        # Check interests
        if interests:
            interest_ok = any(
                interest.lower() in cat.lower()
                for interest in interests
                for cat in exp.get("best_for", [])
            )
        else:
            interest_ok = True

        if dest_ok and interest_ok:
            results.append(exp)

    return results


def get_destination_info(destination):
    """Get all info about a destination for the bot to use"""

    dest_name = destination.lower()

    # Find the destination
    dest_info = None
    for dest in DATA.get("destinations", []):
        if dest_name in dest["name"].lower():
            dest_info = dest
            break

    if not dest_info:
        return None

    # Get related hotels and experiences
    hotels = search_hotels(destination=dest_info["name"])
    experiences = search_experiences(destination=dest_info["name"])

    # Build info text
    output = f"""
        INFO FOR: {dest_info['name']}

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
        output += "\nHOTELS:\n"
        for h in hotels:
            output += f"- {h['name']}: ${h['price_per_night']}/night, Rating {h['rating']}/5\n"

    if experiences:
        output += "\nTHINGS TO DO:\n"
        for e in experiences:
            output += f"- {e['title']}: {e['duration_hours']}h, {e['price']}\n"

    return output
