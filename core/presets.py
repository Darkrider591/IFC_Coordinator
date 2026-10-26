"""Presets manager for IFC Coordination settings.

Persists coordinate presets to JSON file in AppData or local directory.
"""

import os
import json
from typing import Dict, List, Any, Optional

DEFAULT_PRESETS: List[Dict[str, Any]] = [
    {
        "name": "Схема ТСС (из примера)",
        "description": "Параметры из образца BlenderBIM",
        "x": 4151394.0,
        "y": -4065338.0,
        "z": 184000.0,
        "should_rotate_first": True,
        "ax": 0.0,
        "ay": 0.0,
        "az": -48.55611111,
    },
    {
        "name": "Нулевые координаты (Сброс)",
        "description": "Без смещения и без поворота",
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
        "should_rotate_first": True,
        "ax": 0.0,
        "ay": 0.0,
        "az": 0.0,
    },
    {
        "name": "Поворот на 90° (в плане)",
        "description": "Поворот вокруг Z против часовой стрелки",
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
        "should_rotate_first": True,
        "ax": 0.0,
        "ay": 0.0,
        "az": 90.0,
    },
    {
        "name": "Поворот на 180° (в плане)",
        "description": "Разворот на 180 градусов",
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
        "should_rotate_first": True,
        "ax": 0.0,
        "ay": 0.0,
        "az": 180.0,
    },
]


def get_presets_file_path() -> str:
    """Returns path to presets file in user APPDATA or home dir."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        dir_path = os.path.join(appdata, "IFC_Coordinator")
    else:
        dir_path = os.path.join(os.path.expanduser("~"), ".ifc_coordinator")
    os.makedirs(dir_path, exist_ok=True)
    return os.path.join(dir_path, "presets.json")


def load_presets() -> List[Dict[str, Any]]:
    """Loads presets from disk or returns defaults."""
    file_path = get_presets_file_path()
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            pass
    return list(DEFAULT_PRESETS)


def save_presets(presets: List[Dict[str, Any]]) -> None:
    """Saves presets to disk."""
    file_path = get_presets_file_path()
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(presets, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving presets: {e}")


def add_or_update_preset(preset: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Adds or updates a preset by name."""
    presets = load_presets()
    idx = -1
    for i, p in enumerate(presets):
        if p["name"] == preset["name"]:
            idx = i
            break
    if idx >= 0:
        presets[idx] = preset
    else:
        presets.append(preset)
    save_presets(presets)
    return presets


def delete_preset(preset_name: str) -> List[Dict[str, Any]]:
    """Deletes a preset by name."""
    presets = load_presets()
    presets = [p for p in presets if p["name"] != preset_name]
    save_presets(presets)
    return presets
