# This module is used for managing Connection of database

from pathlib import Path
import sqlite3
from p2app.events.database import (
    OpenDatabaseEvent, CloseDatabaseEvent, DatabaseOpenedEvent,
    DatabaseOpenFailedEvent, DatabaseClosedEvent)
class Database_Handler:
    # Handling opening and closing the database
    def __init__(self):
        self._connection = None

    def connection(self):
        # return the current database connection or raise an error if not connected
        if not self._connection:
            raise sqlite3.ProgrammingError("No database connection")
        return self._connection

    def open_database(self, event: OpenDatabaseEvent):
        path = event.path()
        # make sure the path exist
        if path is None:
            print("Can't open database")
        try:
            # Connect to the database and enable foreign key constraints
            # execute one SQL statement after it connects
            self._connection = sqlite3.connect(str(path))
            self._connection.execute("PRAGMA foreign_keys=ON;")
            yield DatabaseOpenedEvent(path)
        except sqlite3.Error as e:
            self._connection = None
            yield DatabaseOpenFailedEvent(str(e))

    def close_database(self, event: CloseDatabaseEvent):
        if self._connection:
            self._connection.close()
            self._connection = None
        yield DatabaseClosedEvent()


