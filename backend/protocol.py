"""
Coords Protocol v1 - Spec-Compliant Implementation
Based on: https://github.com/coordsapp/spec

L1 URI Format: coords:l1:v1:<lat>,<lng>,<alt>*<checksum>
Canonical Payload: v1|<lat>|<lng>|<alt>
Precision: lat/lng = 6 decimals, alt = 2 decimals
Checksum: FNV-1a 32-bit, lowercase hex, 8 chars
"""
from typing import Optional, Tuple, Dict
from decimal import Decimal, ROUND_HALF_UP


# =============================================================================
# FNV-1a 32-bit Constants
# =============================================================================
FNV1_32A_INIT = 2166136261  # 0x811c9dc5
FNV_32_PRIME = 16777619     # 0x01000193


def fnv1a_32(data: bytes) -> int:
    """
    FNV-1a 32-bit hash implementation per spec.
    
    Pseudocode from spec:
    hash = 2166136261
    for each byte b in utf8(payload):
      hash = hash XOR b
      hash = (hash * 16777619) mod 2^32
    """
    hash_value = FNV1_32A_INIT
    for byte in data:
        hash_value ^= byte
        hash_value = (hash_value * FNV_32_PRIME) & 0xFFFFFFFF
    return hash_value


# =============================================================================
# Canonical Formatting (Spec-Compliant)
# =============================================================================

