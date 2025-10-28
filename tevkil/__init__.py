"""Tevkil application package.

This package progressively modularizes the legacy single-file Flask app
into a maintainable factory/blueprint architecture.  During the migration
period we expose helper utilities so existing imports continue to work.
"""

from .config import Config, DevelopmentConfig, get_config  # noqa: F401
