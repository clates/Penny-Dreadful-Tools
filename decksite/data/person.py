from munch import Munch

from shared.database import sqlescape

from decksite.data import deck, query
from decksite.database import db

def load_person(person_id):
    return load_people('p.id = {id}'.format(id=sqlescape(person_id)))[0]

def load_people(where_clause='1 = 1'):
    sql = """
        SELECT id, {person_query} AS name
        FROM person AS p
        WHERE {where_clause}
        ORDER BY name
    """.format(person_query=query.person_query(), where_clause=where_clause)
    people = [Person(r) for r in db().execute(sql)]
    set_decks(people)
    return people

def set_decks(people):
    people_by_id = {person.id: person for person in people}
    where_clause = 'person_id IN ({ids})'.format(ids=', '.join(str(k) for k in people_by_id.keys()))
    decks = deck.load_decks(where_clause)
    for p in people:
        p.decks = []
    for d in decks:
        people_by_id[d.person_id].decks.append(d)

class Person(Munch):
    pass
