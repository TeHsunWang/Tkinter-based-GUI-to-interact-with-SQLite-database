# p2app/engine/main.py
#
# ICS 33 Spring 2024
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.


from p2app.events import (
    OpenDatabaseEvent, CloseDatabaseEvent, ErrorEvent,
    StartContinentSearchEvent, LoadContinentEvent, SaveNewContinentEvent,
    SaveContinentEvent, StartCountrySearchEvent, LoadCountryEvent,
    SaveNewCountryEvent, SaveCountryEvent, StartRegionSearchEvent,
    LoadRegionEvent, SaveNewRegionEvent, SaveRegionEvent
)
from p2app.engine.database_handler import Database_Handler
from p2app.engine.continent_handler import ContinentHandler
from p2app.engine.regions_handler import regions_handler
from p2app.engine.countries_handler import CountriesHandler
class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self._database_handler = Database_Handler()
        self._continent_handler = ContinentHandler(self._database_handler)
        self._countries_handler = CountriesHandler(self._database_handler)
        self._regions_handler = regions_handler(self._database_handler)

    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        # This is a way to write a generator function that always yields zero values.
        # You'll want to remove this and replace it with your own code, once you start
        # writing your engine, but this at least allows the program to run.
        try:
            if isinstance(event, OpenDatabaseEvent):
                yield from self._database_handler.open_database(event)
            elif isinstance(event, CloseDatabaseEvent):
                yield from self._database_handler.close_database(event)

            elif isinstance(event, StartContinentSearchEvent):
                yield from self._continent_handler.search_continents(event)
            elif isinstance(event, LoadContinentEvent):
                yield from self._continent_handler.load_continent(event)
            elif isinstance(event, SaveNewContinentEvent):
                yield from self._continent_handler.save_new_continent(event)
            elif isinstance(event, SaveContinentEvent):
                yield from self._continent_handler.save_existing_continent(event)

            elif isinstance(event, StartCountrySearchEvent):
                yield from self._countries_handler.search_countries(event)
            elif isinstance(event, LoadCountryEvent):
                yield from self._countries_handler.load_countries(event)
            elif isinstance(event, SaveNewCountryEvent):
                yield from self._countries_handler.save_new_country(event)
            elif isinstance(event, SaveCountryEvent):
                yield from self._countries_handler.save_existing_country(event)

            elif isinstance(event, StartRegionSearchEvent):
                yield from self._regions_handler.search_region(event)
            elif isinstance(event, LoadRegionEvent):
                yield from self._regions_handler.load_region(event)
            elif isinstance(event, SaveNewRegionEvent):
                yield from self._regions_handler.save_new_region(event)
            elif isinstance(event, SaveRegionEvent):
                yield from self._regions_handler.save_existing_region(event)

            else:
                yield ErrorEvent("Unknown event type")
        except Exception as e:
            yield ErrorEvent(str(e))
