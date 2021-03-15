from common.application import Application, UtilClassCall


class Tm:
    def a(self, c=0, **kwargs):
        return c+1


def fun():
    return "234"


def test_app():
    UtilClassCall(Tm(), "a").call(3) == 4
    app = Application([
        ("tm", Tm),
        ("fun", fun)
    ])
    app.call("tm/a", 0) == 1
    app.call("fun") == "234"
