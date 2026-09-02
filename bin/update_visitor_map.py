#!/usr/bin/env python3
"""Generate the public city-level visitor map data from a GA4 property."""

from __future__ import annotations

import json
import os
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import geonamescache
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2 import service_account


OUTPUT_PATH = Path(__file__).resolve().parents[1] / "assets" / "data" / "visitor-map.json"
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
START_DATE = "2020-01-01"


def normalize(value: str) -> str:
    """Make GA and GeoNames names comparable while keeping the lookup simple."""

    decomposed = unicodedata.normalize("NFKD", value)
    ascii_value = decomposed.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_value.casefold().split())


def get_required_environment(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_client() -> tuple[BetaAnalyticsDataClient, str]:
    property_id = get_required_environment("GA4_PROPERTY_ID")
    property_id = property_id.removeprefix("properties/")
    if not property_id.isdigit():
        raise RuntimeError("GA4_PROPERTY_ID must be the numeric GA4 Property ID, not the G- measurement ID.")

    credentials_file = os.environ.get("GA4_SERVICE_ACCOUNT_FILE", "").strip()
    credentials_json = os.environ.get("GA4_SERVICE_ACCOUNT_JSON", "").strip()
    if credentials_file:
        try:
            credentials_json = Path(credentials_file).read_text(encoding="utf-8")
        except OSError as error:
            raise RuntimeError(f"Could not read GA4_SERVICE_ACCOUNT_FILE: {credentials_file}") from error
    if not credentials_json:
        raise RuntimeError("Missing GA4_SERVICE_ACCOUNT_JSON or GA4_SERVICE_ACCOUNT_FILE")

    try:
        service_account_info = json.loads(credentials_json)
    except json.JSONDecodeError as error:
        raise RuntimeError("GA4_SERVICE_ACCOUNT_JSON must contain the service-account JSON object.") from error

    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES,
    )
    return BetaAnalyticsDataClient(credentials=credentials), property_id


def build_city_index() -> dict[tuple[str, str], dict[str, str | float]]:
    city_index = {}
    for city in geonamescache.GeonamesCache().get_cities().values():
        country_code = str(city.get("countrycode", "")).upper()
        city_name = normalize(str(city.get("name", "")))
        if not country_code or not city_name:
            continue
        key = (country_code, city_name)
        population = int(city.get("population", 0) or 0)
        existing = city_index.get(key)
        if existing is not None and population <= int(existing.get("population", 0)):
            continue
        city_index[key] = {
            "city": str(city["name"]),
            "lat": float(city["latitude"]),
            "lon": float(city["longitude"]),
            "population": population,
        }
    return city_index


def build_country_index(city_index: dict[tuple[str, str], dict[str, str | float]]) -> dict[str, dict[str, str | float]]:
    country_index = {}
    for country_code, country in geonamescache.GeonamesCache().get_countries().items():
        capital = normalize(str(country.get("capital", "")))
        capital_city = city_index.get((country_code.upper(), capital))
        if capital_city is not None:
            country_index[country_code.upper()] = capital_city
    return country_index


def fetch_visitors(client: BetaAnalyticsDataClient, property_id: str) -> list[dict[str, str | int | float]]:
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="country"), Dimension(name="countryId"), Dimension(name="city")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date=START_DATE, end_date="today")],
        limit=10000,
    )
    response = client.run_report(request)
    city_index = build_city_index()
    country_index = build_country_index(city_index)
    visitors = defaultdict(
        lambda: {
            "visitors": 0,
            "city": "",
            "country": "",
            "lat": 0.0,
            "lon": 0.0,
            "precision": "city",
        }
    )
    unmatched_rows = 0
    unlocated_active_users = 0

    for row in response.rows:
        country, country_id, city_name = (value.value for value in row.dimension_values)
        country_code = country_id.upper()
        city = city_index.get((country_code, normalize(city_name)))
        if city is None and city_name == "(not set)":
            unmatched_rows += 1
        if city is None:
            city = country_index.get(country_code)
            if city is None:
                unlocated_active_users += int(row.metric_values[0].value or 0)
                continue
            key = (country_code, "__country__")
        else:
            key = (country_code, normalize(city_name))

        visitors[key]["visitors"] += int(row.metric_values[0].value or 0)
        visitors[key]["city"] = city["city"] if key[1] != "__country__" else "City unavailable"
        visitors[key]["country"] = country
        visitors[key]["lat"] = city["lat"]
        visitors[key]["lon"] = city["lon"]
        visitors[key]["precision"] = "city" if key[1] != "__country__" else "country"

    if unmatched_rows:
        print(
            f"Used country-level fallback for {unmatched_rows} GA4 rows with city '(not set)'.",
            file=sys.stderr,
        )
    if unlocated_active_users:
        print(
            f"Could not place {unlocated_active_users} active users with no country-level location.",
            file=sys.stderr,
        )

    result = list(visitors.values())
    result.sort(key=lambda visitor: int(visitor["visitors"]), reverse=True)
    return result[:200]


def main() -> None:
    client, property_id = load_client()
    visitors = fetch_visitors(client, property_id)
    if not visitors:
        raise RuntimeError("GA4 returned no city-level visitor data that could be placed on the map.")

    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "date_range": f"all available data since {START_DATE}",
        "visitors": visitors,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(visitors)} visitor locations to {OUTPUT_PATH}.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001 - provide a concise workflow error
        print(f"Visitor map update failed: {error}", file=sys.stderr)
        raise