def format_lat(lat: float) -> str:
    """Format latitude with exactly 6 decimal places"""
    d = Decimal(str(lat)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
    return f"{d:f}"


def format_lng(lng: float) -> str:
    """Format longitude with exactly 6 decimal places"""
    d = Decimal(str(lng)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
    return f"{d:f}"


def format_alt(alt: float) -> str:
    """Format altitude with exactly 2 decimal places"""
    d = Decimal(str(alt)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return f"{d:f}"


def build_canonical_payload(lat: float, lng: float, alt: float) -> str:
    """
    Build canonical payload for checksum calculation.
    Format: v1|<lat>|<lng>|<alt>
    
    Example: v1|37.774900|-122.419400|15.25
    """
    lat_str = format_lat(lat)
    lng_str = format_lng(lng)
    alt_str = format_alt(alt)
    return f"v1|{lat_str}|{lng_str}|{alt_str}"


# =============================================================================
# Checksum Generation
# =============================================================================

def generate_checksum(lat: float, lng: float, alt: float) -> str:
    """
    Generate FNV-1a 32-bit checksum per spec.
    
    Returns: lowercase hex, exactly 8 characters
    """
    payload = build_canonical_payload(lat, lng, alt)
    hash_value = fnv1a_32(payload.encode('utf-8'))
    return format(hash_value, '08x')


# =============================================================================
# L1 URI Generation
# =============================================================================

def generate_l1(lat: float, lng: float, alt: float = 0.0) -> str:
    """
    Generate L1 URI per spec.
    
    Format: coords:l1:v1:<lat>,<lng>,<alt>*<checksum>
    Example: coords:l1:v1:37.774900,-122.419400,15.25*1c86401e
    
    Note: Altitude is REQUIRED per spec (defaults to 0.0)
    """
    lat_str = format_lat(lat)
    lng_str = format_lng(lng)
    alt_str = format_alt(alt)
    checksum = generate_checksum(lat, lng, alt)
    
    return f"coords:l1:v1:{lat_str},{lng_str},{alt_str}*{checksum}"


# =============================================================================
# L1 URI Parsing & Validation
# =============================================================================

def parse_l1(l1_uri: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    Parse and validate L1 URI.
    
    Returns: (valid, data_dict, error_message)
    
    data_dict contains:
    - lat: float
    - lng: float
    - alt: float
    - checksum: str (provided)
    - expected_checksum: str (computed)
    - checksum_valid: bool
    - canonical_payload: str
    """
    try:
        # Validate prefix
        if not l1_uri.startswith("coords:l1:v1:"):
            return False, None, "Invalid prefix. Expected 'coords:l1:v1:'"
        
        # Extract content after prefix
        content = l1_uri[13:]  # len("coords:l1:v1:") = 13
        
        # Split on checksum separator
        if '*' not in content:
            return False, None, "Missing checksum separator '*'"
        
        coord_part, provided_checksum = content.rsplit('*', 1)
        
        # Validate checksum format
        if len(provided_checksum) != 8:
            return False, None, f"Checksum must be 8 hex chars, got {len(provided_checksum)}"
        
        try:
            int(provided_checksum, 16)
        except ValueError:
            return False, None, "Checksum must be valid hexadecimal"
        
        # Parse coordinates (comma-separated in URI)
        parts = coord_part.split(',')
        if len(parts) != 3:
            return False, None, "Expected exactly 3 components: lat,lng,alt"
        
        lat_str, lng_str, alt_str = parts
        
        try:
            lat = float(lat_str)
            lng = float(lng_str)
            alt = float(alt_str)
        except ValueError as e:
            return False, None, f"Invalid numeric value: {e}"
        
        # Validate ranges
        if not (-90 <= lat <= 90):
            return False, None, f"Latitude {lat} out of range [-90, 90]"
        if not (-180 <= lng <= 180):
            return False, None, f"Longitude {lng} out of range [-180, 180]"
        
        # Compute expected checksum
        expected_checksum = generate_checksum(lat, lng, alt)
        checksum_valid = provided_checksum.lower() == expected_checksum.lower()
        
        # Build canonical payload for reference
        canonical_payload = build_canonical_payload(lat, lng, alt)
        
        return True, {
            "lat": lat,
            "lng": lng,
            "alt": alt,
            "checksum": provided_checksum.lower(),
            "expected_checksum": expected_checksum,
            "checksum_valid": checksum_valid,
            "canonical_payload": canonical_payload
        }, None
        
    except Exception as e:
        return False, None, f"Parse error: {str(e)}"


# =============================================================================
# L2 Handle Functions
# =============================================================================

def generate_l2_handle(tenant: str, *path_parts: str) -> str:
    """
    Generate L2 human-friendly handle.
    Format: @<tenant>/<path>
    Example: @acme/warehouse/dock-1
    """
    path = "/".join(path_parts)
    return f"@{tenant}/{path}"


def parse_l2_handle(handle: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    Parse L2 handle.
    Returns: (valid, data_dict, error_message)
    """
    try:
        if not handle.startswith("@"):
            return False, None, "L2 handle must start with '@'"
        
        content = handle[1:]
        parts = content.split("/")
        
        if len(parts) < 2:
            return False, None, "L2 handle must have tenant/path format"
        
        tenant = parts[0]
        path = "/".join(parts[1:])
        
        return True, {
            "tenant": tenant,
            "path": path,
            "parts": parts[1:],
            "full_handle": handle
        }, None
        
    except Exception as e:
        return False, None, f"Parse error: {str(e)}"


# =============================================================================
# What3Words-style Simulation (Offline, Deterministic)
# =============================================================================

# NATO phonetic + logistics words for demonstration
WORD_LIST = [
    "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
    "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa",
    "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey", "xray",
    "yankee", "zulu", "anchor", "beacon", "cargo", "depot", "express", "freight",
    "gateway", "harbor", "intake", "junction", "keystone", "loading", "manifest",
    "nexus", "outbound", "platform", "queue", "receiving", "staging", "terminal"
]


def coords_to_words(lat: float, lng: float) -> str:
    """
    Generate deterministic 3-word code from coordinates.
    Offline simulation - no external dependencies.
    """
    # Use canonical format for consistency
    coord_str = f"{format_lat(lat)}|{format_lng(lng)}"
    hash_val = fnv1a_32(coord_str.encode('utf-8'))
    
    n = len(WORD_LIST)
    w1 = WORD_LIST[hash_val % n]
    w2 = WORD_LIST[(hash_val >> 8) % n]
    w3 = WORD_LIST[(hash_val >> 16) % n]
    
    return f"{w1}.{w2}.{w3}"


# =============================================================================
# Test Vectors Validation
# =============================================================================

def validate_test_vectors() -> list:
    """
    Validate implementation against spec test vectors.
    Returns list of test results.
    """
    test_vectors = [
        {
            "lat": 37.774900, "lng": -122.419400, "alt": 15.25,
            "expected_checksum": "1c86401e",
            "expected_uri": "coords:l1:v1:37.774900,-122.419400,15.25*1c86401e"
        },
        {
            "lat": 0.000000, "lng": 0.000000, "alt": 0.00,
            "expected_checksum": "8922cf52",
            "expected_uri": "coords:l1:v1:0.000000,0.000000,0.00*8922cf52"
        },
        {
            "lat": -33.868800, "lng": 151.209300, "alt": 58.70,
            "expected_checksum": "905f6970",
            "expected_uri": "coords:l1:v1:-33.868800,151.209300,58.70*905f6970"
        },
        {
            "lat": 48.856600, "lng": 2.352200, "alt": 35.40,
            "expected_checksum": "ae6c07e1",
            "expected_uri": "coords:l1:v1:48.856600,2.352200,35.40*ae6c07e1"
        }
    ]
    
    results = []
    for tv in test_vectors:
        checksum = generate_checksum(tv["lat"], tv["lng"], tv["alt"])
        uri = generate_l1(tv["lat"], tv["lng"], tv["alt"])
        
        results.append({
            "input": f"({tv['lat']}, {tv['lng']}, {tv['alt']})",
            "expected_checksum": tv["expected_checksum"],
            "actual_checksum": checksum,
            "checksum_pass": checksum == tv["expected_checksum"],
            "expected_uri": tv["expected_uri"],
            "actual_uri": uri,
            "uri_pass": uri == tv["expected_uri"]
        })
    
    return results


if __name__ == "__main__":
    # Run test vector validation
    print("Validating against spec test vectors...\n")
    results = validate_test_vectors()
    
    all_pass = True
    for r in results:
        status = "✓ PASS" if (r["checksum_pass"] and r["uri_pass"]) else "✗ FAIL"
        all_pass = all_pass and r["checksum_pass"] and r["uri_pass"]
        print(f"{status}: {r['input']}")
        if not r["checksum_pass"]:
            print(f"  Checksum: expected {r['expected_checksum']}, got {r['actual_checksum']}")
        if not r["uri_pass"]:
            print(f"  URI: expected {r['expected_uri']}")
            print(f"       got      {r['actual_uri']}")
    
    print(f"\nOverall: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
