from calculator import Speed, Item, RecipeSpeed, Recipe
import datetime


def test_speed_for_item_vs_time():
    graphite = Speed(item=Item("graphite", count=10),
                     time_sec=60
                     )
    assert graphite.speed == 10


def test_speed_for_item_vs_bigtime():
    graphite = Speed(item=Item("steel_plate", count=250),
                     time_sec=250*60
                     )
    assert graphite.speed == 1


def test_time_if_time_defined():
    graphite = Speed(item=Item("steel_plate", count=250),
                       time_sec=250*60
                       )
    assert graphite.time == datetime.timedelta(seconds=250*60)


def test_time_for_item_vs_rpm():
    graphite = Speed(item=Item("steel_plate", count=250),
                       speed_rpm=1
                       )
    assert graphite.time == datetime.timedelta(minutes=250)


def test_speed_if_speed_defined():
    graphite = Speed(item=Item("steel_plate", count=250),
                       speed_rpm=152
                       )
    assert graphite.speed == 152


def test_speed_up():
    graphite = Speed(item=Item("graphite", count=10),
                       time_sec=60
                       ) * 1.2
    assert graphite.speed == 12


def test_speed_down():
    graphite = Speed(item=Item("steel_plate", count=250),
                       speed_rpm=152
                       ) * 0.8
    assert graphite.speed == 121.6


def test_speed_add_positive():
    # 240 RPM
    steel_plate1 = Speed(item=Item("steel_plate", count=10000),
                           time_sec=2500)
    # 12 RPM
    steel_plate2 = Speed(item=Item("steel_plate", count=500),
                           time_sec=2500)
    assert (steel_plate1+steel_plate2).speed == 252


def test_speed_add_negative():
    # 240 RPM
    steel_plate1 = Speed(item=Item("steel_plate", count=10000),
                           time_sec=2500)
    # 12 RPM
    steel_plate2 = Speed(item=Item("steel_plate", count=500),
                           time_sec=2500)
    assert (steel_plate1 * (-1) + steel_plate2).speed == -228


def test_count_1min():
    graphite = RecipeSpeed(recipe=Recipe("graphite")).quantity(time_sec=60)
    assert graphite == 12


def test_count_1hour():
    graphite = RecipeSpeed(recipe=Recipe("graphite")).quantity(
        time_sec=60 * 60)
    assert graphite == 720


def test_count_1day():
    motherboard = RecipeSpeed(Recipe("motherboard"))
    assert motherboard.quantity(60*60*24) == 48