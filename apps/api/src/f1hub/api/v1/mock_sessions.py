"""
Mock Sessions Endpoint - For Testing Without Database
"""

from fastapi import APIRouter

router = APIRouter(prefix="/mock", tags=["mock"])


@router.get("/sessions")
def get_mock_sessions():
    """Return mock session data for testing live timing without database"""
    return {
        "seasons": [
            {
                "year": 2024,
                "meetings": [
                    {
                        "id": "test-abu-dhabi",
                        "name": "Abu Dhabi Grand Prix",
                        "location": "Yas Marina Circuit",
                        "sessions": [
                            {
                                "id": "test-session",
                                "name": "Race",
                                "type": "Race",
                                "date": "2024-12-08"
                            }
                        ]
                    },
                    {
                        "id": "test-monaco",
                        "name": "Monaco Grand Prix",
                        "location": "Circuit de Monaco",
                        "sessions": [
                            {
                                "id": "monaco-session",
                                "name": "Race",
                                "type": "Race",
                                "date": "2024-05-26"
                            }
                        ]
                    }
                ]
            }
        ]
    }
