import os
import json
import httpx
from fastmcp import FastMCP

mcp = FastMCP(name="Weather Server")

API_KEY = os.environ.get("openweather_api_key","")

@mcp.tool
def get_current_weather(city: str) -> str:

    if not API_KEY:
        return "Error: Set OPENWEATHER_API_KEY environment variable"

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric"}

    response = httpx.get(url, params=params, timeout=10)
    data = response.json()

    if response.status_code != 200:
        return f"Error: {data.get('message', 'City not found')}"

    return json.dumps({
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"],
    })


@mcp.tool
def get_forecast(city: str) -> str:

    if not API_KEY:
        return "Error: Set OPENWEATHER_API_KEY environment variable"

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": API_KEY, "units": "metric"}

    response = httpx.get(url, params=params, timeout=10)
    data = response.json()

    if response.status_code != 200:
        return f"Error: {data.get('message', 'City not found')}"

    daily = []
    for i in range(0, len(data["list"]), 8):
        entry = data["list"][i]
        daily.append({
            "date": entry["dt_txt"].split(" ")[0],
            "temperature": entry["main"]["temp"],
            "description": entry["weather"][0]["description"],
            "humidity": entry["main"]["humidity"],
        })

    return json.dumps({
        "city": data["city"]["name"],
        "country": data["city"]["country"],
        "forecast": daily
    })


if __name__ == "__main__":
    print("Weather MCP Server")
    print(f"API Key: {'set' if API_KEY else 'NOT SET'}")
    print("Tools: get_current_weather, get_forecast")
    print("Running on http://localhost:8001\n")
    mcp.run(transport="sse", host="0.0.0.0", port=8001)