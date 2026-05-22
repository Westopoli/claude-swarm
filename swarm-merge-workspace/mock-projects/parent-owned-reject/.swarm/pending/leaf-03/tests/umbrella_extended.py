# This file matches parent_owned glob tests/umbrella*.py
# It should be REJECTED by /swarm-merge
from src.cache import Cache
def test_extra():
    assert Cache() is not None
