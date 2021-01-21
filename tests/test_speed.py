import calculator as c
import datetime


def test_speed_for_item_vs_time():
    graphite = c.Speed(item=c.Item("graphite", count=10),
                       time_sec=60
                       )
    assert graphite.speed == 10


def test_speed_for_item_vs_bigtime():
    graphite = c.Speed(item=c.Item("steel_plate", count=250),
                       time_sec=250*60
                       )
    assert graphite.speed == 1


def test_time_if_time_defined():
    graphite = c.Speed(item=c.Item("steel_plate", count=250),
                       time_sec=250*60
                       )
    assert graphite.time == datetime.timedelta(seconds=250*60)


def test_time_for_item_vs_rpm():
    graphite = c.Speed(item=c.Item("steel_plate", count=250),
                       speed_rpm=1
                       )
    assert graphite.time == datetime.timedelta(minutes=250)


def test_speed_if_speed_defined():
    graphite = c.Speed(item=c.Item("steel_plate", count=250),
                       speed_rpm=152
                       )
    assert graphite.speed == 152


def test_speed_up():
    graphite = c.Speed(item=c.Item("graphite", count=10),
                       time_sec=60
                       ) * 1.2
    assert graphite.speed == 12


def test_speed_down():
    graphite = c.Speed(item=c.Item("steel_plate", count=250),
                       speed_rpm=152
                       ) * 0.8
    assert graphite.speed == 121.6


def test_speed_add_positive():
    # 240 RPM
    steel_plate1 = c.Speed(item=c.Item("steel_plate", count=10000),
                           time_sec=2500)
    # 12 RPM
    steel_plate2 = c.Speed(item=c.Item("steel_plate", count=500),
                           time_sec=2500)
    assert (steel_plate1+steel_plate2).speed == 252


def test_speed_add_negative():
    # 240 RPM
    steel_plate1 = c.Speed(item=c.Item("steel_plate", count=10000),
                           time_sec=2500)
    # 12 RPM
    steel_plate2 = c.Speed(item=c.Item("steel_plate", count=500),
                           time_sec=2500)
    assert (steel_plate1 * (-1) + steel_plate2).speed == -228

