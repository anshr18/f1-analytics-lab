#!/usr/bin/env python3
"""
Test Script for Safety Car Strategy Recommender

Tests the safety car analysis API with a realistic F1 scenario.
Simulates a safety car period at Bahrain 2024 GP.
"""

import requests
import json

# API configuration
API_BASE = "http://localhost:8000/api/v1"

# Test scenario: Safety car deployed at lap 35 of 57 at Bahrain 2024
# Realistic driver states based on typical F1 race conditions
TEST_REQUEST = {
    "session_id": "94476e2f-02e7-425c-a83b-53cac8c82bb6",  # Bahrain 2024 Race
    "safety_car_lap": 35,
    "total_laps": 57,
    "track_status": "SC",
    "driver_states": [
        # P1: VER - Leader on old tires (18 laps)
        {
            "driver_id": "VER",
            "position": 1,
            "tyre_age": 18,
            "compound": "MEDIUM",
            "gap_to_leader": 0.0,
            "gap_to_next": 0.0,
        },
        # P2: LEC - 2nd place on fresher tires (15 laps)
        {
            "driver_id": "LEC",
            "position": 2,
            "tyre_age": 15,
            "compound": "MEDIUM",
            "gap_to_leader": 2.5,
            "gap_to_next": 2.5,
        },
        # P3: PER - 3rd on very old tires (22 laps)
        {
            "driver_id": "PER",
            "position": 3,
            "tyre_age": 22,
            "compound": "HARD",
            "gap_to_leader": 5.8,
            "gap_to_next": 3.3,
        },
        # P4: SAI - 4th on fresh tires (8 laps)
        {
            "driver_id": "SAI",
            "position": 4,
            "tyre_age": 8,
            "compound": "SOFT",
            "gap_to_leader": 8.2,
            "gap_to_next": 2.4,
        },
        # P5: NOR - 5th on medium tires (16 laps)
        {
            "driver_id": "NOR",
            "position": 5,
            "tyre_age": 16,
            "compound": "MEDIUM",
            "gap_to_leader": 12.1,
            "gap_to_next": 3.9,
        },
        # P6: HAM - 6th on old hard tires (20 laps)
        {
            "driver_id": "HAM",
            "position": 6,
            "tyre_age": 20,
            "compound": "HARD",
            "gap_to_leader": 15.5,
            "gap_to_next": 3.4,
        },
        # P7: RUS - 7th on very fresh tires (3 laps, just pitted)
        {
            "driver_id": "RUS",
            "position": 7,
            "tyre_age": 3,
            "compound": "SOFT",
            "gap_to_leader": 18.2,
            "gap_to_next": 2.7,
        },
        # P8: ALO - 8th on medium age tires (14 laps)
        {
            "driver_id": "ALO",
            "position": 8,
            "tyre_age": 14,
            "compound": "MEDIUM",
            "gap_to_leader": 22.4,
            "gap_to_next": 4.2,
        },
    ],
}


