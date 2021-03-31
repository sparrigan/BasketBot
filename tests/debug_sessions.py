import sqlalchemy as sa
from sqlalchemy import inspect

from basketbot import create_app
from basketbot import db 
from basketbot.datamodel import model as dm
app = create_app()
app.app_context().push()


connection = db.engine.connect()
transaction = connection.begin()

# Bind a session to the transaction. The empty `binds` dict is necessary
# when specifying a `bind` option, or else Flask-SQLAlchemy won't scope
# the connection properly
options = dict(bind=connection, binds={})
session = db.create_scoped_session(options=options)

# Make sure the session, connection, and transaction can't be closed by accident in
# the codebase
connection.force_close = connection.close
transaction.force_rollback = transaction.rollback

connection.close = lambda: None
transaction.rollback = lambda: None
session.close = lambda: None

# Begin a nested transaction (any new transactions created in the codebase
# will be held until this outer transaction is committed or closed)
session.begin_nested()

# Each time the SAVEPOINT for the nested transaction ends, reopen it
@sa.event.listens_for(session, 'after_transaction_end')
def restart_savepoint(session, trans):
    if trans.nested and not trans._parent.nested:
        # ensure that state is expired the way
        # session.commit() at the top level normally does
        session.expire_all()

        session.begin_nested()

# Force the connection to use nested transactions
connection.begin = connection.begin_nested

# If an object gets moved to the 'detached' state by a call to flush the session,
# add it back into the session (this allows us to see changes made to objects
# in the context of a test, even when the change was made elsewhere in
# the codebase)
@sa.event.listens_for(session, 'persistent_to_detached')
@sa.event.listens_for(session, 'deleted_to_detached')
def rehydrate_object(session, obj):
    session.add(obj)


SESSION_INFO_KEY = 'altered_regions'

@sa.event.listens_for(session, "before_flush")
def check_for_items(session, flush_context, instances):
    """
    Detect whether any items have been altered or addded during a flush
    and take a note of their regions in the Session.info dict
    """
    altered_regions = set()
    print("In flush check")
    print(session.new.union(session.dirty))
    for _ in session.new.union(session.dirty):
        if isinstance(_, Item):
            # Idea here is to check only for cases where the specific fields of Item have changed, to prevent recursion
            state = inspect(_)
            if len(state.attrs.name.history.added)>0:
                altered_regions.update(_.regions)
    print(altered_regions)
    print("Done in flush check")
    if SESSION_INFO_KEY in session.info:
        session.info[SESSION_INFO_KEY].update(altered_regions)
    else:
        session.info[SESSION_INFO_KEY] = altered_regions

@sa.event.listens_for(session, "after_rollback")
def remove_items(session):
    """
    Remove any altered regions from Session.info dict, as there has been
    a rollback
    """
    if SESSION_INFO_KEY in session.info:
        del session.info[SESSION_INFO_KEY]

@sa.event.listens_for(session, "before_commit")
def update_basket_versions(session):
# def update_basket_version(session, flush_context, instances):
    """
    Using the list of regions stored in Session.info dict, update the
    basket_versions for these regions, as some of their basket items have
    been added/edited.
    """
    session.flush() # see https://stackoverflow.com/a/36732359 for why this is here
    # Should really optimize this all if it's going to run on every
    # session flush (DB trigger?)
    # altered_regions = set()
    # for _ in session.new.union(session.dirty):
    #     if isinstance(_, Item):
    #         altered_regions.update(_.region)
    # print("Dirty session")
    # print(session.dirty)
    # print(session)

    print("Triggered before commit")
    print(session.info)
    if len(altered_regions:=session.info.get(SESSION_INFO_KEY, set()))>0:
        print("Inside Loop")
        for region in altered_regions:
            region.basket_version += 1
            # Trigger alerts for any regions with updated basket_versions
            # could go here if there is not also an update in this commit 
            # for their baskets
        session.add_all(altered_regions)
        for ar in altered_regions:
            print(ar.basket_version)
        # session.commit()
        # session.flush()

    # Make sure to clear altered_regions from session.info
    if SESSION_INFO_KEY in session.info:
        del session.info[SESSION_INFO_KEY]
