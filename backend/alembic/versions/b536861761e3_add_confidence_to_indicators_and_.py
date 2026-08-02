"""Add confidence to indicators and implementation_success to negotiation_events

Revision ID: b536861761e3
Revises: ff99ad846894
Create Date: 2026-08-02 20:33:07.903027

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b536861761e3'
down_revision: Union[str, Sequence[str], None] = 'ff99ad846894'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Autogenerate ΔΕΝ δημιουργεί αυτόματα CREATE TYPE όταν προσθέτεις μια νέα
# Enum στήλη σε ΥΠΑΡΧΟΝ πίνακα (μόνο όταν η Enum γεννιέται μαζί με νέο πίνακα
# μέσω CREATE TABLE) -- γι' αυτό το φτιάχνουμε ρητά εδώ πριν το add_column.
indicator_confidence_enum = postgresql.ENUM(
    'EXACT', 'CHART_READ', 'RANGE', name='indicatorconfidence'
)


def upgrade() -> None:
    """Upgrade schema."""
    indicator_confidence_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('indicators', sa.Column('confidence', indicator_confidence_enum, nullable=True))
    op.add_column('negotiation_events', sa.Column('implementation_success', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('negotiation_events', 'implementation_success')
    op.drop_column('indicators', 'confidence')
    indicator_confidence_enum.drop(op.get_bind(), checkfirst=True)
