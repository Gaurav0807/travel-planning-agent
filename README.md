# Travel Planning Agent

 AI Agents that helps to plan trips. It uses AWS Bedrock (Claude AI) to understand what you want and suggest flights, hotels, and itineraries.

## How to Run

```bash
cd src
python3 main.py
```

## How It Works

You chat with the bot. It asks where you want to go, when, budget, etc. Then it gives you flight options, hotel options, and a day-by-day plan.

## Files

- `main.py` - Start here. This runs the chatbot.
- `graph.py` - Connects all the agents together.
- `state.py` - Stores conversation data.
- `agents/` - The 4 agents (trip_analyzer, flight_searcher, hotel_searcher, itinerary_planner)
- `knowledge_base.py` - Has info about destinations like Tokyo, Paris, Bali.
- `user_profiles.py` - Saves your past trips so it can give better suggestions next time.

## Example

```
You: I want to go to Tokyo

Bot: Cool! When do you want to go? How many days? What's your budget?

You: June 15 to June 22, $5000, 2 people

Bot: Here are some flights... Here are some hotels... Here's your itinerary...
```

## Requirements

- Python 3
- AWS account with Bedrock access
- Run `pip install -r requirements.txt`
