from _cob import mymodels


def test_person():
    p = mymodels.Person(first_name="First", last_name="Last")
    assert p.full_name == "First Last"
