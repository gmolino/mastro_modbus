"""database status

Revision ID: 1e5833c8030d
Revises: 
Create Date: 2024-05-10 07:17:59.970126

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1e5833c8030d'
down_revision = '54d3750146d7'
branch_labels = None
depends_on = None


def upgrade():

    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.create_table('devices',
    sa.Column('device_id', sa.UUID(), server_default=sa.text("uuid_generate_v4()::uuid"), autoincrement=False, nullable=False),
    sa.Column('reference', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('timer_loop', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('measurement', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('file', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('gateway', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('available', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('last_access', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('device_id', name='devices_pk'),
    sa.UniqueConstraint('reference', name='devices_reference_key')
    )
    op.create_table('channels',
    sa.Column('channel_id', sa.UUID(), server_default=sa.text("uuid_generate_v4()::uuid"), autoincrement=False, nullable=False),
    sa.Column('device_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('channel', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('unit', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('item', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('constant', sa.NUMERIC(), autoincrement=False, nullable=True),
    sa.Column('writable', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['device_id'], ['devices.device_id'], name='channels_fk'),
    sa.PrimaryKeyConstraint('channel_id', name='channels_pk'),
    postgresql_ignore_search_path=False
    )
    op.create_table('alerts',
    sa.Column('device_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('alert', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('time', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    )

def downgrade():
    op.drop_table('alerts')
    op.drop_table('devices')
    op.drop_table('channels')
