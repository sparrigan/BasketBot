from basketbot import create_app, db
from basketbot.datamodel import defaults

@pytest.fixture(scope="module")
def app():
    """ Exposes basketbot Flask app object """
    return create_app("basketbot.config.Testing")

@pytest.fixture()
def database(app):
    """ Exposes the basketbot SQLAlchemy database object """
    with db.app.app_context():
        db.create_all()
        defaults.create()
        yield db
    db.drop_all()

@pytest.fixture()
def session(database):
    """ Return SQLAlchemy database session """
    return database.session()

@pytest.fixture()
def item_urls(database):
    """ Return some item URLs to test on """
