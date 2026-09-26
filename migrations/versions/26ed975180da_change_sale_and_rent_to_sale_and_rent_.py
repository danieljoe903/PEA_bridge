"""Change sale and rent to SALE and RENT in propertysubmission listing_type enum

Revision ID: 26ed975180da
Revises: 8f938d9293a5
Create Date: 2026-09-24 00:00:03.628528
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "26ed975180da"
down_revision = "8f938d9293a5"
branch_labels = None
depends_on = None


def upgrade():

    # Step 1:
    # Temporarily allow both old and new enum values.
    op.execute(
        """
        ALTER TABLE property_submissions
        MODIFY COLUMN listing_type
        ENUM('sale', 'rent', 'SALE', 'RENT')
        NOT NULL
        """
    )

    # Step 2:
    # Convert existing lowercase data to uppercase.
    op.execute(
        """
        UPDATE property_submissions
        SET listing_type = 'SALE'
        WHERE listing_type = 'sale'
        """
    )

    op.execute(
        """
        UPDATE property_submissions
        SET listing_type = 'RENT'
        WHERE listing_type = 'rent'
        """
    )

    # Step 3:
    # Remove the old lowercase enum values.
    op.execute(
        """
        ALTER TABLE property_submissions
        MODIFY COLUMN listing_type
        ENUM('SALE', 'RENT')
        NOT NULL
        """
    )


def downgrade():

    # Step 1:
    # Temporarily allow both versions.
    op.execute(
        """
        ALTER TABLE property_submissions
        MODIFY COLUMN listing_type
        ENUM('sale', 'rent', 'SALE', 'RENT')
        NOT NULL
        """
    )

    # Step 2:
    # Convert uppercase values back to lowercase.
    op.execute(
        """
        UPDATE property_submissions
        SET listing_type = 'sale'
        WHERE listing_type = 'SALE'
        """
    )

    op.execute(
        """
        UPDATE property_submissions
        SET listing_type = 'rent'
        WHERE listing_type = 'RENT'
        """
    )

    # Step 3:
    # Restore the original enum.
    op.execute(
        """
        ALTER TABLE property_submissions
        MODIFY COLUMN listing_type
        ENUM('sale', 'rent')
        NOT NULL
        """
    )