import pytest
import json
from pathlib import Path
from basketbot import create_app
from basketbot.datamodel import defaults, register_events
from pytest_postgresql.factories import DatabaseJanitor #init_postgresql_database, drop_postgresql_database
from basketbot.datamodel import model as dm

TEST_DATA_DIR = Path(__file__).resolve().parent / 'data'

# @pytest.fixture(scope='session')
# def database(request, app):
#     '''
#     Create a Postgres database for the tests, and drop it when the tests are done.
#     '''
#     # Make sure that test env has had
#     # createuser test --createdb
#     db_conf = [app.config['DB_USER'], 
#             app.config['DB_HOST'], 
#             app.config['DB_PORT'], 
#             app.config['DB_NAME']
#             ]
#
#     yield init_postgresql_database(*db_conf)
#
#     # @request.addfinalizer
#     # def drop_database():
#     drop_postgresql_database(*db_conf, 13.2)

# Fixtures

@pytest.fixture(scope='session')
def database(request):
    '''
    Create a Postgres database for the tests, and drop it when the tests are done.
    '''
    # Make sure that test env has had
    # createuser test --createdb
    # Note other permissions are needed to dropdb? 
    # But can't figure out what these are. 
    # Using a superuser role definitely works though ¯\_(ツ)_/¯ 
    from basketbot.config import Testing
    db_conf = [
            Testing.DB_USER, 
            Testing.DB_HOST, 
            Testing.DB_PORT, 
            Testing.DB_NAME,
            Testing.DB_VERSION
            ]
    with DatabaseJanitor(*db_conf):
        yield


@pytest.fixture(scope="session")
def app(database):
    """ Exposes basketbot Flask app object """
    app = create_app("basketbot.config.Testing")
    with app.app_context():
        yield app


# @pytest.fixture(scope='session')
# def database(app):
#     """ Exposes the basketbot SQLAlchemy database object """
#     with app.app_context():
#         from basketbot import db
#         db.create_all()
#         defaults.create()
#         yield db
#     # Not using this teardown as should be handled by 
#     # pytest-flask-sqlalchemy extension
#     # db.drop_all()
#

# This fixture needed by pytest-flask-sqlalchemy extension
@pytest.fixture(scope='session')
def _db(app):
    from basketbot import db
    db.create_all()
    defaults.create(db.session)
    return db

@pytest.fixture(scope='function')
def db_with_items(db_session):
    defaults.create_test_defaults(db_session)
    # Register event listeners
    register_events(db_session)
    return db_session

@pytest.fixture(scope='function')
def mocked_http_urls(requests_mock):
    requests_mock.get('https://example_https.com', status_code=200)
    requests_mock.get('https://example_no_https.com', status_code=404)
    requests_mock.get('https://mail.mydomain.co.uk', status_code=200)

# Hooks

def pytest_generate_tests(metafunc):
    # Parametrize tests of scraping rule schema
    if "scraping_rule_schema_data" in metafunc.fixturenames:
        data = []
        with open(TEST_DATA_DIR / 'scraping_rule_schema_test_data.json', 'r') as file:
            for line in file:
                if line.strip(" ")[0:2]!='//': # Ignore comments
                    data.append(json.loads(line))
        metafunc.parametrize("scraping_rule_schema_data", data)

