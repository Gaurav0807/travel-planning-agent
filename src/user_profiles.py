"""
User Profile Storage - Episodic Memory

Stores user's past trips, preferences, and lessons learned.
This enables personalized recommendations across sessions.
"""

import json
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Store profiles in a JSON file
PROFILES_FILE = Path(__file__).parent.parent / "user_profiles.json"


def load_profiles():
    """Load all user profiles from file"""
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


def get_user_profile(user_id: str) -> dict:
    """Get profile for a specific user

    Args:
        user_id: Unique user identifier (we use thread_id prefix)

    Returns:
        User profile dict with past_trips, preferences, lessons_learned
    """
    profiles = load_profiles()

    profile = profiles.get(user_id, {
        "past_trips": [],
        "preferences": {},
        "lessons_learned": []
    })

    logger.info(f"[user_profiles] Loaded profile for {user_id}: {len(profile.get('past_trips', []))} past trips")
    return profile


def save_user_profile(user_id: str, profile: dict):
    """Save profile for a specific user"""
    profiles = load_profiles()
    profiles[user_id] = profile
    save_profiles(profiles)
    logger.info(f"[user_profiles] Saved profile for {user_id}")


def add_trip_to_profile(user_id: str, trip_details: dict, rating: int = None, feedback: str = None):
    """Add a completed trip to user's history

    Args:
        user_id: User identifier
        trip_details: Trip info (destination, dates, budget, etc.)
        rating: User's rating 1-10 (optional)
        feedback: What they liked/disliked (optional)
    """
    profile = get_user_profile(user_id)

    # Create trip record
    trip_record = {
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
    profile["past_trips"].append(trip_record)
    profile["past_trips"] = profile["past_trips"][-10:]

    # Update preferences based on trip
    if trip_details.get("interests"):
        existing = profile["preferences"].get("interests", [])
        for interest in trip_details["interests"]:
            if interest not in existing:
                existing.append(interest)
        profile["preferences"]["interests"] = existing[-10:]

    if trip_details.get("budget"):
        profile["preferences"]["avg_budget"] = trip_details["budget"]

    save_user_profile(user_id, profile)
    logger.info(f"[user_profiles] Added trip to {trip_details['destination']} for {user_id}")


def add_lesson_learned(user_id: str, lesson: str):
    """Add a lesson learned from a trip"""
    profile = get_user_profile(user_id)

    if lesson not in profile["lessons_learned"]:
        profile["lessons_learned"].append(lesson)
        profile["lessons_learned"] = profile["lessons_learned"][-10:]

    save_user_profile(user_id, profile)


def update_preferences(user_id: str, preferences: dict):
    """Update user preferences"""
    profile = get_user_profile(user_id)
    profile["preferences"].update(preferences)
    save_user_profile(user_id, profile)
