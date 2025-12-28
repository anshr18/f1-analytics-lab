#!/usr/bin/env python3
"""
Test Script for Undercut Strategy Predictor

Tests the undercut calculation API with real race data from Bahrain 2024.
"""

import requests
import json

# API configuration
API_BASE = "http://localhost:8000/api/v1"

# Test scenario: VER trying to undercut LEC at Bahrain 2024
TEST_REQUEST = {
    "session_id": "94476e2f-02e7-425c-a83b-53cac8c82bb6",  # Bahrain 2024 Race
    "attacking_driver": "VER",
    "defending_driver": "LEC",
    "current_lap": 25,
    "gap_seconds": 3.5,
    "tyre_age_attacker": 15,
    "tyre_age_defender": 12,
    "attacker_compound": "SOFT",
    "defender_compound": "MEDIUM",
    "track_status": "GREEN"
}


def test_undercut_api():
    """Test the undercut strategy API endpoint"""
    print("\n" + "="*70)
    print("TESTING UNDERCUT STRATEGY API")
    print("="*70 + "\n")

    # Display test scenario
    print("Test Scenario:")
    print(f"  Session: Bahrain 2024 Race")
    print(f"  Attacking Driver: {TEST_REQUEST['attacking_driver']}")
    print(f"  Defending Driver: {TEST_REQUEST['defending_driver']}")
    print(f"  Current Lap: {TEST_REQUEST['current_lap']}")
    print(f"  Gap: {TEST_REQUEST['gap_seconds']}s")
    print(f"  Attacker Tyre Age: {TEST_REQUEST['tyre_age_attacker']} laps ({TEST_REQUEST['attacker_compound']})")
    print(f"  Defender Tyre Age: {TEST_REQUEST['tyre_age_defender']} laps ({TEST_REQUEST['defender_compound']})")

    # Make API request
    print(f"\nCalling: POST {API_BASE}/strategy/undercut\n")

    try:
        response = requests.post(
            f"{API_BASE}/strategy/undercut",
            json=TEST_REQUEST,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()

            # Display results
            print("✓ API Call Successful!\n")

            # Strategy Summary
            print("Strategy Recommendation:")
            print(f"  Optimal Pit Lap: Lap {result['optimal_pit_lap']}")
            print(f"  Success Probability: {result['success_probability']*100:.1f}%")
            print(f"  Time Delta: {result['time_delta']:+.2f}s")
            print(f"  Attacker Outlap: {result['attacker_outlap']:.3f}s")
            print(f"  Defender Response: Lap {result['defender_response_lap']}")

            # Final Positions
            print(f"\nPredicted Final Positions:")
            for driver, position in result['net_positions'].items():
                marker = "★" if driver == TEST_REQUEST['attacking_driver'] and position == 1 else " "
                print(f"  {marker} P{position}: {driver}")

            # Lap-by-lap breakdown (first 5 laps)
            print(f"\nLap-by-Lap Breakdown (First 5 Laps):")
            print(f"{'Lap':<6} {TEST_REQUEST['attacking_driver']+' Time':<12} {TEST_REQUEST['defending_driver']+' Time':<12} {'Delta':<10} {'Gap':<10} {TEST_REQUEST['attacking_driver']+' Tyre':<12} {TEST_REQUEST['defending_driver']+' Tyre':<12}")
            print("-"*70)

            for lap_data in result['lap_by_lap'][:5]:
                print(
                    f"{lap_data['lap']:<6} "
                    f"{lap_data['attacker_lap_time']:>11.3f}s "
                    f"{lap_data['defender_lap_time']:>11.3f}s "
                    f"{lap_data['lap_delta']:>9.3f}s "
                    f"{lap_data['cumulative_gap']:>9.2f}s "
                    f"{lap_data['attacker_tyre_age']:>11} laps "
                    f"{lap_data['defender_tyre_age']:>11} laps"
                )

            # Verdict
            print(f"\nVerdict:")
            if result['success_probability'] > 0.7:
                print("  ✓ UNDERCUT RECOMMENDED")
                print(f"  High probability ({result['success_probability']*100:.0f}%) of gaining position")
            elif result['success_probability'] > 0.4:
                print("  ⚠ UNDERCUT RISKY")
                print(f"  Moderate probability ({result['success_probability']*100:.0f}%) - situational call")
            else:
                print("  ✗ UNDERCUT NOT RECOMMENDED")
                print(f"  Low probability ({result['success_probability']*100:.0f}%) of success")

            print("\n" + "="*70 + "\n")
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
    success = test_undercut_api()
    exit(0 if success else 1)
