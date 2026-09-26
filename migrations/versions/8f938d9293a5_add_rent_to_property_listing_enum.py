"""Add RENT to property listing enum

Revision ID: 8f938d9293a5
Revises: be641c6ff835
Create Date: 2026-09-23 17:46:12.383103

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f938d9293a5'
down_revision = 'be641c6ff835'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE properties
        MODIFY COLUMN property_listing
        ENUM('SALE', 'RENT')
        NOT NULL
        """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE properties
        MODIFY COLUMN property_listing
        ENUM('SALE')
        NOT NULL
        """
    )
