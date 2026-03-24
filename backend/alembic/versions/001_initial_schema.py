"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create regions table
    op.create_table(
        'regions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=True),
        sa.Column('level', sa.String(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('geometry', Geometry('POLYGON'), nullable=True),
        sa.Column('population', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['regions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_regions_code', 'regions', ['code'], unique=True)
    op.create_index('ix_regions_name', 'regions', ['name'], unique=False)

    # Create diseases table
    op.create_table(
        'diseases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_diseases_name', 'diseases', ['name'], unique=True)

    # Create disease_records table
    op.create_table(
        'disease_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('disease_id', sa.Integer(), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('total_cases', sa.Integer(), nullable=True),
        sa.Column('new_cases', sa.Integer(), nullable=True),
        sa.Column('total_deaths', sa.Integer(), nullable=True),
        sa.Column('new_deaths', sa.Integer(), nullable=True),
        sa.Column('incidence_rate', sa.Float(), nullable=True),
        sa.Column('mortality_rate', sa.Float(), nullable=True),
        sa.Column('data_source', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['disease_id'], ['diseases.id'], ),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_disease_records_date', 'disease_records', ['date'], unique=False)

    # Create climate_records table
    op.create_table(
        'climate_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('temp_avg', sa.Float(), nullable=True),
        sa.Column('temp_min', sa.Float(), nullable=True),
        sa.Column('temp_max', sa.Float(), nullable=True),
        sa.Column('rainfall', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('wind_speed', sa.Float(), nullable=True),
        sa.Column('pressure', sa.Float(), nullable=True),
        sa.Column('data_source', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_climate_records_date', 'climate_records', ['date'], unique=False)

    # Create economic_records table
    op.create_table(
        'economic_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('gdp_per_capita', sa.Float(), nullable=True),
        sa.Column('poverty_rate', sa.Float(), nullable=True),
        sa.Column('unemployment_rate', sa.Float(), nullable=True),
        sa.Column('urban_population_pct', sa.Float(), nullable=True),
        sa.Column('population_density', sa.Float(), nullable=True),
        sa.Column('hospital_beds_per_1000', sa.Float(), nullable=True),
        sa.Column('doctors_per_1000', sa.Float(), nullable=True),
        sa.Column('vaccination_rate', sa.Float(), nullable=True),
        sa.Column('data_source', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_economic_records_year', 'economic_records', ['year'], unique=False)

def downgrade() -> None:
    op.drop_table('economic_records')
    op.drop_table('climate_records')
    op.drop_table('disease_records')
    op.drop_table('diseases')
    op.drop_table('regions')
