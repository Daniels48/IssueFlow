import json
import reverse_geocode

from fastapi import Request
from user_agents import parse

SENSITIVE_QUERY = {"token", "password", "secret"}



def get_protocol(request: Request) -> str:
    forwarded_proto = request.headers.get("x-forwarded-proto")
    if forwarded_proto:
        return forwarded_proto

    return request.url.scheme


def sanitize_query(params: dict):
    return {k: "***" if k in SENSITIVE_QUERY else v for k, v in params.items()}


def get_os(os_family:str) -> str | None:

    if os_family in {"Ubuntu", "Debian", "Fedora", "Linux"}:
        return "Linux"

    if os_family in {"Windows", "Windows 10", "Windows 11"}:
        return "Windows"

    if os_family in {"Mac OS X", "macOS"}:
        return "macOS"

    if os_family == "Android":
        return "Android"

    if os_family in {"iOS", "iPhone OS"}:
        return "iOS"

    return os_family

def parse_user_agent(user_agent: str | None):

    if not user_agent:
        return {}

    ua = parse(user_agent)

    if ua.is_mobile:
        device_type = "mobile"
    elif ua.is_tablet:
        device_type = "tablet"
    else:
        device_type = "desktop"

    return {
        "user_agent": user_agent,
        "browser": ua.browser.family,
        "browser_version": ua.browser.version_string,
        "os": get_os(ua.os.family),
        "os_distribution":ua.os.family,
        "device_type": device_type,

    }


def format_distance(meters: float) -> str:
    if meters >= 1000:
        km = meters / 1000

        if km >= 100:
            return f"{km:.0f} km"

        return f"{km:.1f} km"

    return f"{meters:.0f} m"


def get_position_info(position: dict | None) -> dict:
    if not position:
        return {}

    latitude = position.get("latitude")
    longitude = position.get("longitude")

    if latitude is None or longitude is None:
        return {}

    result = reverse_geocode.search([(latitude, longitude)])[0]

    accuracy = position.get("accuracy")

    return {
        "country": result.get("country"),
        "state": result.get("state"),
        "city": result.get("city"),
        "accuracy": float(accuracy) if accuracy is not None else None,
    }

def get_client_info(value: str | None) -> dict:
    if not value:
        return {}

    try:
        client_info = json.loads(value)
    except json.JSONDecodeError:
        return {}

    if not isinstance(client_info, dict):
        return {}

    resolution = client_info.pop("resolution", None)

    if isinstance(resolution, dict):
        client_info.update({
            "screen_width": resolution.get("screen_width"),
            "screen_height": resolution.get("screen_height"),
            "dpr": resolution.get("dpr"),
        })

    position = client_info.pop("position", None)
    position = get_position_info(position)

    client_info.update(position)

    # # languages пока тоже не сохраняем
    client_info.pop("languages", None)

    return client_info