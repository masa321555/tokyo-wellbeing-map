"""Add leisure facilities to culture_data table

Revision ID: add_leisure_facilities
Revises: 
Create Date: 2025-08-12

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_leisure_facilities'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to culture_data table
    op.add_column('culture_data', sa.Column('movie_theaters', sa.Integer(), nullable=True))
    op.add_column('culture_data', sa.Column('theme_parks', sa.Integer(), nullable=True))
    op.add_column('culture_data', sa.Column('shopping_malls', sa.Integer(), nullable=True))
    op.add_column('culture_data', sa.Column('game_centers', sa.Integer(), nullable=True))


def downgrade():
    # Remove columns from culture_data table
    op.drop_column('culture_data', 'game_centers')
    op.drop_column('culture_data', 'shopping_malls')
    op.drop_column('culture_data', 'theme_parks')
    op.drop_column('culture_data', 'movie_theaters')