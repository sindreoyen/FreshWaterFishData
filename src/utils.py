from shapely import LineString

def normalize_key(waterbody, region_id):
    if waterbody is None or region_id is None:
        return None
    """Create a normalized key for consistent grouping."""
    return f"{waterbody.strip().lower()}" # + f"_{region_id.strip().lower()}"

def calculate_midpoint(geom):
    if isinstance(geom, LineString):
        return geom.coords[0]  # Returns the first coordinate (start point)
        # return geom.interpolate(0.5, normalized=True)
    return geom.centroid  # Fallback to centroid if not a LineString