def test_safety_car_api():
    """Test the safety car strategy API endpoint"""
    print("\n" + "=" * 70)
    print("TESTING SAFETY CAR STRATEGY RECOMMENDER")
    print("=" * 70 + "\n")

    # Display test scenario
    print("Test Scenario:")
    print(f"  Race: Bahrain 2024")
    print(f"  Safety Car Lap: {TEST_REQUEST['safety_car_lap']}")
    print(f"  Total Laps: {TEST_REQUEST['total_laps']}")
    print(f"  Laps Remaining: {TEST_REQUEST['total_laps'] - TEST_REQUEST['safety_car_lap']}")
    print(f"  Track Status: {TEST_REQUEST['track_status']}")
    print(f"  Drivers in Field: {len(TEST_REQUEST['driver_states'])}")

    print("\nCurrent Field State:")
    print(f"{'Pos':<5} {'Driver':<8} {'Tyre':<10} {'Age':<8} {'Gap to Leader':<15}")
    print("-" * 50)
    for driver in TEST_REQUEST["driver_states"]:
        print(
            f"P{driver['position']:<4} {driver['driver_id']:<8} "
            f"{driver['compound']:<10} {driver['tyre_age']:<8} "
            f"{driver['gap_to_leader']:>14.1f}s"
        )

    # Make API request
    print(f"\nCalling: POST {API_BASE}/strategy/safety-car\n")

    try:
        response = requests.post(
            f"{API_BASE}/strategy/safety-car", json=TEST_REQUEST, timeout=30
        )

        if response.status_code == 200:
            result = response.json()

            # Display results
            print("✓ API Call Successful!\n")

            # Field Summary
            print("=" * 70)
            print("FIELD SUMMARY")
            print("=" * 70)
            summary = result["field_summary"]
            print(f"  Total Drivers: {summary['total_drivers']}")
            print(f"  Average Tyre Age: {summary['avg_tyre_age']:.1f} laps")
            print(f"  Drivers on Old Tyres: {summary['drivers_on_old_tyres']}")
            print(f"  Drivers on Fresh Tyres: {summary['drivers_on_fresh_tyres']}")
            print(f"  Laps Remaining: {summary['laps_remaining']}")
            print(
                f"  Pit Window Advantage: {'Yes' if summary['pit_window_advantage'] else 'No'} (SC pit ~18s vs normal ~22s)"
            )

            # Strategic Overview
            print("\n" + "=" * 70)
            print("STRATEGIC OVERVIEW")
            print("=" * 70)
            print(
                f"  Drivers Who Should PIT: {', '.join(result['drivers_who_should_pit']) or 'None'}"
            )
            print(
                f"  Drivers Who Should STAY: {', '.join(result['drivers_who_should_stay']) or 'None'}"
            )

            # Individual Decisions
            print("\n" + "=" * 70)
            print("DRIVER-BY-DRIVER RECOMMENDATIONS")
            print("=" * 70)

            for decision in result["decisions"]:
                # Color code by recommendation
                if decision["recommendation"] == "PIT":
                    icon = "⬇️  PIT"
                    color = "\033[92m"  # Green
                elif decision["recommendation"] == "STAY_OUT":
                    icon = "⬆️  STAY"
                    color = "\033[94m"  # Blue
                else:
                    icon = "⚠️  RISKY"
                    color = "\033[93m"  # Yellow
                reset = "\033[0m"

                print(
                    f"\nP{decision['current_position']} {decision['driver_id']} - {color}{icon}{reset}"
                )
                print(f"  Confidence: {decision['confidence']*100:.0f}%")
                print(
                    f"  If PIT: P{decision['predicted_position_if_pit']} "
                    f"({'↑' if decision['position_gain_if_pit'] > 0 else '↓' if decision['position_loss_if_pit'] > 0 else '→'}"
                    f"{'+' + str(decision['position_gain_if_pit']) if decision['position_gain_if_pit'] > 0 else '-' + str(decision['position_loss_if_pit']) if decision['position_loss_if_pit'] > 0 else '±0'})"
                )
                print(f"  If STAY: P{decision['predicted_position_if_stay']}")
                print(
                    f"  Tyre Advantage: +{decision['tyre_advantage']} laps fresher than average"
                )
                print(f"  Reasoning: {decision['reasoning']}")

            # Summary verdict
            print("\n" + "=" * 70)
            print("VERDICT")
            print("=" * 70)
            pit_count = len(result["drivers_who_should_pit"])
            stay_count = len(result["drivers_who_should_stay"])

            if pit_count > stay_count:
                print(
                    f"  🏁 Majority ({pit_count}/{len(result['decisions'])}) should PIT - good opportunity!"
                )
            elif stay_count > pit_count:
                print(
                    f"  🏁 Majority ({stay_count}/{len(result['decisions'])}) should STAY - tire advantage minimal"
                )
            else:
                print(
                    "  🏁 Field split on strategy - interesting battle ahead!"
                )

            print("\n" + "=" * 70 + "\n")
            return True

        else:
            print(f"✗ API Error: {response.status_code}")
            print(response.text)
            return False

    except requests.exceptions.ConnectionError:
        print("✗ Connection Error: Could not connect to API")
        print("Make sure the API is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_safety_car_api()
    exit(0 if success else 1)
