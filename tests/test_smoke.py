import importlib

import pytest

import creditsense

PACKAGES = ["data", "model", "rag", "graph", "llm", "api", "audit", "ui"]


def test_version() -> None:
    assert creditsense.__version__ == "0.1.0"


@pytest.mark.parametrize("name", PACKAGES)
def test_subpackage_imports(name: str) -> None:
    importlib.import_module(f"creditsense.{name}")
