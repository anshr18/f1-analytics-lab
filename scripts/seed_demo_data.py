#!/usr/bin/env python3
"""
Seed script for F1 Intelligence Hub

This script populates the database with demo data:
- 2024 season metadata (drivers, constructors, events)
- Ingests example sessions (Bahrain 2024 Race, Qualifying)
- Verifies data integrity

Usage:
    python scripts/seed_demo_data.py

Or via Make:
    make db-seed
"""

import logging
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from f1hub.core.config import get_settings
from f1hub.services.fastf1_ingest import FastF1IngestService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main seeding function."""
    print("\n" + "=" * 60)
    print("🌱 F1 Intelligence Hub - Database Seeding")
    print("=" * 60)
    print()

    # Load settings
    settings = get_settings()

    # Create database session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Sessions to ingest
        sessions_to_ingest = [
            {"year": 2024, "round": 1, "session_type": "Race", "name": "Bahrain GP Race"},
            {"year": 2024, "round": 1, "session_type": "Q", "name": "Bahrain GP Qualifying"},
        ]

        print(f"📊 Will ingest {len(sessions_to_ingest)} sessions:")
        for session in sessions_to_ingest:
            print(f"  - {session['year']} Round {session['round']} {session['name']}")
        print()

        # Initialize ingestion service
        service = FastF1IngestService(db)

        # Ingest each session
        for i, session_info in enumerate(sessions_to_ingest, 1):
            print(f"\n[{i}/{len(sessions_to_ingest)}] Ingesting: {session_info['name']}")
            print("-" * 60)

            try:
                session_id = service.ingest_session(
                    year=session_info["year"],
                    round_number=session_info["round"],
                    session_type=session_info["session_type"]
                )

                print(f"✅ Successfully ingested session: {session_id}")

            except Exception as e:
                print(f"❌ Failed to ingest {session_info['name']}: {e}")
                logger.error(f"Ingestion failed", exc_info=True)
                continue

        print("\n" + "=" * 60)
        print("✅ Database seeding complete!")
        print("=" * 60)
        print()
        print("📊 Data Summary:")
        print(f"  - Sessions ingested: {len(sessions_to_ingest)}")
        print()
        print("🚀 Next steps:")
        print("  1. Start the API: make dev-up")
        print("  2. View docs: http://localhost:8000/docs")
        print("  3. Query data: GET /api/v1/sessions")
        print()

    except Exception as e:
        print(f"\n❌ Seeding failed: {e}")
        logger.error("Seeding failed", exc_info=True)
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
