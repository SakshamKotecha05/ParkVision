"""Streamlit render functions, one module per dashboard tab.

Each tab module exposes ``render(data: dict) -> None`` where ``data`` is the
dict returned by ``parkvision.app_data.load_all()``.
"""
