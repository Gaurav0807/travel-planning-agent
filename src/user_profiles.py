"""
USER_PROFILES.PY - Saves user's past trips

So the bot can remember what you like.
"""

import json
from pathlib import Path


PROFILES_FILE = Path(__file__).parent.parent / "user_profiles.json"


def load_profiles():

    if not PROFILES_FILE.exists():
        return {}

    try:
        with open(PROFILES_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_profiles(profiles):
    """Save all user profiles to file"""

    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)


def get_user_profile(user_id):

    profiles = load_profiles()


    return profiles.get(user_id, {
        "past_trips": [],
        "preferences": {},
        "lessons_learned": []
    })


def save_user_profile(user_id, profile):


    profiles = load_profiles()
    profiles[user_id] = profile
    save_profiles(profiles)


def add_trip_to_profile(user_id, trip_details, rating=None, feedback=None):


    profile = get_user_profile(user_id)

    # Create trip record
    trip = {
        "destination": trip_details.get("destination"),
        "departure_date": trip_details.get("departure_date"),
        "return_date": trip_details.get("return_date"),
        "budget": trip_details.get("budget"),
        "num_travelers": trip_details.get("num_travelers"),
        "interests": trip_details.get("interests", []),
        "rating": rating,
        "feedback": feedback
    }

    # Add to past trips (keep last 10)
    profile["past_trips"].append(trip)
    profile["past_trips"] = profile["past_trips"][-10:]

    # Update preferences
    if trip_details.get("interests"):
        existing = profile["preferences"].get("interests", [])
        for interest in trip_details["interests"]:
            if interest not in existing:
                existing.append(interest)
        profile["preferences"]["interests"] = existing[-10:]

    if trip_details.get("budget"):
        profile["preferences"]["avg_budget"] = trip_details["budget"]

    save_user_profile(user_id, profile)
