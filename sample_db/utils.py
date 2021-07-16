#
# This file is part of Sample Database Model.
# Copyright (C) 2020-2021 INPE.
#
# Sample Database Model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Utils Interface for the Sample Database Model ."""
import logging

from bdc_db.db import db as _db
from lccs_db.models import LucClassificationSystem
from sqlalchemy import exc
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.schema import DropSequence

from .config import Config
from .db_util import DBAccessor
from .models import CollectMethod, Datasets


def drop_dataset_table(dataset_data_table, sequence):
    """Drop dataset_<name>."""
    try:
        _db.session.execute(dataset_data_table.delete())
        _db.session.execute(DropSequence(sequence))
        _db.session.session.commit()
    except BaseException as err:
        logging.warning('Error while delete dataset table data')


def get_classification_system(classification_system_name, classification_system_version):
    """Return the classification system."""
    try:
        class_system = _db.session.query(LucClassificationSystem)\
            .filter_by(name=classification_system_name, version=classification_system_version)\
            .one()
    except NoResultFound:
        raise RuntimeError(f'Classification System {classification_system_name} not found!')

    return class_system


def get_collect_method(collect_method_name):
    """Return the collect method."""
    try:
        collect_method = CollectMethod.get(name=collect_method_name)
    except ValueError:
        raise RuntimeError(f'Collect Method {collect_method_name} not found!')
    return collect_method


def add_dataset_data_file(dataset_name, dataset_version, user_id,
                          mimetype, dataset_file, **extra_fields):
    """Insert dataset data into database."""
    from sample_db_utils.core.driver import Driver
    from sample_db_utils.factory import factory

    extra_fields.setdefault('create', False)
    extra_fields.setdefault('mappings_json', dict(class_id="class_id", start_date="start_date", end_date="end_date"))

    affected_rows = 0
    ds = None

    driver_type = factory.get(mimetype)

    _accessor = DBAccessor()

    with _db.session.begin_nested():
        try:
            ds = _db.session.query(Datasets)\
                .filter(Datasets.name == dataset_name, Datasets.version == dataset_version)\
                .first()
        except ValueError:
            raise RuntimeError(f'Dataset {dataset_name}-V{dataset_version} not found!')

        driver: Driver = driver_type(entries=dataset_file,
                                     mappings=extra_fields['mappings_json'],
                                     storager=_accessor,
                                     user=user_id)

        driver.load_data_sets()
        dataset_table = ds.ds_table

        try:
            driver.store(dataset_table)
            logging.info('Data inserted in table {}'.format(driver.__class__.__name__))
            affected_rows = len(driver.get_data_sets())
        except exc.SQLAlchemyError as e:
            _db.session.rollback()
            raise RuntimeError(f'Error while store data: {e}')

    _db.session.commit()

    return ds, affected_rows


def create_view(dataset_name, dataset_version):
    """Create dataset_view."""
    with _db.session.begin_nested():
        try:
            ds = _db.session.query(Datasets)\
                .filter(Datasets.name == dataset_name, Datasets.version == dataset_version)\
                .first()
        except ValueError:
            raise RuntimeError(f'Dataset {dataset_name}-V{dataset_version} not found!')

        try:
            result = ds.make_view_dataset_data
            _db.engine.execute(result)
        except exc.SQLAlchemyError as e:
            _db.session.rollback()
            raise RuntimeError(f'Error while create view data: {e}')

    _db.session.commit()

    return


def create_dataset(user_id, classification_system_id, collect_method_id,
                   dataset_name, title, start_date, end_date, version, **extra_fields):
    """Insert a new dataset."""
    extra_fields.setdefault('description', "")
    extra_fields.setdefault('version_predecessor', None)
    extra_fields.setdefault('version_successor', None)
    extra_fields.setdefault('metadata_json', None)
    extra_fields.setdefault('is_public', True)

    with _db.session.begin_nested():
        ds = Datasets.create_ds_table(table_name=dataset_name, version=version)
        ds.name = dataset_name
        ds.title = title
        ds.start_date = start_date
        ds.end_date = end_date
        ds.description = extra_fields["description"]
        ds.version_predecessor = extra_fields["version_predecessor"]
        ds.version_successor = extra_fields["version_successor"]
        ds.is_public = extra_fields["is_public"]
        ds.classification_system_id = classification_system_id
        ds.collect_method_id = collect_method_id
        ds.metadata_json = extra_fields['metadata_json']
        ds.user_id = user_id

        _db.session.add(ds)

    _db.session.commit()

    return ds


def delete_dataset_table(dataset_name, dataset_version):
    """Delete dataset table."""
    ds_sq = dataset_name.replace("-", "_")

    s_name = f"{Config.SAMPLEDB_SCHEMA}.dataset_{ds_sq.lower()}_id_seq"

    with _db.session.begin_nested():
        try:
            ds = _db.session.query(Datasets) \
                .filter(Datasets.name == dataset_name, Datasets.version == dataset_version) \
                .first()
        except ValueError:
            raise RuntimeError(f'Dataset {dataset_name}-V{dataset_version} not found!')

        ds_table = ds.ds_table

        _db.session.delete(ds)
        _db.session.execute(f"DROP TABLE {Config.SAMPLEDB_SCHEMA}.{ds_table.name} CASCADE;")
        _db.session.execute(f"DROP SEQUENCE {s_name};")

    _db.session.commit()

    return
