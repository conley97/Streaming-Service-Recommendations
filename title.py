import requests as rq
import sqlite3
import tkinter as tk
from tkinter import ttk
import customtkinter
import title
import user
from tkinter import *
from PIL import ImageTk, Image
from io import BytesIO

class Title:

    def __init__(self, api_id, name):
        # Connect to the database
        con = sqlite3.connect('titleDB.db')
        c = con.cursor()

        self.api_id = api_id
        self.name = name
        self.id = str(self.name) + str(self.api_id)
        # Check if the given title is in the database
        c.execute("SELECT * FROM titles WHERE ID = ?", [self.id], )
        db_id = c.fetchone()

        # If the title is not in the database, retrieve information about it from the API and store it in the database
        if db_id is None:
            self.movie = True
            results = rq.get(
                'https://api.themoviedb.org/3//movie/{}?api_key=ec0c9cf926c79f5c0a1ecf728d746601'.format(
                    api_id)).json()

            # If the movie is not found, try searching for a TV show instead
            if results.get('title') != name:
                results = rq.get(
                    'https://api.themoviedb.org/3//tv/{}?api_key=ec0c9cf926c79f5c0a1ecf728d746601'.format(
                        api_id)).json()
                self.movie = False

            # Initialize the object attributes with the information from the API
            self.api_id = api_id
            self.name = name
            self.poster_image = results.get('poster_path')
            self.description = results.get('overview')
            self.rating = results.get('vote_average')
            self.relations = []

            self.genres_ids = results.get('genres')
            self.genres = []
            if self.genres_ids is not None:
                for genre in self.genres_ids:
                    self.genres.append(genre.get('name'))
            self.streaming_services = []
            self.getStreamingServices()

            print(self.streaming_services)
            # Insert the title into the database
            c.execute(
                "INSERT INTO titles (api_id, name, poster_image, description, rating, ID) VALUES (?, ?, ?, ?, ?, ?)", (
                str(self.api_id), str(self.name), str(self.poster_image), str(self.description), str(self.rating),
                str(self.id)))
            con.commit()

        # If the title is already in the database, retrieve the information from the database
        else:
            c.execute("SELECT * FROM titles WHERE api_id = ? AND name = ?", (self.api_id, self.name))
            db_title = c.fetchone()

            # Initialize the object attributes with the information from the database
            self.api_id = db_title[0]
            self.name = db_title[1]
            self.poster_image = db_title[2]
            self.description = db_title[3]
            self.rating = db_title[4]
            self.relations = db_title[5]
            self.genres = db_title[6]

        # Close the database connection
        con.close()


    def getName(self):
        return self.name


    def get_api_id(self):
        return self.api_id


    def getStreamingServices(self):
        if self.movie:
            streaming_providers = rq.get(
                'https://api.themoviedb.org/3/movie/{}/watch/providers?api_key=ec0c9cf926c79f5c0a1ecf728d746601'.format(
                    self.api_id)).json()
            streaming_providers = streaming_providers.get("results")
            if streaming_providers is not None:
                streaming_providers = streaming_providers.get("US")
                if streaming_providers is not None:
                    streaming_providers = streaming_providers.get('flatrate')
                    if streaming_providers is not None:
                        if 'flatrate' in streaming_providers:
                            streaming_providers = streaming_providers.get('flatrate')
                            if streaming_providers is not None:
                                for providers in streaming_providers:
                                    provider_name = providers['provider_name']
                                    self.streaming_services.append(provider_name)

        else:
            streaming_providers = rq.get(
                'https://api.themoviedb.org/3/tv/{}/watch/providers?api_key=ec0c9cf926c79f5c0a1ecf728d746601'.format(
                    self.api_id)).json()
            streaming_providers = streaming_providers.get("results")
            if streaming_providers is not None:
                streaming_providers = streaming_providers.get("US")
                if streaming_providers is not None:
                    streaming_providers = streaming_providers.get('flatrate')
                    if streaming_providers is not None:
                        if 'flatrate' in streaming_providers:
                            streaming_providers = streaming_providers.get('flatrate')
                            if streaming_providers is not None:
                                for providers in streaming_providers:
                                    provider_name = providers['provider_name']
                                    self.streaming_services.append(provider_name)

