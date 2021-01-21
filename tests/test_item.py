
import calculator as c


def test_item_exists():
    assert c.Item(key="coal").exists


def test_item_doesnt_exist():
    assert not c.Item(key="brilliant").exists


def test():
    assert c.Item("optic_fiber").name == "Optic Fiber"

