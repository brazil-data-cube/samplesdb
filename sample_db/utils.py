#
# This file is part of Sample Database Model.
# Copyright (C) 2020-2021 INPE.
#
# Sample Database Model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Utils Interface for the Sample Database Model ."""
from bdc_db.db import db as _db
from lccs_db.models import LucClassificationSystem
from sample_db_utils.core.driver import Driver
from sample_db_utils.core.postgis_accessor import PostgisAccessor
from sqlalchemy.orm.exc import NoResultFound

from .models import CollectMethod, Datasets, Users, make_observation


def get_user(user_full_name):
    """Return the user object."""
    try:
        user = _db.session.query(Users) \
            .filter_by(full_name=user_full_name) \
            .one()
    except NoResultFound:
        raise RuntimeError(f'User {user_full_name} not found!')

    return user


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


def create_sample(user_full_name, observation_table_name, classification_system_name, classification_system_version,
                  driver_type, **kwargs):
    """Create a dataset."""
    user = get_user(user_full_name)

    class_system = get_classification_system(classification_system_name, classification_system_version)

    _accessor = PostgisAccessor(system_id=class_system.id)

    observation_table = make_observation(table_name=observation_table_name, create=kwargs['obs_already_exist'])

    driver: Driver = driver_type(entries=kwargs['observation_file'],
                                 mappings=kwargs['mappings_json'],
                                 storager=_accessor,
                                 user=user.id,
                                 system=class_system)
    _db.session.commit()

    try:
        driver.load_data_sets()
        driver.store(observation_table)
        print('Observation table insert {}'.format(driver.__class__.__name__))
    except BaseException as err:
        print(err)

    affected_rows = len(driver.get_data_sets())

    collect_method = get_collect_method(kwargs['collect_method'])
 
    dataset_info = dict()
    
    dataset_info["classification_system_id"] = class_system.id
    dataset_info["user_id"] = user.id
    dataset_info["name"] = kwargs['dataset_name']
    dataset_info["start_date"] = kwargs['start_date']
    dataset_info["end_date"] = kwargs['end_date']
    dataset_info["collect_method_id"] = collect_method.id
    dataset_info["observation_table_name"] = observation_table.name
    dataset_info["version"] = kwargs['version']
    dataset_info["description"] = kwargs['description']

    if kwargs['metadata_json'] is not None:
        dataset_info["metadata_json"] = kwargs['metadata_json']
    
    dataset = Datasets(**dataset_info)

    with _db.session.begin_nested():
        _db.session.add(dataset)
    
    _db.session.commit()

    return affected_rows


def create_observation(user_full_name, observation_table_name, classification_system_name,
                       classification_system_version, driver_type, **kwargs):
    """Insert observation into database."""
    user = get_user(user_full_name)

    class_system = get_classification_system(classification_system_name, classification_system_version)

    observation_table = make_observation(table_name=observation_table_name, create=kwargs['obs_already_exist'])

    _accessor = PostgisAccessor(system_id=class_system.id)

    driver: Driver = driver_type(entries=kwargs['observation_file'],
                                 mappings=kwargs['mappings_json'],
                                 storager=_accessor,
                                 user=user.id,
                                 system=class_system)
    _db.session.commit()

    try:
        driver.load_data_sets()
        driver.store(observation_table)
        print('Observation table insert {}'.format(driver.__class__.__name__))
    except BaseException as err:
        _db.session.rollback()
        print(err)

    affected_rows = len(driver.get_data_sets())

    return affected_rows


def create_dataset(user_full_name, classification_system_name, classification_system_version, collect_method_name,
                   observation_name, **kwargs):
    """Insert a new dataset."""
    user = get_user(user_full_name)

    class_system = get_classification_system(classification_system_name, classification_system_version)

    collect_method = get_collect_method(collect_method_name)

    observation_full_name = f"{observation_name}_observations"

    dataset_info = dict()

    dataset_info["classification_system_id"] = class_system.id
    dataset_info["user_id"] = user.id
    dataset_info["name"] = kwargs['dataset_name']
    dataset_info["start_date"] = kwargs['start_date']
    dataset_info["end_date"] = kwargs['end_date']
    dataset_info["collect_method_id"] = collect_method.id
    dataset_info["observation_table_name"] = observation_full_name
    dataset_info["version"] = kwargs['version']
    dataset_info["description"] = kwargs['description']

    if kwargs['metadata_json'] is not None:
        dataset_info["metadata_json"] = kwargs['metadata_json']

    dataset = Datasets(**dataset_info)

    try:
        with _db.session.begin_nested():
            _db.session.add(dataset)
        _db.session.commit()
    except Exception as e:
        _db.session.rollback()
        raise e