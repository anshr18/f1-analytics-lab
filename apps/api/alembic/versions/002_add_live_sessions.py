"""Add live session tracking tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Live sessions table
    op.create_table(
        'live_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', UUID(as_uuid=True), sa.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('started_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('stopped_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('current_lap', sa.Integer(), nullable=True),
        sa.Column('session_status', sa.String(50), nullable=True),  # 'Started', 'Aborted', 'Finished', etc.
        sa.Column('track_status', sa.String(50), nullable=True),  # 'AllClear', 'Yellow', 'Red', 'SCDeployed', etc.
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()'), onupdate=sa.text('NOW()')),
    )

    # Live timing data (position updates)
    op.create_table(
        'live_timing',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('live_session_id', UUID(as_uuid=True), sa.ForeignKey('live_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('driver_id', sa.String(3), sa.ForeignKey('drivers.abbreviation', ondelete='CASCADE'), nullable=False),
        sa.Column('lap_number', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('gap_to_leader', sa.Float(), nullable=True),  # seconds
        sa.Column('gap_to_ahead', sa.Float(), nullable=True),  # seconds
        sa.Column('interval', sa.Float(), nullable=True),  # seconds to car ahead
        sa.Column('last_lap_time', sa.Float(), nullable=True),  # seconds
        sa.Column('sector1_time', sa.Float(), nullable=True),
        sa.Column('sector2_time', sa.Float(), nullable=True),
        sa.Column('sector3_time', sa.Float(), nullable=True),
        sa.Column('tyre_compound', sa.String(20), nullable=True),
        sa.Column('tyre_age', sa.Integer(), nullable=True),
        sa.Column('in_pit', sa.Boolean(), nullable=False, default=False),
        sa.Column('timestamp', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
    )

    # Live events (pit stops, incidents, etc.)
    op.create_table(
        'live_events',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('live_session_id', UUID(as_uuid=True), sa.ForeignKey('live_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),  # 'pit_stop', 'fastest_lap', 'overtake', 'incident', etc.
        sa.Column('lap_number', sa.Integer(), nullable=False),
        sa.Column('driver_id', sa.String(3), sa.ForeignKey('drivers.abbreviation', ondelete='CASCADE'), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(20), nullable=True),  # 'info', 'warning', 'critical'
        sa.Column('data', JSONB, nullable=False, server_default='{}'),
        sa.Column('timestamp', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
    )

    # WebSocket connections tracking
    op.create_table(
        'websocket_connections',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('connection_id', sa.String(100), nullable=False, unique=True),
        sa.Column('live_session_id', UUID(as_uuid=True), sa.ForeignKey('live_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(100), nullable=True),
        sa.Column('connected_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('disconnected_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
    )

    # Create indexes for performance
    op.create_index('idx_live_sessions_session_id', 'live_sessions', ['session_id'])
    op.create_index('idx_live_sessions_active', 'live_sessions', ['is_active'])
    op.create_index('idx_live_timing_session_lap', 'live_timing', ['live_session_id', 'lap_number'])
    op.create_index('idx_live_timing_driver', 'live_timing', ['driver_id'])
    op.create_index('idx_live_events_session', 'live_events', ['live_session_id'])
    op.create_index('idx_live_events_type', 'live_events', ['event_type'])
    op.create_index('idx_websocket_connections_session', 'websocket_connections', ['live_session_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_websocket_connections_session')
    op.drop_index('idx_live_events_type')
    op.drop_index('idx_live_events_session')
    op.drop_index('idx_live_timing_driver')
    op.drop_index('idx_live_timing_session_lap')
    op.drop_index('idx_live_sessions_active')
    op.drop_index('idx_live_sessions_session_id')

    # Drop tables
    op.drop_table('websocket_connections')
    op.drop_table('live_events')
    op.drop_table('live_timing')
    op.drop_table('live_sessions')
