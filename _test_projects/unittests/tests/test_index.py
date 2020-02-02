import pytest
from _cob import mymodels


@pytest.fixture
def people():
    people = []
    for _ in range(10):
        person = mymodels.Person(first_name="First", last_name="Last")
        people.append(person)
        mymodels.db.session.add(person)
    mymodels.db.session.commit()
    yield people
    for person in people:
        mymodels.db.session.delete(person)
    mymodels.db.session.commit()


def test_person_model_and_view(webapp, people):
    assert webapp.get("/index/list_models") == [{"id": person.id} for person in people]
