from langchain_core.tools import tool
from datetime import datetime
import json
from urllib.parse import quote
from urllib.request import urlopen


@tool
def calculator(a: float, b: float, operation: str) -> float:
    """Perform addition, subtraction, multiplication, or division on two numbers."""

    if operation == "add":
        return a + b

    elif operation == "subtract":
        return a - b

    elif operation == "multiply":
        return a * b

    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero.")

        return a / b

    raise ValueError(f"Unknown operation: {operation}")

@tool
def get_time():
    """give current time"""
    return datetime.now().strftime("%H:%M:%S")


@tool
def get_weather(city: str) -> str:
    """Return the current weather for a city using Open-Meteo."""
    geocoding_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?name={quote(city)}&count=1&language=en&format=json"
    )

    with urlopen(geocoding_url, timeout=10) as response:
        location_data = json.load(response)

    locations = location_data.get("results", [])
    if not locations:
        return f"No location found for {city}"

    location = locations[0]
    forecast_url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={location['latitude']}&longitude={location['longitude']}"
        "&current=temperature_2m,weather_code,wind_speed_10m&timezone=auto"
    )

    with urlopen(forecast_url, timeout=10) as response:
        forecast_data = json.load(response)

    current = forecast_data["current"]
    weather_descriptions = {
        0: "clear sky",
        1: "mainly clear",
        2: "partly cloudy",
        3: "overcast",
        45: "foggy",
        48: "depositing rime fog",
        51: "light drizzle",
        53: "moderate drizzle",
        55: "dense drizzle",
        61: "slight rain",
        63: "moderate rain",
        65: "heavy rain",
        71: "slight snow",
        73: "moderate snow",
        75: "heavy snow",
        80: "slight rain showers",
        81: "moderate rain showers",
        82: "violent rain showers",
        95: "thunderstorm",
        96: "thunderstorm with slight hail",
        99: "thunderstorm with heavy hail",
    }

    condition = weather_descriptions.get(
        current["weather_code"],
        "unknown conditions",
    )
    return (
        f"{location['name']}: {current['temperature_2m']}"
        f"{forecast_data['current_units']['temperature_2m']}, {condition}; "
        f"wind {current['wind_speed_10m']}"
        f"{forecast_data['current_units']['wind_speed_10m']}"
    )


TOOL_REGISTRY = {
    calculator.name: calculator,
    get_time.name: get_time,
    get_weather.name: get_weather,
}


def get_tool(name: str):
    """Return a registered tool by name."""
    try:
        return TOOL_REGISTRY[name]
    except KeyError:
        raise ValueError(f"Unknown tool: {name}") from None