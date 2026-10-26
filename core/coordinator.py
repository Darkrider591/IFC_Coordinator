"""IFC Coordination Engine (OffsetObjectPlacements).

Performs lossless transformation (translation and rotation) of IFC models
by updating root object placements, matching the behavior of BlenderBIM / Bonsai
IFC Patch (recipe 'OffsetObjectPlacements').
Preserves all geometry, GUIDs, attributes, property sets, and relationships intact.
"""

import os
import sys
import math
import time
import shutil
import logging
from typing import Optional, Callable, Dict, Any, List, Set, Tuple

# Preload shape to prevent circular import bug in some ifcopenshell versions
try:
    import ifcopenshell.util.shape
except Exception:
    pass

import ifcopenshell
import ifcopenshell.util.placement
import numpy as np


class CoordinationError(Exception):
    """Custom exception for coordination failures."""
    pass


def get_absolute_placement(placement: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """Traverse placement hierarchy to find the root placement."""
    while getattr(placement, "PlacementRelTo", None) is not None:
        placement = placement.PlacementRelTo
    return placement


def build_rotation_matrix(ax_deg: float = 0.0, ay_deg: float = 0.0, az_deg: float = 0.0) -> np.ndarray:
    """Build composite 3D rotation matrix from Euler angles in decimal degrees.
    Order of rotations: X, then Y, then Z (standard CAD/BIM convention).
    Positive angle is counterclockwise around the positive axis.
    """
    Rx = np.eye(4)
    Ry = np.eye(4)
    Rz = np.eye(4)

    if ax_deg:
        rad = math.radians(ax_deg)
        c, s = math.cos(rad), math.sin(rad)
        Rx[1, 1] = c
        Rx[1, 2] = -s
        Rx[2, 1] = s
        Rx[2, 2] = c

    if ay_deg:
        rad = math.radians(ay_deg)
        c, s = math.cos(rad), math.sin(rad)
        Ry[0, 0] = c
        Ry[0, 2] = s
        Ry[2, 0] = -s
        Ry[2, 2] = c

    if az_deg:
        rad = math.radians(az_deg)
        c, s = math.cos(rad), math.sin(rad)
        Rz[0, 0] = c
        Rz[0, 1] = -s
        Rz[1, 0] = s
        Rz[1, 1] = c

    # Order of composition matching BlenderBIM OffsetObjectPlacements
    return Rz @ Ry @ Rx


def build_transformation_matrix(
    x: float,
    y: float,
    z: float,
    ax: float = 0.0,
    ay: float = 0.0,
    az: float = 0.0,
    should_rotate_first: bool = True
) -> np.ndarray:
    """Build 4x4 affine transformation matrix.

    :param x, y, z: Translation offsets in project length units.
    :param ax, ay, az: Rotation angles in decimal degrees.
    :param should_rotate_first: If True, transformation is T @ R (first rotate, then shift).
                                If False, transformation is R @ T (first shift, then rotate).
    """
    translate = np.eye(4)
    translate[0, 3] = float(x)
    translate[1, 3] = float(y)
    translate[2, 3] = float(z)

    rotate = build_rotation_matrix(float(ax), float(ay), float(az))

    if should_rotate_first:
        return translate @ rotate
    else:
        return rotate @ translate


def coordinate_ifc(
    input_path: str,
    output_path: str,
    x: float,
    y: float,
    z: float,
    ax: float = 0.0,
    ay: float = 0.0,
    az: float = 0.0,
    should_rotate_first: bool = True,
    create_backup: bool = True,
    log_callback: Optional[Callable[[str, str], None]] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None,
) -> Dict[str, Any]:
    """Applies OffsetObjectPlacements coordination to an IFC file.

    :param input_path: Source IFC file path.
    :param output_path: Destination IFC file path (can be same as input).
    :param x, y, z: Offsets in project units.
    :param ax, ay, az: Angles in degrees.
    :param should_rotate_first: Rotate first then translate (default True).
    :param create_backup: If overwriting, creates .bak file.
    :param log_callback: Function taking (message, level: 'info'|'success'|'warning'|'error').
    :param progress_callback: Function taking (percentage 0..100, status_text).
    :param cancel_check: Function returning True if operation was cancelled.
    :return: Summary dictionary with execution statistics.
    """
    start_time = time.time()

    def log(msg: str, lvl: str = "info"):
        if log_callback:
            log_callback(msg, lvl)

    def set_progress(pct: int, text: str):
        if progress_callback:
            progress_callback(pct, text)

    def is_cancelled() -> bool:
        return cancel_check() if cancel_check else False

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Файл не найден: {input_path}")

    log(f"Открытие файла: {os.path.basename(input_path)}", "info")
    set_progress(10, "Чтение структуры IFC...")

    if is_cancelled():
        raise InterruptedError("Операция отменена пользователем.")

    input_size_bytes = os.path.getsize(input_path)

    try:
        model = ifcopenshell.open(input_path)
    except Exception as e:
        raise CoordinationError(f"Ошибка чтения IFC файла: {e}")

    schema = model.schema
    log(f"Схема IFC: {schema}, размер: {input_size_bytes / (1024 * 1024):.2f} МБ", "info")
    set_progress(30, "Анализ дерева размещений (IfcLocalPlacement)...")

    if is_cancelled():
        raise InterruptedError("Операция отменена пользователем.")

    # 1. Discover all root placements
    products = model.by_type("IfcProduct")
    products_with_placement = 0
    absolute_placements: Set[ifcopenshell.entity_instance] = set()

    for product in products:
        if not product.ObjectPlacement:
            continue
        products_with_placement += 1
        root_placement = get_absolute_placement(product.ObjectPlacement)
        if root_placement.is_a("IfcLocalPlacement"):
            absolute_placements.add(root_placement)

    log(
        f"Найдено элементов IfcProduct: {len(products)} "
        f"(с размещением: {products_with_placement}), "
        f"корневых систем координат (root placements): {len(absolute_placements)}",
        "info"
    )

    if not absolute_placements:
        log("В модели не найдено корневых IfcLocalPlacement. Проверьте содержимое модели.", "warning")

    set_progress(50, "Расчет матрицы координации...")

    if is_cancelled():
        raise InterruptedError("Операция отменена пользователем.")

    # 2. Build 4x4 transformation matrix
    T = build_transformation_matrix(x, y, z, ax, ay, az, should_rotate_first)
    log(
        f"Параметры трансформации: dX={x}, dY={y}, dZ={z}, "
        f"Ax={ax}°, Ay={ay}°, Az={az}°, RotateFirst={should_rotate_first}",
        "info"
    )

    # 3. Transform each root placement
    set_progress(60, "Применение координатной матрицы к размещениям...")
    modified_count = 0

    for placement in absolute_placements:
        if is_cancelled():
            raise InterruptedError("Операция отменена пользователем.")

        current_matrix = ifcopenshell.util.placement.get_local_placement(placement)
        new_matrix = T @ current_matrix

        # Extract axes and origin
        x_axis = np.array((new_matrix[0, 0], new_matrix[1, 0], new_matrix[2, 0]))
        z_axis = np.array((new_matrix[0, 2], new_matrix[1, 2], new_matrix[2, 2]))
        origin = np.array((new_matrix[0, 3], new_matrix[1, 3], new_matrix[2, 3]))

        # Orthonormalize via a2p (Gram-Schmidt)
        ortho_mat = ifcopenshell.util.placement.a2p(origin, z_axis, x_axis)

        # Create standard IfcAxis2Placement3D
        pt = model.createIfcCartesianPoint(ortho_mat[:3, 3].tolist())
        axis_dir = model.createIfcDirection(ortho_mat[:3, 2].tolist())
        ref_dir = model.createIfcDirection(ortho_mat[:3, 0].tolist())

        placement.RelativePlacement = model.createIfcAxis2Placement3D(pt, axis_dir, ref_dir)
        modified_count += 1

    log(f"Успешно обновлено корневых систем координат: {modified_count}", "info")
    set_progress(80, "Сохранение выходного файла IFC...")

    if is_cancelled():
        raise InterruptedError("Операция отменена пользователем.")

    # 4. Save to destination
    is_overwrite = os.path.abspath(input_path) == os.path.abspath(output_path)
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Write to temp file first to ensure atomicity and never corrupt data
    temp_output_path = output_path + f".tmp_{os.getpid()}_{int(time.time())}"
    try:
        model.write(temp_output_path)

        if is_overwrite:
            if create_backup:
                backup_path = input_path + ".bak"
                log(f"Создание резервной копии: {os.path.basename(backup_path)}", "info")
                shutil.copy2(input_path, backup_path)
            # Replace atomic on windows
            os.replace(temp_output_path, output_path)
        else:
            if os.path.exists(output_path):
                os.remove(output_path)
            os.replace(temp_output_path, output_path)

    except Exception as e:
        if os.path.exists(temp_output_path):
            try:
                os.remove(temp_output_path)
            except Exception:
                pass
        raise CoordinationError(f"Ошибка записи IFC файла: {e}")

    elapsed = time.time() - start_time
    output_size_bytes = os.path.getsize(output_path)
    set_progress(100, "Готово!")
    log(
        f"Файл успешно скоординирован за {elapsed:.2f} сек. "
        f"Результат сохранен в: {output_path} ({output_size_bytes / (1024 * 1024):.2f} МБ)",
        "success"
    )

    return {
        "status": "success",
        "input_path": input_path,
        "output_path": output_path,
        "schema": schema,
        "products_count": len(products),
        "products_with_placement": products_with_placement,
        "root_placements_modified": modified_count,
        "input_size_bytes": input_size_bytes,
        "output_size_bytes": output_size_bytes,
        "elapsed_seconds": elapsed,
    }
