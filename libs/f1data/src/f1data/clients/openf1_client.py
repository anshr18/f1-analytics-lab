"""
F1 Data - OpenF1 Client

Client for accessing F1 data via the OpenF1 API.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class OpenF1Client:
    """
    OpenF1 API client for real-time and historical F1 data.

    API Docs: https://openf1.org/
    """

    BASE_URL = "https://api.openf1.org/v1"

    def __init__(self, timeout: int = 30):
        """
        Initialize OpenF1 client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        logger.info("OpenF1 client initialized")

    def get_sessions(self, year: Optional[int] = None, session_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get sessions from OpenF1.

        Args:
            year: Optional year filter
            session_name: Optional session name filter (e.g., "Race", "Qualifying")

        Returns:
            List of session dictionaries
        """
        params = {}
        if year:
            params["year"] = year
        if session_name:
            params["session_name"] = session_name

        return self._get("/sessions", params=params)

    def get_laps(
        self, session_key: int, driver_number: Optional[int] = None, lap_number: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get lap data from OpenF1.

        Args:
            session_key: OpenF1 session key
            driver_number: Optional driver number filter
            lap_number: Optional lap number filter

        Returns:
            List of lap dictionaries
        """
        params = {"session_key": session_key}
        if driver_number:
            params["driver_number"] = driver_number
        if lap_number:
            params["lap_number"] = lap_number

        return self._get("/laps", params=params)

    def get_drivers(self, session_key: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get driver data from OpenF1.

        Args:
            session_key: Optional session key filter

        Returns:
            List of driver dictionaries
        """
        params = {}
        if session_key:
            params["session_key"] = session_key

        return self._get("/drivers", params=params)

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Make GET request to OpenF1 API.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response data

        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"OpenF1 API request failed: {e}")
            raise
