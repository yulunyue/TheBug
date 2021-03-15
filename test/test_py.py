import re
class A:
    V=[]
class B(A):
    def __init__(self):
        self.V.append(1)
def test_py():
    b=B()
    assert type(A).__name__=='type'
    assert len(A.V)==1 
    assert len(b.V)==1
def test_re():
    s=re.compile("/a/(.*)")
    assert s.match("/a/b").groups()[0]=='b'