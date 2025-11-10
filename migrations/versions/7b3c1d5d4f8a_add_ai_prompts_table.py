"""add ai_prompts table

Revision ID: 7b3c1d5d4f8a
Revises: d80a7266c2db
Create Date: 2025-11-11 02:06:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b3c1d5d4f8a'
down_revision = 'd80a7266c2db'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'ai_prompts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('key', sa.String(length=100), nullable=False, unique=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('system_message', sa.Text(), nullable=True),
        sa.Column('prompt_template', sa.Text(), nullable=False),
        sa.Column('model', sa.String(length=50), nullable=False, server_default=sa.text("'gpt-3.5-turbo'")),
        sa.Column('temperature', sa.Float(), nullable=False, server_default=sa.text('0.5')),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('ai_prompts')


