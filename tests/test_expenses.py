import pytest
from app import create_app
from app.db import db
from app.models import Expense
import datetime

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    with app.app_context():
        db.create_all()
        # Add some test data
        for i in range(30):
            expense = Expense(name=f'Expense {i}', amount=10.0, event_date=datetime.date.today())
            db.session.add(expense)
        db.session.commit()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_expenses_pagination(client):
    response = client.get('/expenses/')
    assert response.status_code == 200
    # Check for pagination controls
    assert b'Previous' in response.data
    assert b'Next' in response.data
    # Check that only 20 items are displayed
    assert response.data.count(b'<tr>') == 21 # 20 expenses + 1 header row

def test_expenses_pagination_page2(client):
    response = client.get('/expenses/?page=2')
    assert response.status_code == 200
    # Check for pagination controls
    assert b'Previous' in response.data
    assert b'Next' in response.data
    # Check that only 10 items are displayed
    assert response.data.count(b'<tr>') == 11 # 10 expenses + 1 header row
