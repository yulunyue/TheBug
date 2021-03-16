import re
import sys
import os


class A:
    V = []


class B(A):
    def __init__(self):
        self.V.append(1)


def test_py():
    b = B()
    assert type(A).__name__ == 'type'
    assert len(A.V) == 1
    assert len(b.V) == 1


def test_re():
    s = re.compile("/a/(.*)")
    assert s.match("/a/b").groups()[0] == 'b'
    c = re.compile(r".*\.bak")
    assert c.match("123.bak") is not None
    assert c.match("123.ba") is None


def test_import():
    old_path, sys.path = sys.path, []

    assert "socket" not in sys.modules
    try:
        import socket
    except:
        sys.path = old_path
        import socket
        assert "socket" in sys.modules
