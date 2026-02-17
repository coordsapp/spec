"""
Coords - Protocol Utilities
L1 Immutable Spatial Identifier with FNV-1a checksum
"""
import struct
from typing import Optional, Tuple


def fnv1a_32(data: bytes) -> int:
    """FNV-1a 32-bit hash"""
    FNV_32_PRIME = 0x01000193
    FNV1_32A_INIT = 0x811c9dc5
    
    hash_value = FNV1_32A_INIT
    for byte in data:
        hash_value ^= byte
        hash_value = (hash_value * FNV_32_PRIME) & 0xFFFFFFFF
    return hash_value


def generate_l1_checksum(lat: float, lng: float, altitude: Optional[float] = None) -> str:
    """Generate FNV-1a checksum for coordinates"""
    if altitude is not None:
        data = f"{lat},{lng},{altitude}".encode('utf-8')
    else:
        data = f"{lat},{lng}".encode('utf-8')
    
    checksum = fnv1a_32(data)
    return format(checksum, '08x')


def generate_l1_string(lat: float, lng: float, altitude: Optional[float] = None) -> str:
    """
    Generate L1 immutable spatial identifier
    Format: coords:l1:v1:38.8977,-77.0365,12.3*a7f3b912
    """
    checksum = generate_l1_checksum(lat, lng, altitude)
    
    if altitude is not None:
        coord_part = f"{lat},{lng},{altitude}"
    else:
        coord_part = f"{lat},{lng}"
    
    return f"coords:l1:v1:{coord_part}*{checksum}"


def parse_l1_string(l1_string: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Parse and validate L1 string
    Returns: (valid, data_dict, error_message)
    """
    try:
        # Check prefix
        if not l1_string.startswith("coords:l1:v1:"):
            return False, None, "Invalid L1 prefix. Expected 'coords:l1:v1:'"
        
        # Extract coordinate and checksum parts
        content = l1_string[13:]  # Remove "coords:l1:v1:"
        
        if '*' not in content:
            return False, None, "Missing checksum separator '*'"
        
        coord_part, provided_checksum = content.rsplit('*', 1)
        
        # Parse coordinates
        parts = coord_part.split(',')
        if len(parts) < 2 or len(parts) > 3:
            return False, None, "Invalid coordinate format. Expected lat,lng or lat,lng,altitude"
        
        lat = float(parts[0])
        lng = float(parts[1])
        altitude = float(parts[2]) if len(parts) == 3 else None
        
        # Validate coordinate ranges
        if not (-90 <= lat <= 90):
            return False, None, f"Latitude {lat} out of range [-90, 90]"
        if not (-180 <= lng <= 180):
            return False, None, f"Longitude {lng} out of range [-180, 180]"
        
        # Verify checksum
        expected_checksum = generate_l1_checksum(lat, lng, altitude)
        checksum_valid = provided_checksum.lower() == expected_checksum.lower()
        
        return True, {
            "lat": lat,
            "lng": lng,
            "altitude": altitude,
            "checksum": provided_checksum,
            "expected_checksum": expected_checksum,
            "checksum_valid": checksum_valid
        }, None
        
    except ValueError as e:
        return False, None, f"Parse error: {str(e)}"
    except Exception as e:
        return False, None, f"Unexpected error: {str(e)}"


def generate_l2_handle(tenant: str, *path_parts: str) -> str:
    """
    Generate L2 human-friendly handle
    Format: @acme/warehouse/dock-1
    """
    path = "/".join(path_parts)
    return f"@{tenant}/{path}"


def parse_l2_handle(handle: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Parse L2 handle
    Returns: (valid, data_dict, error_message)
    """
    try:
        if not handle.startswith("@"):
            return False, None, "L2 handle must start with '@'"
        
        content = handle[1:]  # Remove "@"
        parts = content.split("/")
        
        if len(parts) < 2:
            return False, None, "L2 handle must have at least tenant/path"
        
        tenant = parts[0]
        path = "/".join(parts[1:])
        
        return True, {
            "tenant": tenant,
            "path": path,
            "parts": parts[1:]
        }, None
        
    except Exception as e:
        return False, None, f"Parse error: {str(e)}"


# What3Words-like simulation (offline, deterministic)
def coords_to_words(lat: float, lng: float) -> str:
    """
    Generate deterministic 3-word code from coordinates
    Offline simulation - no external dependencies
    """
    # Word lists (subset for demonstration)
    WORDS = [
        "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
        "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa",
        "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "xray",
        "yankee", "zulu", "anchor", "beacon", "cargo", "depot", "express", "freight"
    ]
    
    # Deterministic hash based on coordinates
    coord_str = f"{lat:.6f},{lng:.6f}"
    hash_val = fnv1a_32(coord_str.encode('utf-8'))
    
    # Generate 3 words
    w1 = WORDS[hash_val % len(WORDS)]
    w2 = WORDS[(hash_val >> 8) % len(WORDS)]
    w3 = WORDS[(hash_val >> 16) % len(WORDS)]
    
    return f"{w1}.{w2}.{w3}"


def words_to_coords(words: str) -> Optional[Tuple[float, float]]:
    """
    This is a simulation - in production, would need a proper lookup table
    Returns None as reverse lookup isn't implemented for simulation
    """
    return None
