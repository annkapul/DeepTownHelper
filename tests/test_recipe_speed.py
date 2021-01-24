import calculator as c


def test_recipe_speed():
    print(c.RecipeSpeed(c.Recipe("steel_plate", count=10)).all)
    assert str(c.RecipeSpeed(c.Recipe("steel_plate", count=10)).all) == "[Steel Bar x -2.5 RPM, Steel Plate x 0.5 RPM]"
    assert str(c.RecipeSpeed(c.Recipe("steel_plate", count=100)).all) == "[Steel Bar x -2.5 RPM, Steel Plate x 0.5 RPM]"
    # TODO Incorrwct values for 720
    assert str(c.RecipeSpeed(c.Recipe("steel_plate", count=720)).all) == "[Steel Bar x -2.5 RPM, Steel Plate x 0.5 RPM]"

def test_sum_speed():
    prod1 = c.RecipeSpeed(c.Recipe("steel_plate", count=10)).all
    prod2 = c.RecipeSpeed(c.Recipe("steel_plate", count=1200)).all
    assert str(c.sum_items_by_rpm(prod1 + prod2)) == "[Steel Bar x -5.0 RPM, Steel Plate x 1.0 RPM]"


def test_boosters():
        boosters = {
            "crafting": {
                "bot": 1.2,
                "tech_lab": 2,
                },
            "smelting": {
                "tech_lab": 2,
                "pumpkin": 2
                }
        }
        prod2 = c.RecipeSpeed(c.Recipe("steel_plate"), boosters=boosters)
        assert "tech_lab" in prod2.boosters.keys()
        assert "pumpkin" in prod2.boosters.keys()
        assert str(prod2.all) == "[Steel Bar x -10.0 RPM, Steel Plate x 2.0 RPM]"
