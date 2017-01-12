from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy import event

metadata = MetaData()

def _inspect_for_auditing(conn, cursor, statement, parameters, context, executemany):
    import pdb; pdb.set_trace()
    if statement and statement.lstrip()[:6].upper() == 'SELECT':
        # Allow any SELECTs, so we don't bother setting auditing variables unless
        # we need it.
        return
        

e = create_engine('oracle://kent:kent@localhost:1521/xe?use_ansi=False', echo=True)

import pdb; pdb.set_trace()

conn=e.connect()

event.listen(e, 'before_cursor_execute', _inspect_for_auditing)

conn.execute('SELECT * FROM user_tables')


#event.listen(conn, 'before_cursor_execute', _inspect_for_auditing)
conn._has_events = True

conn.execute('SELECT * FROM user_tables')


