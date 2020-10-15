from app import db, Datatype

db.drop_all()
db.create_all()

numeric = Datatype(name='numeric',extension='csv')
text = Datatype(name='text',extension='txt')
symbolic = Datatype(name='symbolic',extension='sym')
figure = Datatype(name='figure',extension='json')
logical = Datatype(name='logical',extension='log')

db.session.add(numeric)
db.session.add(text)
db.session.add(symbolic)
db.session.add(figure)
db.session.add(logical)

db.session.commit()
