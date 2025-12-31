#!/usr/bin/env python3
"""
Test Race Simulation API

Tests the race simulation endpoint with a realistic scenario.
"""

import requests
import json
from typing import Dict, List

API_BASE_URL = "http://localhost:8000/api/v1"

# Test scenario: 8-driver race with different pit strategies
TEST_REQUEST = {
    "session_id": "94476e2f-02e7-425c-a83b-53cac8c82bb6",  # Bahrain 2024 Race
    "total_laps": 57,
    "drivers": ["VER", "LEC", "PER", "SAI", "RUS", "HAM", "NOR", "ALO"],
    "pit_strategies": {
        "VER": [18, 38],  # 2-stop strategy
        "LEC": [20, 40],  # 2-stop strategy (later)
        "PER": [15, 35],  # 2-stop strategy (early)
        "SAI": [25],      # 1-stop strategy
        "RUS": [22, 42],  # 2-stop strategy
        "HAM": [19, 39],  # 2-stop strategy
        "NOR": [17, 37],  # 2-stop strategy
        "ALO": [30],      # 1-stop strategy (late)
    }
}


def test_race_simulation():
    """Test the race simulation endpoint"""

    print("=" * 80)
    print("RACE SIMULATION API TEST")
    print("=" * 80)
    print()

    # Display test configuration
    print("📋 Test Configuration:")
    print(f"   Session ID: {TEST_REQUEST['session_id']}")
    print(f"   Total Laps: {TEST_REQUEST['total_laps']}")
    print(f"   Drivers: {len(TEST_REQUEST['drivers'])}")
    print()

    print("🔧 Pit Strategies:")
    for driver, stops in TEST_REQUEST["pit_strategies"].items():
        print(f"   {driver}: Laps {', '.join(map(str, stops))} ({len(stops)}-stop)")
    print()

    # Make API request
    print("🚀 Sending request to API...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/strategy/race-simulation",
            json=TEST_REQUEST,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            print()

            # Display results
            print("=" * 80)
            print("🏁 RACE RESULTS")
            print("=" * 80)
            print()

            # Final Classification
            print("🏆 Final Classification:")
            classification = sorted(
                result["final_classification"].items(),
                key=lambda x: x[1]
            )
            for position, (driver, pos) in enumerate(classification, 1):
                stops = result["total_pit_stops"][driver]
                medal = "🥇" if position == 1 else "🥈" if position == 2 else "🥉" if position == 3 else "  "
                print(f"   {medal} P{pos} - {driver} ({stops}-stop)")
            print()

            # Fastest Lap
            print("⚡ Fastest Lap:")
            fastest = result["fastest_lap"]
            print(f"   {fastest['driver']} - Lap {fastest['lap']}")
            print()

            # Race Summary
            print("📊 Race Summary:")
            print(f"   {result['summary']}")
            print()

            # Lap-by-Lap Sample (first 5 laps)
            print("📈 Lap-by-Lap Positions (First 5 Laps):")
            for i, lap_data in enumerate(result["lap_by_lap_positions"][:5], 1):
                positions = sorted(lap_data.items(), key=lambda x: x[1])
                position_str = " | ".join([f"{d}:P{p}" for d, p in positions])
                print(f"   Lap {i}: {position_str}")
            print(f"   ... ({len(result['lap_by_lap_positions'])} total laps)")
            print()

            # Position Changes Analysis
            print("📊 Position Changes:")
            start_positions = result["lap_by_lap_positions"][0]
            end_positions = result["final_classification"]
            for driver in TEST_REQUEST["drivers"]:
                start_pos = start_positions[driver]
                end_pos = end_positions[driver]
                change = start_pos - end_pos

                if change > 0:
                    print(f"   {driver}: P{start_pos} → P{end_pos} (↑{change} positions gained)")
                elif change < 0:
                    print(f"   {driver}: P{start_pos} → P{end_pos} (↓{abs(change)} positions lost)")
                else:
                    print(f"   {driver}: P{start_pos} → P{end_pos} (no change)")
            print()

            # Strategy Effectiveness
            print("🎯 Strategy Effectiveness:")
            one_stop_drivers = [d for d, s in TEST_REQUEST["pit_strategies"].items() if len(s) == 1]
            two_stop_drivers = [d for d, s in TEST_REQUEST["pit_strategies"].items() if len(s) == 2]

            if one_stop_drivers:
                print(f"   1-Stop Strategy ({len(one_stop_drivers)} drivers):")
                for driver in one_stop_drivers:
                    pos = end_positions[driver]
                    print(f"      {driver}: P{pos}")

            if two_stop_drivers:
                print(f"   2-Stop Strategy ({len(two_stop_drivers)} drivers):")
                for driver in two_stop_drivers:
                    pos = end_positions[driver]
                    print(f"      {driver}: P{pos}")
            print()

            print("=" * 80)
            print("✅ RACE SIMULATION TEST PASSED")
            print("=" * 80)

        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.Timeout:
        print("❌ Request timed out (30s)")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the API server running?")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    test_race_simulation()
