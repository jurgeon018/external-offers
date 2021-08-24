import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


metadata = sa.MetaData()

parsed_offers = sa.Table(
    'parsed_offers',
    metadata,
    sa.Column('id', sa.VARCHAR, unique=True, primary_key=True),
    sa.Column('user_segment', sa.VARCHAR),
    sa.Column('source_object_id', sa.VARCHAR, unique=True, nullable=False),
    sa.Column('source_user_id', sa.VARCHAR),
    sa.Column('source_object_model', JSONB(none_as_null=True), nullable=False),
    sa.Column('is_calltracking', sa.BOOLEAN, nullable=False),
    sa.Column('synced',     sa.BOOLEAN,   nullable=False),
    sa.Column('is_test',    sa.BOOLEAN,   nullable=False, default=False),
    sa.Column('timestamp',  sa.TIMESTAMP, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP, nullable=False),
)

clients = sa.Table(
    'clients',
    metadata,
    sa.Column('client_id', sa.VARCHAR, unique=True, primary_key=True),
    sa.Column('avito_user_id', sa.VARCHAR, nullable=False),
    sa.Column('cian_user_id', sa.BIGINT),
    sa.Column('client_name', sa.VARCHAR, nullable=True),
    sa.Column('client_phones', sa.ARRAY(sa.VARCHAR), nullable=False),
    sa.Column('client_email', sa.VARCHAR),
    sa.Column('status', sa.VARCHAR, nullable=False),
    sa.Column('operator_user_id', sa.BIGINT),
    sa.Column('segment', sa.VARCHAR, nullable=True),
    sa.Column('next_call', sa.TIMESTAMP),
    sa.Column('calls_count', sa.SMALLINT),
    sa.Column('last_call_id', sa.VARCHAR),
    sa.Column('synced_with_grafana', sa.BOOLEAN, nullable=False, default=False),
    sa.Column('is_test', sa.BOOLEAN, nullable=False, default=False),
    sa.Column('main_account_chosen', sa.BOOLEAN, nullable=False),
    sa.Column('comment', sa.VARCHAR, nullable=True),
)

offers_for_call = sa.Table(
    'offers_for_call',
    metadata,
    sa.Column('id', sa.VARCHAR, unique=True, primary_key=True),
    sa.Column('parsed_id', sa.VARCHAR, nullable=False),
    sa.Column('offer_cian_id', sa.BIGINT),
    sa.Column('publication_status', sa.VARCHAR, nullable=True),
    sa.Column('row_version', sa.BIGINT, nullable=False, default=0),
    sa.Column('client_id', sa.VARCHAR, nullable=False),
    sa.Column('status', sa.VARCHAR, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP, nullable=False),
    sa.Column('synced_at', sa.TIMESTAMP, nullable=False),
    sa.Column('started_at', sa.TIMESTAMP),
    sa.Column('promocode', sa.VARCHAR),
    sa.Column('priority', sa.INT),
    sa.Column('category', sa.VARCHAR, nullable=True),
    sa.Column('last_call_id', sa.VARCHAR),
    sa.Column('synced_with_kafka', sa.BOOLEAN, nullable=False, default=False),
    sa.Column('synced_with_grafana', sa.BOOLEAN, nullable=False, default=False),
    sa.Column('is_test', sa.BOOLEAN, nullable=False, default=False),
    sa.Column('parsed_created_at', sa.TIMESTAMP, nullable=False),
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
