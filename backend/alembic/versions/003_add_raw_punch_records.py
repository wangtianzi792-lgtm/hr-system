"""add raw_punch_records table

Revision ID: 003
Revises: 002
Create Date: 2026-04-24

"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'raw_punch_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=True),
        sa.Column('device_id', sa.Integer(), nullable=True),
        sa.Column('punch_time', sa.DateTime(), nullable=False),
        sa.Column('verify_type', sa.Integer(), default=0),
        sa.Column('punch_method', sa.Integer(), default=0),
        sa.Column('attendance_record_id', sa.Integer(), nullable=True),
        sa.Column('is_processed', sa.Boolean(), default=False),
        sa.Column('is_anomaly', sa.Boolean(), default=False),
        sa.Column('anomaly_reason', sa.String(length=100), nullable=True),
        sa.Column('raw_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_raw_punch_employee_id', 'raw_punch_records', ['employee_id'])
    op.create_index('ix_raw_punch_device_id', 'raw_punch_records', ['device_id'])
    op.create_index('ix_raw_punch_punch_time', 'raw_punch_records', ['punch_time'])
    op.create_index('ix_raw_punch_is_anomaly', 'raw_punch_records', ['is_anomaly'])
    op.create_foreign_key('fk_raw_punch_employee', 'raw_punch_records', 'employees', ['employee_id'], ['id'])
    op.create_foreign_key('fk_raw_punch_device', 'raw_punch_records', 'devices', ['device_id'], ['id'])
    op.create_foreign_key('fk_raw_punch_attendance', 'raw_punch_records', 'attendance_records', ['attendance_record_id'], ['id'])


def downgrade() -> None:
    op.drop_table('raw_punch_records')
