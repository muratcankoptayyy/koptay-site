"""Utility to execute sequential database migrations."""

from importlib import import_module
from types import ModuleType
from typing import Iterable

MIGRATION_MODULES: Iterable[str] = (
    "migrations.001_create_device_tokens",
    "migrations.002_create_reports_table",
)


def _run_upgrade(module: ModuleType) -> None:
    upgrade = getattr(module, "upgrade", None)
    if callable(upgrade):
        upgrade()


def main() -> None:
    for module_path in MIGRATION_MODULES:
        module = import_module(module_path)
        _run_upgrade(module)


if __name__ == "__main__":
    main()
