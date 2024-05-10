# This module is used for managing regions_event
import sqlite3
from p2app.events.regions import (
    StartRegionSearchEvent, RegionSearchResultEvent, LoadRegionEvent,
    RegionLoadedEvent, SaveNewRegionEvent, SaveRegionEvent,
    RegionSavedEvent, SaveRegionFailedEvent, Region
)
from p2app.events.app import ErrorEvent
from p2app.engine.database_handler import Database_Handler
class regions_handler:
    def __init__(self, database_handler: Database_Handler):
        self._database = database_handler

    def search_region(self, event: StartRegionSearchEvent):
        query = "SELECT region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region WHERE"
        params = []

        if event.region_code():
            query += " region_code = ?"
            params.append(event.region_code())
        if event.local_code():
            query += " AND local_code = ?"
            params.append(event.local_code())
        if event.name():
            query += " AND name = ?"
            params.append(event.name())
        try:
            cursor = self._database.connection().execute(query, params)
            for row in cursor:
                region = Region(
                    region_id = row[0],
                    region_code = row[1],
                    local_code = row[2],
                    name = row[3],
                    continent_id = row[4],
                    country_id = row[5],
                    wikipedia_link= row[6],
                    keywords = row[7]
                    )
                yield RegionSearchResultEvent(region)
        except Exception as e:
            yield ErrorEvent(str(e))

    def load_region(self, event: LoadRegionEvent):
        query = "SELECT region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region WHERE region_id = ?"
        # Each call to fetchone on a cursor returns one row of our
        # result, expressed as a tuple whose values correspond to the
        # columns we've asked for.  We've selected one column called
        # name, so we're seeing one-element tuples returned to us.
        try:
            cursor = self._database.connection().execute(query, (event.region_id(),))
            result = cursor.fetchone() # return a row expressed as a tuple
            if result:
                region = Region(
                    region_id = result[0],
                    region_code = result[1],
                    local_code = result[2],
                    name= result[3],
                    continent_id = result[4],
                    country_id = result[5],
                    wikipedia_link= result[6],
                    keywords = result[7]
                )
                yield RegionLoadedEvent(region)
            else:
                yield ErrorEvent(f"Region with ID {event.region_id()} not found")
        except Exception as e:
            yield ErrorEvent(str(e))

    def save_new_region(self, event: SaveNewRegionEvent):
        query = "INSERT INTO region (region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords) VALUES (?, ?, ?, ?, ?, ?, ?)"
        try:
            cursor = self._database.connection().execute(
                query,
                (
                    event.region().region_code,
                    event.region().local_code,
                    event.region().name,
                    event.region().continent_id,
                    event.region().country_id,
                    event.region().wikipedia_link,
                    event.region().keywords
                )
            )
            self._database.connection().commit()
            region = Region(
                region_id=cursor.lastrowid,
                region_code=event.region().region_code,
                local_code=event.region().local_code,
                name=event.region().name,
                continent_id=event.region().continent_id,
                country_id=event.region().country_id,
                wikipedia_link=event.region().wikipedia_link,
                keywords=event.region().keywords
            )
            yield RegionSavedEvent(region)
        except Exception as e:
            yield ErrorEvent(str(e))

    def save_existing_region(self, event: SaveRegionEvent):
        query = "UPDATE region SET region_code = ?, local_code = ?, name = ?, continent_id = ?, country_id = ?, wikipedia_link = ?, keywords = ? WHERE region_id = ?"
        try:
            self._database.connection().execute(
                query, (
                    event.region().region_code,
                    event.region().local_code,
                    event.region().name,
                    event.region().continent_id,
                    event.region().country_id,
                    event.region().wikipedia_link,
                    event.region().keywords,
                    event.region().region_id
                )
            )
            self._database.connection().commit()
            yield RegionSavedEvent(event.region())
        except Exception as e:
            yield SaveRegionFailedEvent(str(e))