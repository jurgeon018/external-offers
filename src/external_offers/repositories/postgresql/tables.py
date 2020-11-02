import sqlalchemy as sa


metadata = sa.MetaData()

parsed_offers_table = sa.Table(
    'parsed_offers',
    metadata,
    sa.Column('id', sa.VARCHAR, unique=True, primary_key=True),
    sa.Column('user_segment', sa.VARCHAR),
    sa.Column('source_object_id', sa.VARCHAR, nullable=False),
    sa.Column('source_user_id', sa.VARCHAR),
    sa.Column('source_object_model', sa.JSON, nullable=False),
    sa.Column('is_calltracking', sa.BOOLEAN, nullable=False),
    sa.Column('timestamp', sa.TIMESTAMP, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP, nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP, nullable=False),
)


clients = sa.Table(
    'clients',
    metadata,
    sa.Column('client_id', sa.INT, unique=True, primary_key=True),
    sa.Column('avito_user_id', sa.BIGINT, nullable=False),
    sa.Column('realty_user_id', sa.BIGINT),
    sa.Column('client_name', sa.VARCHAR, nullable=False),
    sa.Column('client_phone', sa.VARCHAR, nullable=False),
    sa.Column('client_email', sa.VARCHAR),
    sa.Column('status', sa.VARCHAR, nullable=False),
    sa.Column('operator_user_id', sa.BIGINT),
)


offers_for_call = sa.Table(
    'offers_for_call',
    metadata,
    sa.Column('id', sa.INT, unique=True, primary_key=True),
    sa.Column('parsed_id', sa.BIGINT, nullable=False),
    sa.Column('offer_cian_id', sa.BIGINT),
    sa.Column('client_id', sa.INT, nullable=False),
    sa.Column('status', sa.VARCHAR, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP, nullable=False),
    sa.Column('started_at', sa.TIMESTAMP),
)
