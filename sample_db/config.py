#
# This file is part of Sample Database Model.
# Copyright (C) 2019 INPE.
#
# Sample Database Model is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Define config file for Brazil Data Cube Sample Database Model."""

import os

CURRENT_DIR = os.path.dirname(__file__)


class Config:
    """Define common config along contexts."""

    SAMPLEDB_SCHEMA_NAME = os.environ.get('LCCS_SCHEMA_NAME', 'lccs')