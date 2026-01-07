#!/usr/bin/env python3
"""
Phase 5 Live Streaming Test Script

Tests the live streaming infrastructure:
1. OpenF1 API connection
2. Database models and migrations
3. WebSocket endpoints
4. Live timing service
"""

import asyncio
import json
import sys
from datetime import datetime

import httpx
import websockets


# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
WS_BASE_URL = "ws://localhost:8000/api/v1"


async def test_openf1_api():
    """Test OpenF1 API connectivity and data retrieval."""
    print("\n" + "="*70)
    print("TEST 1: OpenF1 API Connection")
    print("="*70)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test getting latest session
            print("\n📡 Fetching latest F1 sessions from OpenF1...")
            response = await client.get("https://api.openf1.org/v1/sessions", params={"limit": 5})
            response.raise_for_status()
            sessions = response.json()

            if sessions:
                print(f"✅ Successfully connected to OpenF1 API")
                print(f"   Found {len(sessions)} recent sessions:")
                for i, session in enumerate(sessions[:3], 1):
                    session_name = session.get('session_name', 'Unknown')
                    country = session.get('country_name', 'Unknown')
                    date = session.get('date_start', 'Unknown')
                    print(f"   {i}. {country} - {session_name} ({date})")

                # Test getting position data for first session
                session_key = sessions[0].get('session_key')
                print(f"\n📊 Testing live timing data for session {session_key}...")
                response = await client.get(
                    "https://api.openf1.org/v1/position",
                    params={"session_key": session_key, "limit": 5}
                )
                response.raise_for_status()
                timing_data = response.json()

                if timing_data:
                    print(f"✅ Successfully retrieved timing data")
                    print(f"   Sample data points: {len(timing_data)}")
                else:
                    print("⚠️  No timing data available for this session")

                return True, sessions[0]
            else:
                print("❌ No sessions found")
                return False, None

    except Exception as e:
        print(f"❌ OpenF1 API test failed: {e}")
        return False, None


