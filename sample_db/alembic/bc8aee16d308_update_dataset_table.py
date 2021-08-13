"""update_dataset_table

Revision ID: bc8aee16d308
Revises: 6548bf185f76
Create Date: 2021-07-15 14:06:57.521295

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sample_db.models import DatasetView

# revision identifiers, used by Alembic.
revision = 'bc8aee16d308'
down_revision = '6548bf185f76'
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.add_column('datasets', sa.Column('dataset_table_id', postgresql.OID(), nullable=True), schema='sampledb')

    with op.get_bind().connect() as conn:
        conn.execute(f'DROP VIEW IF EXISTS {DatasetView.__table__}')

        result = conn.execute(
            """SELECT table_schema, table_name, (table_schema || '.' || table_name)::regclass::oid AS table_id
               FROM information_schema.tables
               WHERE table_name ~ '^dataset_' AND table_schema = 'sampledb'"""
        )
        for r in result:
            conn.execute(
               f"""UPDATE {r.table_schema}.datasets
                    SET dataset_table_id = '{r.table_id}'
                    WHERE dataset_table_name = '{r.table_name}'"""
            )
        conn.execute('COMMIT')

    op.alter_column('datasets', 'dataset_table_id',
                    existing_type=postgresql.OID(),
                    nullable=False,
                    schema='sampledb')

    op.drop_column('datasets', 'dataset_table_name', schema='sampledb')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('datasets', sa.Column('dataset_table_name', sa.VARCHAR(), autoincrement=False, nullable=False), schema='sampledb')
    op.drop_column('datasets', 'dataset_table_id', schema='sampledb')
    ''' TODO: create view'''
    # ### end Alembic commands ###
