# This module is used for managing continent_events
import sqlite3
from p2app.events.continents import(
Continent, StartContinentSearchEvent, ContinentSearchResultEvent, LoadContinentEvent,
ContinentLoadedEvent,SaveContinentEvent,SaveNewContinentEvent, ContinentSavedEvent,
SaveContinentFailedEvent
)
from p2app.events.app import ErrorEvent
from p2app.engine.database_handler import Database_Handler
class ContinentHandler:
    # initialize the continent handler with a database connection
    def __init__(self, database_handler: Database_Handler):
        self._database_handler = database_handler

    def search_continents(self, event: StartContinentSearchEvent):
        query = "SELECT continent_id, continent_code, name FROM continent WHERE"
        params = []

        if event.continent_code():
            query += " continent_code = ?"
            params.append(event.continent_code())
        if event.name():
            query += " AND name = ?"
            params.append(event.name())
        try:
            cursor = self._database_handler.connection().execute(query, params)
            for row in cursor:
                continent = Continent(
                    continent_id = row[0],
                    continent_code = row[1],
                    name = row[2]
                )
                yield ContinentSearchResultEvent(continent)
        except Exception as e:
            yield ErrorEvent(str(e))

    def load_continent(self, event: LoadContinentEvent):
        # load continent given its continent_id
        query = "SELECT continent_id, continent_code, name FROM continent WHERE continent_id = ?"
        try:
            cursor = self._database_handler.connection().execute(query, (event.continent_id(),))
            result = cursor.fetchone()
            if result:
                continent = Continent(
                    continent_id=result[0],
                    continent_code=result[1],
                    name=result[2]
                )
                yield ContinentLoadedEvent(continent)
            else:
                yield ErrorEvent(f"Continent with ID {event.continent_id()} not found")
        except Exception as e:
            yield SaveContinentFailedEvent(str(e))

    def save_new_continent(self, event: SaveNewContinentEvent):
        query = "INSERT INTO Continent (continent_code, name) VALUES (?,?)"
        try:
            cursor = self._database_handler.connection().execute(
                query, (event.continent().continent_code,event.continent().name)
            )
            self._database_handler.connection().commit()
            continent = Continent(
                continent_id = cursor.lastrowid,
                continent_code = event.continent().continent_code,
                name = event.continent().name
            )
            yield ContinentSavedEvent(continent)
        except Exception as e:
            yield SaveContinentFailedEvent(str(e))

    def save_existing_continent(self, event: SaveContinentEvent):
        query = "UPDATE continent SET continent_code = ?, name = ? WHERE continent_id = ?"
        try:
            self._database_handler.connection().execute(
                query,
                (event.continent().continent_code,
                 event.continent().name,
                 event.continent().continent_id
                 )
            )
            self._database_handler.connection().commit()
            yield ContinentSavedEvent(event.continent())
        except Exception as e:
            yield SaveContinentFailedEvent(str(e))

