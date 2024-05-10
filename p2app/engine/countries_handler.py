# This module is used for managing contries_events
from p2app.events.countries import (
    StartCountrySearchEvent, CountrySearchResultEvent, LoadCountryEvent,
    CountryLoadedEvent, SaveNewCountryEvent, SaveCountryEvent,
    CountrySavedEvent, SaveCountryFailedEvent, Country
)
from p2app.events.app import ErrorEvent
from p2app.engine.database_handler import Database_Handler

class CountriesHandler:
    def __init__(self, database_handler: Database_Handler):
        self._database_handler = database_handler

    def search_countries(self, event: StartCountrySearchEvent):
        query = "SELECT country_id, country_code, name, continent_id, wikipedia_link, keywords FROM country WHERE "
        paramas = []

        if event.country_code():
            query += "country_code = ?"
            paramas.append(event.country_code())
        if event.name():
            query += "AND name = ?"
            paramas.append(event.name())
        try:
            cursor = self._database_handler.connection().execute(query, paramas)
            for row in cursor:
                country = Country(
                    country_id=row[0],
                    country_code=row[1],
                    name=row[2],
                    continent_id=row[3],
                    wikipedia_link=row[4],
                    keywords=row[5]
                )
                yield CountrySearchResultEvent(country)
        except Exception as e:
            yield ErrorEvent(str(e))

    def load_countries(self, event: LoadCountryEvent):
        query = "SELECT country_id, country_code, name, continent_id, wikipedia_link, keywords FROM country WHERE country_id = ?"
        try:
            cursor = self._database_handler.connection().execute(query, (event.country_id(),))
            result = cursor.fetchone()
            if result:
                country = Country(
                    country_id=result[0],
                    country_code=result[1],
                    name=result[2],
                    continent_id=result[3],
                    wikipedia_link=result[4],
                    keywords=result[5]
                )
                yield CountryLoadedEvent(country)
            else:
                yield ErrorEvent(f"Country {event.country_id()} not found")
        except Exception as e:
            yield ErrorEvent(str(e))

    def save_new_country(self, event: SaveNewCountryEvent):
        query = "INSERT INTO country (country_code, name, continent_id, wikipedia_link, keywords) VALUES (?, ?, ?, ?, ?)"
        try:
            cursor = self._database_handler.connection().execute(
                query, (
                    event.country().country_code,
                    event.country().name,
                    event.country().continent_id,
                    event.country().wikipedia_link,
                    event.country().keywords
                )
            )
            self._database_handler.connection().commit()
            country = Country(
                country_id=cursor.lastrowid,
                country_code = event.country().country_code,
                name = event.country().name,
                continent_id = event.country().continent_id,
                wikipedia_link = event.country().wikipedia_link,
                keywords = event.country().keywords
            )
            yield CountrySavedEvent(country)
        except Exception as e:
            yield ErrorEvent(str(e))
    def save_existing_country(self, event: SaveCountryEvent):
        query = "UPDATE country SET country_code = ?, name = ?, continent_id = ?, wikipedia_link = ?, keywords = ? WHERE country_id = ?"
        try:
            self._database_handler.connection().execute(
                query, (
                    event.country().country_code,
                    event.country().name,
                    event.country().continent_id,
                    event.country().wikipedia_link,
                    event.country().keywords,
                    event.country().country_id
                )
            )
            self._database_handler.connection().commit()
            yield CountrySavedEvent(event.country())
        except Exception as e:
            yield SaveCountryFailedEvent(str(e))