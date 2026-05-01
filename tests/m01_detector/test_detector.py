import json
from pathlib import Path
from cpm.m01_detector.detector import BrowserDetector
from cpm.m01_detector.models import BrowserInfo, ProfileInfo

def test_detect_profiles_with_local_state(tmp_path: Path):
    # Setup mock local state
    local_state_path = tmp_path / "Local State"
    mock_state = {
        "profile": {
            "info_cache": {
                "Default": {"name": "Person 1"},
                "Profile 1": {"name": "Work"}
            },
            "last_used": "Profile 1"
        }
    }
    with open(local_state_path, "w", encoding="utf-8") as f:
        json.dump(mock_state, f)
        
    # Create profile dirs
    (tmp_path / "Default").mkdir()
    (tmp_path / "Profile 1").mkdir()
    
    profiles = BrowserDetector.detect_profiles(tmp_path)
    
    assert len(profiles) == 2
    assert any(p.name == "Person 1" and p.path == tmp_path / "Default" and not p.is_default for p in profiles)
    assert any(p.name == "Work" and p.path == tmp_path / "Profile 1" and p.is_default for p in profiles)

def test_detect_profiles_fallback(tmp_path: Path):
    # No Local State, just a Default folder
    (tmp_path / "Default").mkdir()
    
    profiles = BrowserDetector.detect_profiles(tmp_path)
    
    assert len(profiles) == 1
    assert profiles[0].name == "Default"
    assert profiles[0].path == tmp_path / "Default"
    assert profiles[0].is_default is True
