"""Smoke-Test für das installierte Processing-Paket."""

from importlib import import_module


def test_package_is_importable() -> None:
    """Das installierte Paket lässt sich ohne zusätzliche Suchpfade importieren."""
    package = import_module("soly_processing")

    assert package.__file__ is not None
