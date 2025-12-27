"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-03-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # ========================================================================
    # Core Tables
    # ========================================================================

    # seasons
    op.create_table(
        'seasons',
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('year', name=op.f('pk_seasons'))
    )

    # drivers
    op.create_table(
        'drivers',
        sa.Column('driver_id', sa.String(length=50), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('abbreviation', sa.String(length=3), nullable=False),
        sa.Column('number', sa.Integer(), nullable=True),
        sa.Column('country', sa.String(length=3), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('driver_id', name=op.f('pk_drivers'))
    )
    op.create_index(op.f('ix_drivers_abbreviation'), 'drivers', ['abbreviation'], unique=False)

    # constructors
    op.create_table(
        'constructors',
        sa.Column('constructor_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('country', sa.String(length=3), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('constructor_id', name=op.f('pk_constructors'))
    )

    # events
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('season_year', sa.Integer(), nullable=False),
        sa.Column('round_number', sa.Integer(), nullable=False),
        sa.Column('event_name', sa.String(length=100), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('location', sa.String(length=100), nullable=False),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['season_year'], ['seasons.year'], name=op.f('fk_events_season_year_seasons')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_events'))
    )
    op.create_index(op.f('ix_events_season_year'), 'events', ['season_year'], unique=False)
    op.create_index(op.f('ix_events_round_number'), 'events', ['round_number'], unique=False)

    # sessions
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_type', sa.String(length=20), nullable=False),
        sa.Column('session_date', sa.Date(), nullable=False),
        sa.Column('is_ingested', sa.Boolean(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], name=op.f('fk_sessions_event_id_events')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_sessions'))
    )
    op.create_index(op.f('ix_sessions_event_id'), 'sessions', ['event_id'], unique=False)
    op.create_index(op.f('ix_sessions_session_type'), 'sessions', ['session_type'], unique=False)

    # ========================================================================
    # Timing Tables
    # ========================================================================

    # stints (create before laps due to FK)
    op.create_table(
        'stints',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('driver_id', sa.String(length=50), nullable=False),
        sa.Column('stint_number', sa.Integer(), nullable=False),
        sa.Column('compound', sa.String(length=20), nullable=False),
        sa.Column('lap_start', sa.Integer(), nullable=False),
        sa.Column('lap_end', sa.Integer(), nullable=True),
        sa.Column('total_laps', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], name=op.f('fk_stints_session_id_sessions')),
        sa.ForeignKeyConstraint(['driver_id'], ['drivers.driver_id'], name=op.f('fk_stints_driver_id_drivers')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_stints'))
    )
    op.create_index(op.f('ix_stints_session_id'), 'stints', ['session_id'], unique=False)
    op.create_index(op.f('ix_stints_driver_id'), 'stints', ['driver_id'], unique=False)

    # laps
    op.create_table(
        'laps',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('driver_id', sa.String(length=50), nullable=False),
        sa.Column('lap_number', sa.Integer(), nullable=False),
        sa.Column('lap_time', sa.Interval(), nullable=True),
        sa.Column('sector_1_time', sa.Interval(), nullable=True),
        sa.Column('sector_2_time', sa.Interval(), nullable=True),
        sa.Column('sector_3_time', sa.Interval(), nullable=True),
        sa.Column('compound', sa.String(length=20), nullable=True),
        sa.Column('tyre_life', sa.Integer(), nullable=True),
        sa.Column('stint_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('track_status', sa.String(length=20), nullable=True),
        sa.Column('is_personal_best', sa.Boolean(), nullable=True),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=True),
        sa.Column('is_pit_out_lap', sa.Boolean(), nullable=True),
        sa.Column('is_pit_in_lap', sa.Boolean(), nullable=True),
        sa.Column('telemetry', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], name=op.f('fk_laps_session_id_sessions')),
        sa.ForeignKeyConstraint(['driver_id'], ['drivers.driver_id'], name=op.f('fk_laps_driver_id_drivers')),
        sa.ForeignKeyConstraint(['stint_id'], ['stints.id'], name=op.f('fk_laps_stint_id_stints')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_laps'))
    )
    op.create_index(op.f('ix_laps_session_id'), 'laps', ['session_id'], unique=False)
    op.create_index(op.f('ix_laps_driver_id'), 'laps', ['driver_id'], unique=False)
    op.create_index(op.f('ix_laps_lap_number'), 'laps', ['lap_number'], unique=False)

    # ========================================================================
    # Track Status Tables
    # ========================================================================

    # race_control
    op.create_table(
        'race_control',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('flag', sa.String(length=20), nullable=True),
        sa.Column('scope', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], name=op.f('fk_race_control_session_id_sessions')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_race_control'))
    )
    op.create_index(op.f('ix_race_control_session_id'), 'race_control', ['session_id'], unique=False)

    # incidents
    op.create_table(
        'incidents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('driver_id', sa.String(length=50), nullable=True),
        sa.Column('incident_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('lap_number', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], name=op.f('fk_incidents_session_id_sessions')),
        sa.ForeignKeyConstraint(['driver_id'], ['drivers.driver_id'], name=op.f('fk_incidents_driver_id_drivers')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_incidents'))
    )
    op.create_index(op.f('ix_incidents_session_id'), 'incidents', ['session_id'], unique=False)

    # ========================================================================
    # Feature Tables
    # ========================================================================

    # lap_features
    op.create_table(
        'lap_features',
        sa.Column('lap_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('delta_to_leader', sa.Float(), nullable=True),
        sa.Column('delta_to_ahead', sa.Float(), nullable=True),
        sa.Column('delta_to_personal_best', sa.Float(), nullable=True),
        sa.Column('tyre_age', sa.Integer(), nullable=True),
        sa.Column('compound_code', sa.Integer(), nullable=True),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.Column('positions_gained', sa.Integer(), nullable=True),
        sa.Column('track_status_code', sa.Integer(), nullable=True),
        sa.Column('extra_features', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['lap_id'], ['laps.id'], name=op.f('fk_lap_features_lap_id_laps')),
        sa.PrimaryKeyConstraint('lap_id', name=op.f('pk_lap_features'))
    )

    # stint_features
    op.create_table(
        'stint_features',
        sa.Column('stint_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('avg_lap_time', sa.Float(), nullable=True),
        sa.Column('fastest_lap_time', sa.Float(), nullable=True),
        sa.Column('slowest_lap_time', sa.Float(), nullable=True),
        sa.Column('deg_per_lap', sa.Float(), nullable=True),
        sa.Column('deg_r_squared', sa.Float(), nullable=True),
        sa.Column('fuel_corrected_avg', sa.Float(), nullable=True),
        sa.Column('extra_features', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['stint_id'], ['stints.id'], name=op.f('fk_stint_features_stint_id_stints')),
        sa.PrimaryKeyConstraint('stint_id', name=op.f('pk_stint_features'))
    )

    # battle_features
    op.create_table(
        'battle_features',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lap_number', sa.Integer(), nullable=False),
        sa.Column('driver_ahead_id', sa.String(length=50), nullable=False),
        sa.Column('driver_behind_id', sa.String(length=50), nullable=False),
        sa.Column('gap_seconds', sa.Float(), nullable=False),
        sa.Column('closing_rate', sa.Float(), nullable=True),
        sa.Column('overtake_occurred', sa.Integer(), nullable=False),
        sa.Column('overtake_within_laps', sa.Integer(), nullable=True),
        sa.Column('drs_available', sa.Integer(), nullable=True),
        sa.Column('tyre_advantage', sa.Float(), nullable=True),
        sa.Column('extra_features', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], name=op.f('fk_battle_features_session_id_sessions')),
        sa.ForeignKeyConstraint(['driver_ahead_id'], ['drivers.driver_id'], name=op.f('fk_battle_features_driver_ahead_id_drivers')),
        sa.ForeignKeyConstraint(['driver_behind_id'], ['drivers.driver_id'], name=op.f('fk_battle_features_driver_behind_id_drivers')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_battle_features'))
    )
    op.create_index(op.f('ix_battle_features_session_id'), 'battle_features', ['session_id'], unique=False)

    # ========================================================================
    # ML Model Tables
    # ========================================================================

    # model_registry
    op.create_table(
        'model_registry',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('model_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('artifact_path', sa.String(length=500), nullable=True),
        sa.Column('training_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_model_registry'))
    )
    op.create_index(op.f('ix_model_registry_model_name'), 'model_registry', ['model_name'], unique=False)
    op.create_index(op.f('ix_model_registry_status'), 'model_registry', ['status'], unique=False)

    # predictions
    op.create_table(
        'predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('prediction_type', sa.String(length=50), nullable=False),
        sa.Column('input_features', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('prediction_value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('confidence', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['model_id'], ['model_registry.id'], name=op.f('fk_predictions_model_id_model_registry')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], name=op.f('fk_predictions_session_id_sessions')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_predictions'))
    )
    op.create_index(op.f('ix_predictions_model_id'), 'predictions', ['model_id'], unique=False)
    op.create_index(op.f('ix_predictions_prediction_type'), 'predictions', ['prediction_type'], unique=False)

    # ========================================================================
    # LLM/RAG Tables
    # ========================================================================

    # documents
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('doc_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('source_url', sa.String(length=1000), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_documents'))
    )
    op.create_index(op.f('ix_documents_doc_type'), 'documents', ['doc_type'], unique=False)

    # embeddings (uses pgvector)
    op.create_table(
        'embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=False),  # pgvector Vector type
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name=op.f('fk_embeddings_document_id_documents')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_embeddings'))
    )
    op.create_index(op.f('ix_embeddings_document_id'), 'embeddings', ['document_id'], unique=False)
    # Create pgvector index for similarity search
    op.execute('CREATE INDEX ix_embeddings_embedding ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')

    # chat_sessions
    op.create_table(
        'chat_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_name', sa.String(length=200), nullable=True),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_chat_sessions'))
    )

    # chat_messages
    op.create_table(
        'chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('retrieved_chunks', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('model_used', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], name=op.f('fk_chat_messages_session_id_chat_sessions')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_chat_messages'))
    )
    op.create_index(op.f('ix_chat_messages_session_id'), 'chat_messages', ['session_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('embeddings')
    op.drop_table('documents')
    op.drop_table('predictions')
    op.drop_table('model_registry')
    op.drop_table('battle_features')
    op.drop_table('stint_features')
    op.drop_table('lap_features')
    op.drop_table('incidents')
    op.drop_table('race_control')
    op.drop_table('laps')
    op.drop_table('stints')
    op.drop_table('sessions')
    op.drop_table('events')
    op.drop_table('constructors')
    op.drop_table('drivers')
    op.drop_table('seasons')

    # Drop extension
    op.execute('DROP EXTENSION IF EXISTS vector')
