from typing import Tuple

from flask_restful import Api
from flask_restful import Resource


class Uri():
    def __init__(self):
        # Initialize a dictionary to store URL-to-resource mappings
        # and a prefix string for route grouping
        self._uri = {}
        self._prefix = ""

    def set_prefix(self, prefix: str):
        """Set a common prefix for all registered routes."""
        self._prefix = prefix
    
    def add(self, resource: Resource, *urls: Tuple[str, ...]):
        """
        Add one or more URL routes associated with a specific resource.

        Args:
            resource (Resource): A class inheriting from Flask-RESTful's Resource.
            *urls (Tuple[str, ...]): One or more URL paths to associate with the resource.
        """
        for url in urls:
            self._uri[url] = resource

    def get_uri(self) -> dict:
        """
        Get the current mapping of URLs to their associated resources.

        Returns:
            dict: A dictionary mapping URL paths to resource classes.
        """
        return self._uri
    
    def register(self, api: Api):
        """
        Register all stored routes and their resources to a Flask-RESTful API instance.

        Args:
            api (Api): An instance of Flask-RESTful's Api class.
        """
        for k in self._uri.keys():
            if not self._prefix:
                api.add_resource(self._uri[k], k)
            else:
                full_k = f"{self._prefix}{k}"
                api.add_resource(self._uri[k], full_k)





