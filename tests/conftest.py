import pytest
from app import create_app
from core.database import db
import os

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    os.environ['FLASK_TESTING'] = 'true'
    _app = create_app()
    
    # Establish an application context
    ctx = _app.app_context()
    ctx.push()
    
    # Create the database and tables
    db.create_all()
    
    yield _app
    
    # Clean up
    db.session.remove()
    db.drop_all()
    ctx.pop()

@pytest.fixture(scope='session')
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture(scope='session')
def runner(app):
    """Create a test runner for the app's CLI commands."""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def session():
    """Create a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Create a session with the connection
    session = db.create_scoped_session(
        options={"bind": connection, "binds": {}}
    )
    
    db.session = session
    
    yield session
    
    # Rollback the transaction and close the connection
    session.close()
    transaction.rollback()
    connection.close()
