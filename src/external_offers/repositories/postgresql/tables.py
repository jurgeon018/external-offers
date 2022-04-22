import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM, JSONB

from external_offers.enums.teams import TeamType
from external_offers.helpers.tables import get_names


metadata = sa.MetaData()

parsed_offers = sa.Table(
    'parsed_offers',
    metadata,
    sa.Column('id', sa.VARCHAR, unique=True, primary_key=True),
    sa.Column('user_segment', sa.VARCHAR),
    sa.Column('user_subsegment', sa.VARCHAR),
    sa.Column('source_object_id', sa.VARCHAR, unique=True, nullable=False),
    sa.Column('source_user_id', sa.VARCHAR),
    sa.Column('source_object_model', JSONB(none_as_null=True), nullable=False),
    sa.Column('source_group_id', sa.VARCHAR, nullable=True),
    sa.Column('is_calltracking', sa.BOOLEAN, nullable=False),
    sa.Column('synced',     sa.BOOLEAN,   nullable=False),
    sa.Column('is_test',    sa.BOOLEAN,   nullable=False, default=False),
    sa.Column('timestamp',  sa.TIMESTAMP, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP, nullable=False),
    sa.Column('external_offer_type', sa.VARCHAR, nullable=True),
)

clients = sa.Table(
    'clients',
    metadata,
    sa.Column('client_id', sa.VARCHAR, unique=True, primary_key=True),
    sa.Column('avito_user_id', sa.VARCHAR, nullable=False),
    sa.Column('cian_user_id', sa.BIGINT),
    sa.Column('client_name', sa.VARCHAR, nullable=True),
    sa.Column('client_phones', sa.ARRAY(sa.VARCHAR), nullable=False),
    sa.Column('real_phone', sa.VARCHAR, nullable=True),
    sa.Column('real_name', sa.VARCHAR, nullable=True),
    sa.Column('real_phone_hunted_at', sa.TIMESTAMP, nullable=True),
    sa.Column('client_email', sa.VARCHAR),
    sa.Column('status', sa.VARCHAR, nullable=False),
    sa.Column('operator_user_id', sa.BIGINT),
    sa.Column('segment', sa.VARCHAR, nullable=True),
    sa.Column('subsegment', sa.VARCHAR, nullable=True),
    sa.Column('next_call', sa.TIMESTAMP),
    sa.Column('calls_count', sa.SMALLINT),
    sa.Column('last_call_id', sa.VARCHAR),
    sa.Column('synced_with_grafana', sa.BOOLEAN, nullable=False, default=False),
    sa.Column('is_test', sa.BOOLEAN, nullable=False, default=False),
    sa.Column('main_account_chosen', sa.BOOLEAN, nullable=False),
    sa.Column('comment', sa.VARCHAR, nullable=True),
    sa.Column('team_id', sa.INT, nullable=True),
    sa.Column('reason_of_decline', sa.VARCHAR, nullable=True),
    sa.Column('additional_numbers', sa.VARCHAR, nullable=True),
    sa.Column('additional_emails', sa.VARCHAR, nullable=True),
    sa.Column('unactivated', sa.BOOLEAN, nullable=False, default=False),
    sa.Column('drafted_at', sa.TIMESTAMP),
    sa.Column('published_at', sa.TIMESTAMP),
)

offers_for_call = sa.Table(
    'offers_for_call',
    metadata,
    sa.Column('id', sa.VARCHAR, unique=True, primary_key=True),
    sa.Column('group_id', sa.VARCHAR, nullable=True),
    sa.Column('parsed_id', sa.VARCHAR, nullable=False),
    sa.Column('source_object_id', sa.VARCHAR, nullable=True),
    sa.Column('offer_cian_id', sa.BIGINT),
    sa.Column('publication_status', sa.VARCHAR, nullable=True),
    sa.Column('row_version', sa.BIGINT, nullable=False, default=0),
    sa.Column('is_calltracking', sa.BOOLEAN, nullable=True),
    sa.Column('client_id', sa.VARCHAR, nullable=False),
    sa.Column('status', sa.VARCHAR, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP, nullable=False),
    sa.Column('synced_at', sa.TIMESTAMP, nullable=False),
    sa.Column('started_at', sa.TIMESTAMP),
    sa.Column('promocode', sa.VARCHAR),
    sa.Column('comment', sa.VARCHAR, nullable=True),
    sa.Column('priority', sa.BIGINT),
    sa.Column('team_priorities', JSONB(none_as_null=True), nullable=True),
    sa.Column('category', sa.VARCHAR, nullable=True),
    sa.Column('last_call_id', sa.VARCHAR),
    sa.Column('synced_with_kafka', sa.BOOLEAN, nullable=False, default=False),
    sa.Column('synced_with_grafana', sa.BOOLEAN, nullable=False, default=False),
    sa.Column('is_test', sa.BOOLEAN, nullable=False, default=False),
    sa.Column('parsed_created_at', sa.TIMESTAMP, nullable=False),
    sa.Column('external_offer_type', sa.VARCHAR, nullable=True),
    sa.Column('drafted_at', sa.TIMESTAMP),
    sa.Column('published_at', sa.TIMESTAMP),
)

event_log = sa.Table(
    'event_log',
    metadata,
    sa.Column('id', sa.BIGINT, autoincrement=True, primary_key=True),
    sa.Column('offer_id', sa.VARCHAR),
    sa.Column('operator_user_id', sa.BIGINT),
    sa.Column('status', sa.VARCHAR, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP, nullable=False),
    sa.Column('call_id', sa.VARCHAR,)
)

team_type_enum = ENUM(
    *get_names(TeamType),
    name='team_type'
)

teams = sa.Table(
    'teams',
    metadata,
    sa.Column('team_id', sa.INT, unique=True, nullable=False, autoincrement=True, primary_key=True),
    sa.Column('team_name', sa.VARCHAR, unique=True, nullable=True),
    sa.Column('team_type', team_type_enum, nullable=False),
    sa.Column('lead_id', sa.VARCHAR, nullable=False),
    sa.Column('settings', JSONB(), nullable=True),
    sa.Column('team_waiting_offers_count', sa.INT, nullable=True),
    sa.Column('team_waiting_offers_count_updated_at', sa.TIMESTAMP, nullable=True),
)

operators = sa.Table(
    'operators',
    metadata,
    sa.Column('operator_id', sa.VARCHAR, unique=True, nullable=False, primary_key=True),
    sa.Column('is_teamlead', sa.BOOLEAN, nullable=False),
    sa.Column('full_name', sa.VARCHAR, nullable=True),
    sa.Column('team_id', sa.INT, nullable=True),
    sa.Column('email', sa.VARCHAR, nullable=True),
    sa.Column('created_at', sa.TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP, nullable=False),
)

client_account_statuses = sa.Table(
    'client_account_statuses',
    metadata,
    sa.Column('phone', sa.VARCHAR, nullable=False, unique=True, primary_key=True),
    sa.Column('smb_account_status', sa.VARCHAR, nullable=True),
    sa.Column('homeowner_account_status', sa.VARCHAR, nullable=True),
    sa.Column('new_cian_user_id', sa.BIGINT, nullable=True),
    sa.Column('created_at', sa.TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP, nullable=False),
)

clients_priorities = sa.Table(
    'clients_priorities',
    metadata,
    sa.Column('priorities', JSONB(), nullable=True),
    sa.Column('team_id', sa.INT, nullable=True),
    sa.Column('created_at', sa.TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP, nullable=False),
)
