# Travel Planning Agent

A multi-agent travel planning system built with LangGraph and AWS Bedrock. Demonstrates the CoALA (Cognitive Architectures for Language Agents) memory architecture with all 4 memory types.

## CoALA Memory Architecture

This project implements all 4 types of memory from the CoALA framework:

| Memory Type | What It Stores | Implementation |
|-------------|----------------|----------------|
| **Working Memory** | Current conversation, trip details, flight/hotel options | `state.py` (TravelState class) |
| **Episodic Memory** | User's past trips, preferences, lessons learned | `user_profiles.py` + `user_profiles.json` |
| **Semantic Memory** | Facts about destinations, hotels, flights | `knowledge_base.py` + `data/mock_kb.json` |
| **Procedural Memory** | How agents should behave, output formats | `system_prompts/travel/*.txt` |



## Agent Flow

```
START -> trip_analyzer -> flight_searcher -> hotel_searcher -> itinerary_planner -> END
```

1. **trip_analyzer**: Asks questions, extracts destination/dates/budget
2. **flight_searcher**: Suggests flight options based on trip details
3. **hotel_searcher**: Suggests hotels matching budget and preferences
4. **itinerary_planner**: Creates day-by-day itinerary

## Setup

### 1. Install Dependencies

```bash
cd Travel-planning-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure AWS

Make sure you have AWS credentials configured:

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### 3. Create .env File

```bash
# .env
AWS_REGION=us-east-1
CHECKPOINTER_MEMORY=sqlite
```

## Running the Agent

```bash
cd src
python3 main.py
```

### Example Conversation

```
You: I want to go to Tokyo

Agent: Great choice! Tokyo is an incredible destination. To help you plan:
       1. When are you thinking of visiting?
       2. How long do you want to stay?
       3. What's your total budget?
       4. How many people are traveling?
       5. What interests you most?

You: June 15 to June 22, budget $5000, 2 people, interested in food and temples

Agent: [Extracts trip details, searches flights, hotels, creates itinerary]
```

### Resume a Session

```bash
python3 main.py travel_abc123
```

### Save a Trip

Type `save` during conversation to save the trip to your profile. This enables personalized recommendations in future sessions.

## How Memory Works

### Working Memory (state.py)

Holds current session data:
- `travel_chat`: Conversation messages
- `trip_details`: Destination, dates, budget, travelers, interests
- `flight_options`: Found flights
- `hotel_options`: Found hotels
- `itinerary_draft`: Generated itinerary

### Episodic Memory (user_profiles.py)

Persists across sessions in `user_profiles.json`:
- Past trips with ratings
- User preferences (interests, budget range)
- Lessons learned

### Semantic Memory (knowledge_base.py)

Facts loaded from `data/mock_kb.json`:
- Destination info (attractions, climate, cuisine)
- Hotels (name, price, rating)
- Flights (routes, airlines, prices)
- Experiences (tours, activities)

### Procedural Memory (system_prompts/)

Text files that define agent behavior:
- What format to output (JSON)
- What questions to ask
- How to structure responses

## AWS Bedrock Model

Uses Claude Haiku 4.5 via the Converse API:

```python
# Model ID
us.anthropic.claude-haiku-4-5-20251001-v1:0
```

To change the model, edit `src/utils/bedrock_client.py`.

## Key Files Explained

| File | Purpose |
|------|---------|
| `main.py` | Runs the conversation loop, handles session management |
| `graph.py` | Connects agents with LangGraph, defines routing logic |
| `state.py` | Defines TravelState (what data agents share) |
| `memory.py` | SQLite checkpointer for session persistence |
| `knowledge_base.py` | Functions to search destination/hotel/flight facts |
| `user_profiles.py` | Functions to load/save user history |

## Customization

### Add a New Destination

Edit `src/data/mock_kb.json`:

```json
{
  "destinations": [
    {
      "name": "London",
      "description": "Historic capital of England",
      "attractions": ["Big Ben", "Tower of London", "British Museum"],
      "best_for": ["history", "culture", "museums"],
      "climate": "Mild, rainy year-round",
      "cuisine": "Fish and chips, afternoon tea",
      "budget_level": "high"
    }
  ]
}
```

### Add a New Agent

1. Create `src/agents/new_agent.py`
2. Add to `src/agents/__init__.py`
3. Add node in `graph.py`
4. Add routing logic
5. Create prompt in `system_prompts/travel/`

## License

MIT
