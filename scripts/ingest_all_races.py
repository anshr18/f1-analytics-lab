#!/usr/bin/env python3
"""
Ingest All F1 Races Script

This script ingests all F1 race data from specified seasons (default: 2023-2024).
It uses FastF1 to fetch data and stores it in the database.

Usage:
    python scripts/ingest_all_races.py

    # Ingest specific years
    python scripts/ingest_all_races.py --years 2023 2024

    # Ingest only races (skip practice/qualifying)
    python scripts/ingest_all_races.py --races-only

    # Skip already ingested sessions
    python scripts/ingest_all_races.py --skip-existing
"""

import argparse
import sys
import os
import time
from datetime import datetime
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Add the API source to path
sys.path.insert(0, str(PROJECT_ROOT / 'apps' / 'api' / 'src'))
sys.path.insert(0, str(PROJECT_ROOT / 'libs' / 'f1data' / 'src'))

# Set environment variables for local development BEFORE importing settings
CACHE_DIR = PROJECT_ROOT / 'data' / 'fastf1_cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('FASTF1_CACHE_DIR', str(CACHE_DIR))
os.environ.setdefault('DATABASE_URL', 'postgresql://f1hub:f1hub_dev_password@localhost:5432/f1hub')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import after path setup
from f1hub.db.models import Session as DBSession, Event, Season
from f1hub.core.config import get_settings
from f1hub.services.fastf1_ingest import FastF1IngestService


def setup_fastf1_cache():
    """Configure FastF1 cache directory"""
    import fastf1
    fastf1.Cache.enable_cache(str(CACHE_DIR))
    print(f"FastF1 cache configured: {CACHE_DIR}")


def get_race_calendar(year: int) -> list:
    """Get the F1 race calendar for a given year using FastF1"""
    import fastf1

    try:
        schedule = fastf1.get_event_schedule(year)
        events = []

        for _, row in schedule.iterrows():
            # Skip testing events
            if 'testing' in row['EventName'].lower():
                continue
            if row['RoundNumber'] == 0:
                continue

            events.append({
                'round': int(row['RoundNumber']),
                'name': row['EventName'],
                'country': row.get('Country', 'Unknown'),
                'date': row.get('EventDate', None),
            })

        return sorted(events, key=lambda x: x['round'])
    except Exception as e:
        print(f"Error fetching calendar for {year}: {e}")
        return []


def ingest_session(service, year: int, round_num: int, session_type: str, event_name: str) -> bool:
    """Ingest a single session, return True if successful"""
    try:
        session_id = service.ingest_session(
            year=year,
            round_number=round_num,
            session_type=session_type
        )
        return True, session_id
    except Exception as e:
        error_msg = str(e)
        # Common expected errors
        if "No data available" in error_msg or "not found" in error_msg.lower():
            return None, "No data available"
        return False, error_msg


def main():
    parser = argparse.ArgumentParser(description='Ingest F1 race data')
    parser.add_argument('--years', nargs='+', type=int, default=[2020, 2021, 2022, 2023, 2024],
                        help='Years to ingest (default: 2020-2024)')
    parser.add_argument('--races-only', action='store_true',
                        help='Only ingest Race sessions (skip FP, Q, Sprint)')
    parser.add_argument('--include-practice', action='store_true',
                        help='Include practice sessions (FP1, FP2, FP3)')
    parser.add_argument('--skip-existing', action='store_true',
                        help='Skip sessions that are already ingested')
    parser.add_argument('--start-round', type=int, default=1,
                        help='Start from this round number')
    args = parser.parse_args()

    # Setup FastF1 cache before any data fetching
    setup_fastf1_cache()

    print("=" * 70)
    print("F1 ANALYTICS LAB - BULK DATA INGESTION")
    print("=" * 70)
    print(f"Years to ingest: {args.years}")
    print(f"Races only: {args.races_only}")
    print(f"Include practice: {args.include_practice}")
    print(f"Skip existing: {args.skip_existing}")
    print(f"Start round: {args.start_round}")
    print("=" * 70)
    print()

    # Setup database connection
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    # Create service
    service = FastF1IngestService(db)

    # Define session types to ingest
    if args.races_only:
        session_types = ['Race']
    elif args.include_practice:
        session_types = ['FP1', 'FP2', 'FP3', 'Q', 'Sprint', 'Race']
    else:
        session_types = ['Q', 'Sprint', 'Race']

    # Track statistics
    stats = {
        'total': 0,
        'success': 0,
        'skipped': 0,
        'failed': 0,
        'no_data': 0,
    }

    start_time = time.time()

    for year in args.years:
        print(f"\n{'='*70}")
        print(f"YEAR: {year}")
        print(f"{'='*70}")

        # Get race calendar
        print(f"Fetching {year} calendar...")
        events = get_race_calendar(year)

        if not events:
            print(f"  No events found for {year}")
            continue

        print(f"  Found {len(events)} events")
        print()

        for event in events:
            round_num = event['round']
            event_name = event['name']

            # Skip if before start round
            if round_num < args.start_round:
                continue

            print(f"\nRound {round_num}: {event_name}")
            print("-" * 50)

            for session_type in session_types:
                stats['total'] += 1
                label = f"  {session_type.ljust(6)}"

                # Check if already exists (if skip_existing enabled)
                if args.skip_existing:
                    existing = db.query(DBSession).join(Event).filter(
                        Event.season_year == year,
                        Event.round_number == round_num,
                        DBSession.session_type == session_type,
                        DBSession.is_ingested == True
                    ).first()

                    if existing:
                        print(f"{label} ⏭️  Already ingested")
                        stats['skipped'] += 1
                        continue

                print(f"{label} ", end="", flush=True)

                success, result = ingest_session(service, year, round_num, session_type, event_name)

                if success is True:
                    print(f"✅ Ingested (ID: {str(result)[:8]}...)")
                    stats['success'] += 1
                elif success is None:
                    print(f"⏭️  {result}")
                    stats['no_data'] += 1
                else:
                    print(f"❌ Failed: {result[:50]}...")
                    stats['failed'] += 1

                # Small delay to avoid overwhelming FastF1
                time.sleep(0.5)

            # Commit after each event
            db.commit()

    # Final statistics
    elapsed = time.time() - start_time

    print("\n")
    print("=" * 70)
    print("INGESTION COMPLETE")
    print("=" * 70)
    print(f"Total sessions attempted: {stats['total']}")
    print(f"  ✅ Successfully ingested: {stats['success']}")
    print(f"  ⏭️  Skipped (existing):    {stats['skipped']}")
    print(f"  ⏭️  No data available:     {stats['no_data']}")
    print(f"  ❌ Failed:                 {stats['failed']}")
    print(f"\nTime elapsed: {elapsed/60:.1f} minutes")
    print("=" * 70)

    db.close()


if __name__ == "__main__":
    main()
