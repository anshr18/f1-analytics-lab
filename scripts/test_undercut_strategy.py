#!/usr/bin/env python3
"""
Test Script for Undercut Strategy Predictor

Tests the undercut calculation API with real race data from Bahrain 2024.
"""

import requests
import json
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()

# API configuration
API_BASE = "http://localhost:8000/api/v1"

# Test scenario: VER trying to undercut LEC at Bahrain 2024
# This is a realistic scenario from the race
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
    console.print("\n[bold cyan]Testing Undercut Strategy API[/bold cyan]\n")

    # Display test scenario
    console.print("[bold]Test Scenario:[/bold]")
    console.print(f"  Session: Bahrain 2024 Race")
    console.print(f"  Attacking Driver: {TEST_REQUEST['attacking_driver']}")
    console.print(f"  Defending Driver: {TEST_REQUEST['defending_driver']}")
    console.print(f"  Current Lap: {TEST_REQUEST['current_lap']}")
    console.print(f"  Gap: {TEST_REQUEST['gap_seconds']}s")
    console.print(f"  Attacker Tyre Age: {TEST_REQUEST['tyre_age_attacker']} laps ({TEST_REQUEST['attacker_compound']})")
    console.print(f"  Defender Tyre Age: {TEST_REQUEST['tyre_age_defender']} laps ({TEST_REQUEST['defender_compound']})")

    # Make API request
    console.print(f"\n[bold]Calling:[/bold] POST {API_BASE}/strategy/undercut\n")

    try:
        response = requests.post(
            f"{API_BASE}/strategy/undercut",
            json=TEST_REQUEST,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()

            # Display results
            console.print("[bold green]✓ API Call Successful![/bold green]\n")

            # Strategy Summary
            console.print("[bold]Strategy Recommendation:[/bold]")
            console.print(f"  Optimal Pit Lap: [cyan]Lap {result['optimal_pit_lap']}[/cyan]")
            console.print(f"  Success Probability: [{'green' if result['success_probability'] > 0.5 else 'red'}]{result['success_probability']*100:.1f}%[/]")
            console.print(f"  Time Delta: [{'green' if result['time_delta'] > 0 else 'red'}]{result['time_delta']:+.2f}s[/]")
            console.print(f"  Attacker Outlap: {result['attacker_outlap']:.3f}s")
            console.print(f"  Defender Response: Lap {result['defender_response_lap']}")

            # Final Positions
            console.print(f"\n[bold]Predicted Final Positions:[/bold]")
            for driver, position in result['net_positions'].items():
                color = "green" if driver == TEST_REQUEST['attacking_driver'] and position == 1 else "yellow"
                console.print(f"  P{position}: [{color}]{driver}[/]")

            # Lap-by-lap breakdown (first 5 laps)
            console.print(f"\n[bold]Lap-by-Lap Breakdown (First 5 Laps):[/bold]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Lap", justify="right")
            table.add_column(f"{TEST_REQUEST['attacking_driver']} Time", justify="right")
            table.add_column(f"{TEST_REQUEST['defending_driver']} Time", justify="right")
            table.add_column("Delta", justify="right")
            table.add_column("Gap", justify="right")
            table.add_column(f"{TEST_REQUEST['attacking_driver']} Tyre", justify="right")
            table.add_column(f"{TEST_REQUEST['defending_driver']} Tyre", justify="right")

            for lap_data in result['lap_by_lap'][:5]:
                delta_color = "green" if lap_data['lap_delta'] < 0 else "red"
                gap_color = "green" if lap_data['cumulative_gap'] < TEST_REQUEST['gap_seconds'] else "yellow"

                table.add_row(
                    str(lap_data['lap']),
                    f"{lap_data['attacker_lap_time']:.3f}s",
                    f"{lap_data['defender_lap_time']:.3f}s",
                    f"[{delta_color}]{lap_data['lap_delta']:+.3f}s[/]",
                    f"[{gap_color}]{lap_data['cumulative_gap']:.2f}s[/]",
                    f"{lap_data['attacker_tyre_age']} laps",
                    f"{lap_data['defender_tyre_age']} laps"
                )

            console.print(table)

            # Verdict
            console.print(f"\n[bold]Verdict:[/bold]")
            if result['success_probability'] > 0.7:
                console.print("  [bold green]✓ UNDERCUT RECOMMENDED[/bold green]")
                console.print(f"  High probability ({result['success_probability']*100:.0f}%) of gaining position")
            elif result['success_probability'] > 0.4:
                console.print("  [bold yellow]⚠ UNDERCUT RISKY[/bold yellow]")
                console.print(f"  Moderate probability ({result['success_probability']*100:.0f}%) - situational call")
            else:
                console.print("  [bold red]✗ UNDERCUT NOT RECOMMENDED[/bold red]")
                console.print(f"  Low probability ({result['success_probability']*100:.0f}%) of success")

            return True

        else:
            console.print(f"[bold red]✗ API Error:[/bold red] {response.status_code}")
            console.print(response.text)
            return False

    except requests.exceptions.ConnectionError:
        console.print("[bold red]✗ Connection Error:[/bold red] Could not connect to API")
        console.print("Make sure the API is running on http://localhost:8000")
        return False
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {str(e)}")
        return False


if __name__ == "__main__":
    success = test_undercut_api()
    exit(0 if success else 1)
