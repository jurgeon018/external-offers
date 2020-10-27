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