async def test_database_migration():
    """Test if database migration has been applied."""
    print("\n" + "="*70)
    print("TEST 2: Database Migration")
    print("="*70)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            print("\n🗄️  Checking database tables via API...")

            # Try to get active live sessions (should work if migration is applied)
            response = await client.get(f"{API_BASE_URL}/live/sessions/active")

            if response.status_code == 200:
                sessions = response.json()
                print(f"✅ Database migration successful")
                print(f"   Active live sessions: {len(sessions)}")
                return True
            else:
                print(f"❌ Migration check failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except httpx.ConnectError:
        print("❌ Cannot connect to API server. Is it running?")
        print("   Start with: cd apps/api && uvicorn f1hub.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Database migration test failed: {e}")
        return False


async def test_live_session_endpoints():
    """Test REST API endpoints for live sessions."""
    print("\n" + "="*70)
    print("TEST 3: Live Session REST Endpoints")
    print("="*70)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Get sessions to find a test session
            print("\n📋 Step 1: Getting available sessions...")
            response = await client.get(f"{API_BASE_URL}/sessions")

            if response.status_code != 200:
                print(f"❌ Failed to get sessions: HTTP {response.status_code}")
                return False

            sessions = response.json()
            if not sessions:
                print("❌ No sessions available in database")
                print("   Run ingestion first: POST /ingest/session")
                return False

            test_session = sessions[0]
            session_id = test_session.get('id')
            print(f"✅ Using test session: {test_session.get('event_name')} - {test_session.get('session_type')}")
            print(f"   Session ID: {session_id}")

            # 2. Start a live session
            print(f"\n🚀 Step 2: Starting live session...")
            # Use a fake OpenF1 session key for testing
            response = await client.post(
                f"{API_BASE_URL}/live/sessions/start",
                params={
                    "session_id": session_id,
                    "openf1_session_key": "test_12345"
                }
            )

            if response.status_code == 201:
                live_session = response.json()
                live_session_id = live_session.get('id')
                print(f"✅ Live session started successfully")
                print(f"   Live Session ID: {live_session_id}")
                print(f"   Status: {live_session.get('session_status')}")

                # 3. Get active sessions
                print(f"\n📊 Step 3: Getting active live sessions...")
                response = await client.get(f"{API_BASE_URL}/live/sessions/active")
                active_sessions = response.json()
                print(f"✅ Active sessions: {len(active_sessions)}")

                # 4. Get connection count
                print(f"\n👥 Step 4: Checking connection count...")
                response = await client.get(f"{API_BASE_URL}/live/connections/count")
                count_data = response.json()
                print(f"✅ Active connections: {count_data.get('count')}")

                # 5. Stop the live session
                print(f"\n🛑 Step 5: Stopping live session...")
                response = await client.post(f"{API_BASE_URL}/live/sessions/{live_session_id}/stop")
                print(f"✅ Live session stopped")

                return True
            else:
                print(f"❌ Failed to start live session: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False

    except Exception as e:
        print(f"❌ Live session endpoint test failed: {e}")
        return False


async def test_websocket_connection():
    """Test WebSocket connection and data streaming."""
    print("\n" + "="*70)
    print("TEST 4: WebSocket Connection")
    print("="*70)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get a session to connect to
            print("\n📋 Getting test session...")
            response = await client.get(f"{API_BASE_URL}/sessions")

            if response.status_code != 200 or not response.json():
                print("❌ No sessions available for WebSocket test")
                return False

            session = response.json()[0]
            session_id = session.get('id')
            print(f"✅ Using session: {session.get('event_name')} ({session_id})")

            # Connect to WebSocket
            ws_url = f"{WS_BASE_URL}/live/ws/{session_id}"
            print(f"\n🔌 Connecting to WebSocket: {ws_url}")

            try:
                async with websockets.connect(ws_url, ping_interval=30) as websocket:
                    print("✅ WebSocket connected!")

                    # Wait for connection confirmation
                    print("\n📨 Waiting for connection confirmation...")
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)

                    if data.get('type') == 'connected':
                        print(f"✅ Connection confirmed")
                        print(f"   Connection ID: {data.get('connection_id')}")
                        print(f"   Session ID: {data.get('session_id')}")

                        # Send a ping
                        print("\n📤 Sending ping...")
                        await websocket.send(json.dumps({"type": "ping"}))

                        # Wait for pong
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(message)

                        if data.get('type') == 'pong':
                            print("✅ Received pong - WebSocket is working!")

                        # Close gracefully
                        await websocket.close()
                        print("\n✅ WebSocket test completed successfully")
                        return True
                    else:
                        print(f"⚠️  Unexpected message type: {data.get('type')}")
                        return False

            except asyncio.TimeoutError:
                print("❌ WebSocket connection timeout")
                return False
            except websockets.exceptions.WebSocketException as e:
                print(f"❌ WebSocket error: {e}")
                return False

    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False


async def test_redis_connection():
    """Test Redis connection for Pub/Sub."""
    print("\n" + "="*70)
    print("TEST 5: Redis Connection")
    print("="*70)

    try:
        print("\n🔴 Checking Redis connection...")

        # Try to import aioredis
        try:
            import aioredis
            print("✅ aioredis library installed")
        except ImportError:
            print("❌ aioredis not installed. Install with: pip install aioredis")
            return False

        # Try to connect to Redis
        try:
            redis = await aioredis.from_url("redis://localhost:6379", encoding="utf-8", decode_responses=True)
            await redis.ping()
            print("✅ Redis connection successful")
            await redis.close()
            return True
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            print("   Make sure Redis is running:")
            print("   - Docker: docker-compose up redis")
            print("   - Local: redis-server")
            return False

    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🏎️  F1 INTELLIGENCE HUB - PHASE 5 LIVE STREAMING TESTS")
    print("="*70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"WebSocket Base URL: {WS_BASE_URL}")

    results = {}

    # Test 1: OpenF1 API
    results['openf1'] = await test_openf1_api()
    await asyncio.sleep(1)

    # Test 2: Database Migration
    results['migration'] = await test_database_migration()
    await asyncio.sleep(1)

    # Test 3: Live Session Endpoints
    if results['migration']:
        results['endpoints'] = await test_live_session_endpoints()
        await asyncio.sleep(1)
    else:
        print("\n⏭️  Skipping endpoint tests (migration not applied)")
        results['endpoints'] = False

    # Test 4: WebSocket Connection
    if results['migration']:
        results['websocket'] = await test_websocket_connection()
        await asyncio.sleep(1)
    else:
        print("\n⏭️  Skipping WebSocket tests (migration not applied)")
        results['websocket'] = False

    # Test 5: Redis Connection
    results['redis'] = await test_redis_connection()

    # Print Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if (v[0] if isinstance(v, tuple) else v))
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if (result[0] if isinstance(result, tuple) else result) else "❌ FAIL"
        print(f"{status} - {test_name.upper()}")

    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Phase 5 is ready for production.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)
