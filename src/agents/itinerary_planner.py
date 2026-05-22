from langchain_core.messages import SystemMessage, HumanMessage
from utils.bedrock_client import get_llm
from utils.prompt_loader import load_system_prompt
from utils.mcp_client import call_weather_tool

llm = get_llm()


def itinerary_planner(state):

    trip = state.get("trip_details")

    if not trip:
        return {"response_user": "Need trip details first"}

    prompt = load_system_prompt("itinerary_planner")

    destination = trip["destination"]

    # Call Weather MCP Server for real data
    try:
        current = call_weather_tool("get_current_weather", {"city": destination})
        forecast = call_weather_tool("get_forecast", {"city": destination})
        weather_data = f"Current Weather:\n{current}\n\nForecast:\n{forecast}"
        print(f"[MCP] Got real weather for {destination}")
    except Exception as e:
        weather_data = f"Weather unavailable: {e}"
        print(f"[MCP] Weather fetch failed: {e}")

    context = f"""
        Trip Details:
        - Destination: {destination}
        - Dates: {trip['departure_date']} to {trip['return_date']}
        - Budget: ${trip['budget']}
        - Travelers: {trip['num_travelers']}
        - Interests: {', '.join(trip.get('interests', []))}

        Real Weather Data for {destination} (from Weather MCP Server):
        {weather_data}

        IMPORTANT: Use the real weather data above to plan activities.
        - If rainy → suggest indoor activities (museums, cafes)
        - If sunny → suggest outdoor activities (parks, walking tours)
        - If hot → suggest morning/evening activities, avoid midday
        - If cold → suggest warm indoor places, pack warm clothes
        """

    response = llm.invoke([
        SystemMessage(prompt + context),
        HumanMessage(content=f"Create itinerary for {destination}")
    ])

    return {
        "travel_chat": [response],
        "itinerary_draft": response.content,
        "response_user": response.content,
        "current_step": "finalizing"
    }