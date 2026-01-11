"""
F1 Data - Jolpica Client

Client for accessing F1 historical data via Jolpica API (Ergast replacement).
"""

import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class JolpicaClient:
    """
    Jolpica API client for historical F1 data.

    Jolpica is the successor to the Ergast API.
    API Docs: https://ergast.com/mrd/
    """

    BASE_URL = "https://api.jolpi.ca/ergast/f1"

    def __init__(self, timeout: int = 30):
        """
        Initialize Jolpica client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        logger.info("Jolpica client initialized")

    def get_season(self, year: int) -> Dict[str, Any]:
        """
        Get season information.

        Args:
            year: Season year

        Returns:
            Season data dictionary
        """
        endpoint = f"/{year}.json"
        return self._get(endpoint)

    def get_races(self, year: int) -> List[Dict[str, Any]]:
        """
        Get races for a season.

        Args:
            year: Season year

        Returns:
            List of race dictionaries
        """
        endpoint = f"/{year}.json"
        data = self._get(endpoint)

        # Extract races from Ergast format
        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        return races

    def get_race_results(self, year: int, round_number: int) -> Dict[str, Any]:
        """
        Get race results.

        Args:
            year: Season year
            round_number: Round number

        Returns:
            Race results dictionary
        """
        endpoint = f"/{year}/{round_number}/results.json"
        return self._get(endpoint)

    def get_drivers(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get drivers.

        Args:
            year: Optional year filter

        Returns:
            List of driver dictionaries
        """
        if year:
            endpoint = f"/{year}/drivers.json"
        else:
            endpoint = "/drivers.json"

        data = self._get(endpoint)

        # Extract drivers from Ergast format
        drivers = data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])
        return drivers

    def get_constructors(self, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get constructors.

        Args:
            year: Optional year filter

        Returns:
            List of constructor dictionaries
        """
        if year:
            endpoint = f"/{year}/constructors.json"
        else:
            endpoint = "/constructors.json"

        data = self._get(endpoint)

        # Extract constructors from Ergast format
        constructors = data.get("MRData", {}).get("ConstructorTable", {}).get("Constructors", [])
        return constructors

    def _get(self, endpoint: str) -> Dict[str, Any]:
        """
        Make GET request to Jolpica API.

        Args:
            endpoint: API endpoint

        Returns:
            API response data

        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Jolpica API request failed: {e}")
            raise
