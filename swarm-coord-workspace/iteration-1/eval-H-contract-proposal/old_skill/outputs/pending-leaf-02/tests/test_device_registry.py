"""RED test for leaf-02. Tracks brief spec_lines 60-80."""
from src.types import Session
from src.device_registry import register_device


def test_register_device_sets_device_id_on_session():
    s = Session(user_id="u1", last_seen=0)
    register_device(s, "d1")
    assert s.device_id == "d1"


def test_register_device_overwrites_prior_device_id():
    s = Session(user_id="u1", last_seen=0)
    register_device(s, "d1")
    register_device(s, "d2")
    assert s.device_id == "d2"
