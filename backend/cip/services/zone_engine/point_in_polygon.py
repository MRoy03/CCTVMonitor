"""Attributes a detection's bounding box to a zone, if any, via Shapely
point-in-polygon. Both bounding boxes and zone polygons are stored in
normalized 0-1 coordinates relative to the camera's reference frame, so this
works regardless of actual frame resolution.
"""

from shapely.geometry import Point, Polygon


def bbox_ground_point(bounding_box: dict) -> tuple[float, float]:
    """Bottom-center of the box — more accurate than the centroid for "is
    this person standing in this zone" (their feet, not their head/torso
    center, are what's actually on the ground inside or outside a zone).
    """
    x = (bounding_box["x1"] + bounding_box["x2"]) / 2
    y = bounding_box["y2"]
    return x, y


def find_containing_zone_name(bounding_box: dict, zones: list) -> str | None:
    """`zones` is a list of Zone ORM objects (or anything with .name and
    .polygon_coordinates). Returns the first matching zone's name, or None.
    """
    point = Point(*bbox_ground_point(bounding_box))
    for zone in zones:
        if len(zone.polygon_coordinates) < 3:
            continue
        if Polygon(zone.polygon_coordinates).contains(point):
            return zone.name
    return None
