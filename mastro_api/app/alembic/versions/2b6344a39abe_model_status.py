"""model status

Revision ID: 2b6344a39abe
Revises: 1e5833c8030d
Create Date: 2024-05-10 09:08:48.314600

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2b6344a39abe'
down_revision = '1e5833c8030d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('alerts', sa.Column('channel_id', sqlmodel.sql.sqltypes.GUID(), nullable=False))
    op.add_column('alerts', sa.Column('message', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.add_column('alerts', sa.Column('alert_id', sqlmodel.sql.sqltypes.GUID(), nullable=False))
    op.drop_column('alerts', 'alert')
    op.drop_column('alerts', 'time')
    op.alter_column('channels', 'device_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.alter_column('channels', 'channel',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('channels', 'unit',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('channels', 'constant',
               existing_type=sa.NUMERIC(),
               type_=sa.Float(),
               existing_nullable=True)
    op.alter_column('channels', 'writable',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('false'))
    op.alter_column('devices', 'timer_loop',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('devices', 'last_access',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               type_=sa.DateTime(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('devices', 'last_access',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('devices', 'timer_loop',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('channels', 'writable',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('false'))
    op.alter_column('channels', 'constant',
               existing_type=sa.Float(),
               type_=sa.NUMERIC(),
               existing_nullable=True)
    op.alter_column('channels', 'unit',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('channels', 'channel',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('channels', 'device_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.add_column('alerts', sa.Column('time', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.add_column('alerts', sa.Column('alert', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('alerts', 'alert_id')
    op.drop_column('alerts', 'message')
    op.drop_column('alerts', 'channel_id')
    # ### end Alembic commands ###
