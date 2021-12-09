"""update model.

Revision ID: b049c50f01a6
Revises: 752b10fba4f9
Create Date: 2021-04-15 09:34:16.783824

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy.orm.session import Session
from sample_db.models import Datasets, CollectMethod, DatasetView
from sample_db.models.dataset_table import DatasetType

# revision identifiers, used by Alembic.
revision = 'b049c50f01a6'
down_revision = '752b10fba4f9'
branch_labels = ()
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    session = Session(bind=op.get_bind())

    session.execute(f"DROP VIEW IF EXISTS {DatasetView.__table__}")
    dataset_type = DatasetType()
    dataset_type.create()

    session.commit()

    op.alter_column('collect_method', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='sampledb')

    op.create_unique_constraint(op.f('collect_method_name_key'), 'collect_method', ['name'], schema='sampledb')
    op.create_index(op.f('idx_sampledb_collect_method_name'), 'collect_method', ['name'], unique=False, schema='sampledb')
    op.alter_column('datasets', 'observation_table_name', new_column_name='dataset_table_name', schema='sampledb')
    op.add_column('datasets', sa.Column('is_public', sa.Boolean(), nullable=False,  server_default='t'), schema='sampledb')
    op.add_column('datasets', sa.Column('title', sa.String(length=255), nullable=False,  server_default='Titulo'), schema='sampledb')
    op.add_column('datasets', sa.Column('version_predecessor', sa.Integer(), nullable=True), schema='sampledb')
    op.add_column('datasets', sa.Column('version_successor', sa.Integer(), nullable=True), schema='sampledb')
    op.alter_column('datasets', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='sampledb')
    op.alter_column('datasets', 'version',
               existing_type=sa.VARCHAR(),
               nullable=False,
               schema='sampledb')
    op.create_unique_constraint(op.f('datasets_name_key'), 'datasets', ['name', 'version'], schema='sampledb')
    op.create_index('idx_datasets_start_date_end_date', 'datasets', ['start_date', 'end_date'], unique=False, schema='sampledb')
    op.create_index(op.f('idx_sampledb_datasets_classification_system_id'), 'datasets', ['classification_system_id'], unique=False, schema='sampledb')
    op.create_index(op.f('idx_sampledb_datasets_collect_method_id'), 'datasets', ['collect_method_id'], unique=False, schema='sampledb')
    op.create_index(op.f('idx_sampledb_datasets_name'), 'datasets', ['name'], unique=False, schema='sampledb')
    op.create_index(op.f('idx_sampledb_datasets_start_date'), 'datasets', [sa.text('start_date DESC')], unique=False, schema='sampledb')
    op.create_index(op.f('idx_sampledb_datasets_user_id'), 'datasets', ['user_id'], unique=False, schema='sampledb')
    op.drop_constraint('datasets_collect_method_id_collect_method_fkey', 'datasets', schema='sampledb', type_='foreignkey')
    op.drop_constraint('datasets_classification_system_id_class_systems_fkey', 'datasets', schema='sampledb', type_='foreignkey')
    op.drop_constraint('datasets_user_id_users_fkey', 'datasets', schema='sampledb', type_='foreignkey')
    op.create_foreign_key(op.f('datasets_version_predecessor_datasets_fkey'), 'datasets', 'datasets', ['version_predecessor'], ['id'], source_schema='sampledb', referent_schema='sampledb', onupdate='CASCADE', ondelete='CASCADE')
    op.create_foreign_key(op.f('datasets_version_successor_datasets_fkey'), 'datasets', 'datasets', ['version_successor'], ['id'], source_schema='sampledb', referent_schema='sampledb', onupdate='CASCADE', ondelete='CASCADE')
    op.create_foreign_key(op.f('datasets_collect_method_id_collect_method_fkey'), 'datasets', 'collect_method', ['collect_method_id'], ['id'], source_schema='sampledb', referent_schema='sampledb', onupdate='CASCADE', ondelete='CASCADE')
    op.create_foreign_key(op.f('datasets_classification_system_id_class_systems_fkey'), 'datasets', 'class_systems', ['classification_system_id'], ['id'], source_schema='sampledb', referent_schema='lccs', onupdate='CASCADE', ondelete='CASCADE')
    op.create_foreign_key(op.f('datasets_user_id_users_fkey'), 'datasets', 'users', ['user_id'], ['id'], source_schema='sampledb', referent_schema='sampledb', ondelete='CASCADE')
    op.drop_column('datasets', 'midias_table_name', schema='sampledb')
    op.create_index(op.f('idx_sampledb_provenance_dataset_id'), 'provenance', ['dataset_id'], unique=False, schema='sampledb')
    op.create_index(op.f('idx_sampledb_provenance_dataset_parent_id'), 'provenance', ['dataset_parent_id'], unique=False, schema='sampledb')
    op.drop_constraint('provenance_dataset_id_datasets_fkey', 'provenance', schema='sampledb', type_='foreignkey')
    op.drop_constraint('provenance_dataset_parent_id_datasets_fkey', 'provenance', schema='sampledb', type_='foreignkey')
    op.create_foreign_key(op.f('provenance_dataset_id_datasets_fkey'), 'provenance', 'datasets', ['dataset_id'], ['id'], source_schema='sampledb', referent_schema='sampledb', onupdate='CASCADE', ondelete='CASCADE')
    op.create_foreign_key(op.f('provenance_dataset_parent_id_datasets_fkey'), 'provenance', 'datasets', ['dataset_parent_id'], ['id'], source_schema='sampledb', referent_schema='sampledb', onupdate='CASCADE', ondelete='CASCADE')
    op.create_index(op.f('idx_sampledb_users_email'), 'users', ['email'], unique=False, schema='sampledb')
    op.create_index(op.f('idx_sampledb_users_full_name'), 'users', ['full_name'], unique=False, schema='sampledb')
    op.create_unique_constraint(op.f('users_email_key'), 'users', ['email'], schema='sampledb')

    session.execute("CREATE VIEW {} AS " \
                    "SELECT datasets.created_at, datasets.updated_at, datasets.id, datasets.name, " \
                    "datasets.title, datasets.start_date, datasets.end_date, datasets.dataset_table_name, " \
                    "datasets.version, datasets.version_successor, datasets.version_predecessor, " \
                    "datasets.description, class_systems.name AS classification_system_name, " \
                    "class_systems.id AS classification_system_id, class_systems.version AS classification_system_version, " \
                    "users.id AS user_id, users.full_name AS user_name, collect_method.name AS collect_method_name, " \
                    "collect_method.id AS collect_method_id, " \
                    "datasets.metadata_json, datasets.is_public "
                    "FROM {} AS datasets, {} AS class_systems, {} AS users, {} AS collect_method " \
                    "WHERE users.id = datasets.user_id " \
                    "AND class_systems.id = datasets.classification_system_id " \
                    "AND collect_method.id = datasets.collect_method_id;"
                    .format(DatasetView.__table__,
                            Datasets.__table__,
                            'lccs.class_systems',
                            'sampledb.users',
                            CollectMethod.__table__)
                    )

    session.commit()

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('users_email_key'), 'users', schema='sampledb', type_='unique')
    op.drop_index(op.f('idx_sampledb_users_full_name'), table_name='users', schema='sampledb')
    op.drop_index(op.f('idx_sampledb_users_email'), table_name='users', schema='sampledb')
    op.drop_constraint(op.f('provenance_dataset_parent_id_datasets_fkey'), 'provenance', schema='sampledb', type_='foreignkey')
    op.drop_constraint(op.f('provenance_dataset_id_datasets_fkey'), 'provenance', schema='sampledb', type_='foreignkey')
    op.create_foreign_key('provenance_dataset_parent_id_datasets_fkey', 'provenance', 'datasets', ['dataset_parent_id'], ['id'], source_schema='sampledb', referent_schema='sampledb')
    op.create_foreign_key('provenance_dataset_id_datasets_fkey', 'provenance', 'datasets', ['dataset_id'], ['id'], source_schema='sampledb', referent_schema='sampledb')
    op.drop_index(op.f('idx_sampledb_provenance_dataset_parent_id'), table_name='provenance', schema='sampledb')
    op.drop_index(op.f('idx_sampledb_provenance_dataset_id'), table_name='provenance', schema='sampledb')
    op.add_column('datasets', sa.Column('midias_table_name', sa.VARCHAR(), autoincrement=False, nullable=True), schema='sampledb')
    op.drop_constraint(op.f('datasets_user_id_users_fkey'), 'datasets', schema='sampledb', type_='foreignkey')
    op.drop_constraint(op.f('datasets_classification_system_id_class_systems_fkey'), 'datasets', schema='sampledb', type_='foreignkey')
    op.drop_constraint(op.f('datasets_collect_method_id_collect_method_fkey'), 'datasets', schema='sampledb', type_='foreignkey')
    op.drop_constraint(op.f('datasets_version_successor_datasets_fkey'), 'datasets', schema='sampledb', type_='foreignkey')
    op.drop_constraint(op.f('datasets_version_predecessor_datasets_fkey'), 'datasets', schema='sampledb', type_='foreignkey')
    op.create_foreign_key('datasets_user_id_users_fkey', 'datasets', 'users', ['user_id'], ['id'], source_schema='sampledb', referent_schema='sampledb')
    op.create_foreign_key('datasets_classification_system_id_class_systems_fkey', 'datasets', 'class_systems', ['classification_system_id'], ['id'], source_schema='sampledb', referent_schema='lccs')
    op.create_foreign_key('datasets_collect_method_id_collect_method_fkey', 'datasets', 'collect_method', ['collect_method_id'], ['id'], source_schema='sampledb', referent_schema='sampledb')
    op.drop_index(op.f('idx_sampledb_datasets_user_id'), table_name='datasets', schema='sampledb')
    op.drop_index(op.f('idx_sampledb_datasets_start_date'), table_name='datasets', schema='sampledb')
    op.drop_index(op.f('idx_sampledb_datasets_name'), table_name='datasets', schema='sampledb')
    op.drop_index(op.f('idx_sampledb_datasets_collect_method_id'), table_name='datasets', schema='sampledb')
    op.drop_index(op.f('idx_sampledb_datasets_classification_system_id'), table_name='datasets', schema='sampledb')
    op.drop_index('idx_datasets_start_date_end_date', table_name='datasets', schema='sampledb')
    op.drop_constraint(op.f('datasets_name_key'), 'datasets', schema='sampledb', type_='unique')
    op.alter_column('datasets', 'version',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='sampledb')
    op.alter_column('datasets', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='sampledb')
    op.drop_column('datasets', 'version_successor', schema='sampledb')
    op.drop_column('datasets', 'version_predecessor', schema='sampledb')
    op.drop_column('datasets', 'title', schema='sampledb')
    op.drop_column('datasets', 'is_public', schema='sampledb')
    op.alter_column('datasets', 'dataset_table_name', new_column_name='observation_table_name', schema='sampledb')
    op.drop_index(op.f('idx_sampledb_collect_method_name'), table_name='collect_method', schema='sampledb')
    op.drop_constraint(op.f('collect_method_name_key'), 'collect_method', schema='sampledb', type_='unique')
    op.alter_column('collect_method', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True,
               schema='sampledb')

    session = Session(bind=op.get_bind())

    dataset_type = DatasetType()
    dataset_type.drop()
    session.commit()

    session.execute("CREATE OR REPLACE VIEW {} AS " \
                    "SELECT datasets.created_at, datasets.updated_at, datasets.id, datasets.name, " \
                    "datasets.start_date, datasets.end_date, datasets.observation_table_name, " \
                    "datasets.midias_table_name, datasets.metadata_json, datasets.version, " \
                    "datasets.description, class_systems.name AS classification_system_name, " \
                    "users.full_name AS user_name, collect_method.name AS collect_method " \
                    "FROM {} AS datasets, {} AS class_systems, {} AS users, {} AS collect_method " \
                    "WHERE users.id = datasets.user_id " \
                    "AND class_systems.id = datasets.classification_system_id " \
                    "AND collect_method.id = datasets.collect_method_id;"
                    .format(DatasetView.__table__,
                            Datasets.__table__,
                            'lccs.class_systems',
                            'sampledb.users',
                            CollectMethod.__table__)
                    )
    session.commit()

    # ### end Alembic commands ###
