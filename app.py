import tkinter as tk
from tkinter import ttk
import customtkinter
import title
import user
from tkinter import *
from PIL import ImageTk, Image, UnidentifiedImageError
import requests as rq
from io import BytesIO


class MyApp(tk.Tk):

    def __init__(self):
        super().__init__()

        # Declare use as none until logged in
        self.currentUser = None
        # Declaring Title that will be displayed on a Title page as none until it is determined

        # Set the title of the window
        self.title('Streaming Recommendations')

        # Set the screen resolution to 1080p (1920x1080)
        self.geometry('1920x1080')

        style = ttk.Style()
        style.theme_use('clam')

        # Create the screens for the application
        self.pages = {
            'login': LoginScreen(self),
        }

        # Start with the login screen
        self.show_screen('login')

    def create_home_screen(self):
        # Create the home screen and add it to the pages dictionary
        self.pages['home'] = HomeScreen(self)

    def create_title_screen(self, given_title):
        # Create the home screen and add it to the pages dictionary
        self.pages['title'] = TitleScreen(self, given_title)

    def create_watchlist_screen(self):
        self.pages['list'] = WatchHistory(self)

    def create_search_results_screen(self, results):
        self.pages['results'] = SearchResults(self, results)

    def show_screen(self, screen_name):
        # Hide all screens
        for screen in self.pages.values():
            screen.hide()

        # Show the selected screen
        self.pages[screen_name].show()

    def set_user(self, loginUser):
        self.currentUser = loginUser

    def get_user(self):
        return self.currentUser


class LoginScreen:
    def __init__(self, app):
        self.app = app
        self.login_frame = ttk.Frame(app, width=960, height=540)

        # Create the username and password labels and entry fields
        self.username_label = ttk.Label(self.login_frame, text='Username:')
        self.username_label.grid(row=0, column=0)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)

        self.password_label = ttk.Label(self.login_frame, text='Password:')
        self.password_label.grid(row=1, column=0)
        self.password_entry = ttk.Entry(self.login_frame, show='*')
        self.password_entry.grid(row=1, column=1)

        # Create the login and cancel buttons
        self.login_button = ttk.Button(self.login_frame, text='Login',
                                       command=self.login)
        self.login_button.grid(row=2, column=0)
        self.cancel_button = ttk.Button(self.login_frame, text='Cancel',
                                        command=self.cancel)
        self.cancel_button.grid(row=2, column=1)

    def show(self):
        self.login_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    def hide(self):
        self.login_frame.place_forget()

    def login(self):
        # Get the username and password from the entry fields
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Verify the username and password
        main_user = user.User(username, password)
        if not main_user.login_status:
            self.username_entry.delete(0, END)
            self.password_entry.delete(0, END)
        else:
            self.app.set_user(main_user)
            self.app.create_home_screen()
            self.app.show_screen('home')

    def cancel(self):
        # Clear the entry fields and close the login window
        self.username_entry.delete(0, END)
        self.password_entry.delete(0, END)
        self.app.destroy()


class TitleScreen:
    def __init__(self, app, given_title):
        self.displayed_title = given_title
        self.app = app
        self.title_bar = TitleBar(app)
        self.title_frame = ttk.Frame(app, width=1920, height=1080)
        self.poster_canvas = Canvas(self.title_frame, width=1920, height=1080, )
        self.poster_canvas.grid()
        self.poster_frame = ttk.Frame(self.poster_canvas)
        self.poster_frame.grid()
        title_label = ttk.Label(self.poster_frame, text=self.displayed_title.getName())
        title_label.pack()
        self.left_button_2 = ttk.Button(self.title_frame, text="Watchlist", command=self.add_to_watchlist)
        self.left_button_2.grid(row=1, column=1)

    def add_to_watchlist(self):
        user = self.app.get_user()
        print('you were here')
        api_id = self.displayed_title.get_api_id()
        name = self.displayed_title.getName()
        print(name)

        user.append_watchlist(api_id, name)

    def show(self):
        self.title_bar.show()
        self.title_frame.pack(side=LEFT)

    def hide(self):
        # Hide the title bar and frame
        self.title_bar.hide()
        self.title_frame.pack_forget()

        # Hide the poster canvas and frame
        self.poster_canvas.grid_forget()
        self.poster_frame.grid_forget()


class HomeScreen:
    def __init__(self, app):
        self.on_drag_with_row = None
        self.show_title_obj = None
        self.app = app
        self.title_bar = TitleBar(app)
        self.current_frame = None
        self.trending_list_tv = []
        self.trending_poster_tv = []
        self.trending_list_movie = []
        self.trending_poster_movie = []
        self.start_y = None
        self.start_x = None
        self.end_pos = [0, 0, 0, 0, 0]
        self.home_frame = ttk.Frame(app, width=1920, height=1080)
        # Create a canvas for the rows of movie posters
        self.poster_canvas = Canvas(self.home_frame, width=1920, height=1080, )
        self.poster_canvas.pack()

        # Create a frame for the movie posters
        self.poster_frame = ttk.Frame(self.poster_canvas)
        self.poster_frame2 = ttk.Frame(self.poster_canvas)
        self.poster_frame.place(x=0, y=50)
        self.poster_frame2.place(x=0, y=400)
        self.poster_frame_list = []
        self.poster_frame_list.append(self.poster_frame)
        self.poster_frame_list.append(self.poster_frame2)
        self.getTrendingTitlesTV()
        self.getTrendingTitlesMovie()
        self.create_row_of_trending_tv()
        self.create_row_of_trending_movies()

    def create_row_of_trending_tv(self):
        j = 0
        for list_title in self.trending_list_tv:
            self.show_title_obj = lambda title_obj=list_title: self.show_title(title_obj)
            poster = ttk.Button(self.poster_frame_list[0], image=self.trending_poster_tv[j],
                                command=self.show_title_obj)
            poster.grid(row=0, column=j)
            title_label = ttk.Label(self.poster_frame_list[0], text=list_title.getName())
            title_label.grid(row=1, column=j)
            self.end_pos[0] += self.trending_poster_tv[j].width()
            self.on_drag_with_row = lambda event, row=0: self.on_drag(event, row)
            poster.bind('<Button-1>', self.on_drag_start)
            poster.bind('<B1-Motion>', self.on_drag_with_row)
            # Bind the left mouse button and drag events to a custom function
            j += 1

    def create_row_of_trending_movies(self):
        j = 0
        for list_title in self.trending_list_movie:
            poster = ttk.Button(self.poster_frame_list[1], image=self.trending_poster_movie[j], command=self.show_title)
            poster.grid(row=0, column=j)
            title_label = ttk.Label(self.poster_frame_list[1], text=list_title.getName())
            title_label.grid(row=1, column=j)
            self.end_pos[1] += self.trending_poster_movie[j].width()
            self.on_drag_with_row = lambda event, row=1: self.on_drag(event, row)
            poster.bind('<Button-1>', self.on_drag_start)
            poster.bind('<B1-Motion>', self.on_drag_with_row)
            # Bind the left mouse button and drag events to a custom function
            j += 1

    def show(self):
        self.title_bar.show()
        self.home_frame.pack(side=LEFT)

    def hide(self):
        self.title_bar.hide()
        self.home_frame.pack_forget()

    # Define the custom function for handling mouse events
    def on_drag_start(self, event):
        print('on drag start')
        # Save the starting position of the drag event
        self.start_x = event.x

    def on_drag(self, event, row):
        print('on drag')
        # Calculate the distance moved in x and y directions
        delta_x = event.x - self.start_x
        end_of_frame = -self.end_pos[row]

        # Update the position of the poster frame
        if row == 0:
            if self.poster_frame.winfo_x() + delta_x > 0:
                self.poster_frame.place(x=0)
            elif self.poster_frame.winfo_x() + delta_x < end_of_frame:
                self.poster_frame.place(x=end_of_frame)
            else:
                self.poster_frame.place(x=self.poster_frame.winfo_x() + delta_x)
        else:
            if self.poster_frame2.winfo_x() + delta_x > 0:
                self.poster_frame2.place(x=0)
            elif self.poster_frame2.winfo_x() + delta_x < end_of_frame:
                self.poster_frame2.place(x=end_of_frame)
            else:
                self.poster_frame2.place(x=self.poster_frame2.winfo_x() + delta_x)
        # Save the current position as the starting position for the next drag event
        self.start_x = event.x

    def show_title(self, given_title):
        # Get the title associated with the selected poster
        self.app.create_title_screen(given_title)
        self.app.show_screen('title')

    def getTrendingTitlesTV(self):
        trending = rq.get(
            'https://api.themoviedb.org/3/trending/tv/week?api_key=ec0c9cf926c79f5c0a1ecf728d746601').json().get(
            'results')

        for result in trending:
            if 'name' in result:
                movie = result['name']
                id = result['id']
                print(movie)
                this_title = title.Title(id, movie)
                self.trending_list_tv.append(this_title)
                poster_pic_url = 'https://image.tmdb.org/t/p/w500{}'.format(this_title.poster_image)
                poster_pic = rq.get(poster_pic_url)
                poster_pic = Image.open(BytesIO(poster_pic.content))
                poster_pic = ImageTk.PhotoImage(poster_pic.resize((160, 240)))
                self.trending_poster_tv.append(poster_pic)
            if 'title' in result:
                movie = result['title']
                id = result['id']
                print(movie)
                this_title = title.Title(id, movie)
                self.trending_list_tv.append(this_title)
                poster_pic_url = 'https://image.tmdb.org/t/p/w500{}'.format(this_title.poster_image)
                poster_pic = rq.get(poster_pic_url)
                poster_pic = Image.open(BytesIO(poster_pic.content))
                poster_pic = ImageTk.PhotoImage(poster_pic.resize((160, 240)))
                self.trending_poster_tv.append(poster_pic)

    def getTrendingTitlesMovie(self):
        trending = rq.get(
            'https://api.themoviedb.org/3/trending/movie/week?api_key=ec0c9cf926c79f5c0a1ecf728d746601').json().get(
            'results')

        for result in trending:
            if 'name' in result:
                movie = result['name']
                id = result['id']
                print(movie)
                this_title = title.Title(id, movie)
                self.trending_list_movie.append(this_title)
                poster_pic_url = 'https://image.tmdb.org/t/p/w500{}'.format(this_title.poster_image)
                poster_pic = rq.get(poster_pic_url)
                poster_pic = Image.open(BytesIO(poster_pic.content))
                poster_pic = ImageTk.PhotoImage(poster_pic.resize((160, 240)))
                self.trending_poster_movie.append(poster_pic)
            if 'title' in result:
                movie = result['title']
                id = result['id']
                print(movie)
                this_title = title.Title(id, movie)
                self.trending_list_movie.append(this_title)
                poster_pic_url = 'https://image.tmdb.org/t/p/w500{}'.format(this_title.poster_image)
                poster_pic = rq.get(poster_pic_url)
                poster_pic = Image.open(BytesIO(poster_pic.content))
                poster_pic = ImageTk.PhotoImage(poster_pic.resize((160, 240)))
                self.trending_poster_movie.append(poster_pic)


class TitleBar:
    def __init__(self, app):
        self.filter = None
        self.app = app
        self.title_frame = ttk.Frame(app, width=1920, height=50)
        self.left_button_1 = ttk.Button(self.title_frame, text="Home", command=self.show_home)
        self.left_button_1.pack(side=LEFT)
        self.left_button_2 = ttk.Button(self.title_frame, text="Watchlist", command=self.show_watchlist)
        self.left_button_2.pack(side=LEFT)
        self.left_button_3 = ttk.Button(self.title_frame, text="User")
        self.left_button_3.pack(side=LEFT)
        self.left_button_4 = ttk.Button(self.title_frame, text="Search", command=self.search)
        self.left_button_4.pack(side=RIGHT)
        self.search_var = StringVar()
        self.search_option_var = StringVar()
        self.search_bar = ttk.Entry(self.title_frame, textvariable=self.search_var)
        self.search_bar.pack(side=RIGHT)
        self.search_menu = ttk.OptionMenu(self.title_frame, self.search_option_var, 'Filter', "Movies", "TV Shows",
                                          'All')
        self.search_menu.pack(side=RIGHT)

    def search(self):
        self.filter = self.search_option_var.get()
        results = rq.get(
            'https://api.themoviedb.org/3/search/multi?api_key=ec0c9cf926c79f5c0a1ecf728d746601&language=en-US&page=1&include_adult=false&query={}'.format(
                self.search_var.get())).json().get('results')
        if self.filter == 'Filter' or self.filter == 'All':
            results = rq.get(
                'https://api.themoviedb.org/3/search/multi?api_key=ec0c9cf926c79f5c0a1ecf728d746601&language=en-US&page=1&include_adult=false&query={}'.format(self.search_var.get())).json().get('results')
        elif self.filter == 'Movie':
            results = rq.get(
                'https://api.themoviedb.org/3/search/movie?api_key=ec0c9cf926c79f5c0a1ecf728d746601&language=en-US&page=1&include_adult=false&query={}'.format(
                    self.search_var.get())).json().get('results')
        elif self.filter == 'TV Shows':
            results = rq.get(
                'https://api.themoviedb.org/3/search/tv?api_key=ec0c9cf926c79f5c0a1ecf728d746601&language=en-US&page=1&include_adult=false&query={}'.format(
                    self.search_var.get())).json().get('results')
        self.app.create_search_results_screen(results)
        self.app.show_screen('results')

    def show_watchlist(self):
        self.app.create_watchlist_screen()
        self.app.show_screen('list')

    def show_home(self):
        self.app.show_screen('home')

    def show(self):
        self.title_frame.pack()

    def hide(self):
        self.title_frame.pack_forget()


class SearchResults:

    def __init__(self, app, results):
        self.results = results
        self.search_posters = []
        self.search_titles = []
        self.on_drag_with_row = None
        self.show_title_obj = None
        self.app = app
        self.user = self.app.get_user()
        self.title_bar = TitleBar(app)
        self.current_frame = None
        self.start_y = None
        self.start_x = None
        self.end_pos = 0
        self.home_frame = ttk.Frame(app, width=1920, height=1080)
        # Create a canvas for the rows of movie posters
        self.poster_canvas = Canvas(self.home_frame, width=1920, height=1080, )
        self.poster_canvas.pack()
        # Create a frame for the movie posters
        self.poster_frame = ttk.Frame(self.poster_canvas)
        self.poster_frame.place(x=0, y=50)
        self.get_title_from_search()
        self.create_row_from_search()

    def show(self):
        self.title_bar.show()
        self.home_frame.pack(side=LEFT)

    def create_row_from_search(self):
        j = 0
        for list_title in self.search_titles:
            self.show_title_obj = lambda title_obj=list_title: self.show_title(title_obj)
            poster = ttk.Button(self.poster_frame, image=self.search_posters[j],
                                command=self.show_title_obj)
            poster.grid(row=0, column=j)
            title_label = ttk.Label(self.poster_frame, text=list_title.getName())
            title_label.grid(row=1, column=j)
            self.end_pos += self.search_posters[j].width()
            poster.bind('<Button-1>', self.on_drag_start)
            poster.bind('<B1-Motion>', self.on_drag)
            # Bind the left mouse button and drag events to a custom function
            j += 1

    def get_title_from_search(self):
        for result in self.results:
            if 'poster_path' in result:
                if 'name' in result:
                    movie = result['name']
                    api_id = result['id']
                    this_title = title.Title(api_id, movie)
                    poster_pic = this_title.poster_image
                    if poster_pic is not None:
                        poster_pic_url = 'https://image.tmdb.org/t/p/w500{}'.format(poster_pic)
                        poster_pic = rq.get(poster_pic_url)
                        try:
                            poster_pic = Image.open(BytesIO(poster_pic.content))
                        except UnidentifiedImageError:
                            break
                        poster_pic = ImageTk.PhotoImage(poster_pic.resize((400, 600)))
                        self.search_posters.append(poster_pic)
                        self.search_titles.append(this_title)
                if 'title' in result:
                    movie = result['title']
                    id = result['id']
                    print(movie)
                    this_title = title.Title(id, movie)
                    poster_pic = this_title.poster_image
                    if poster_pic is not None:
                        poster_pic_url = 'https://image.tmdb.org/t/p/w500{}'.format(poster_pic)
                        poster_pic = rq.get(poster_pic_url)
                        try:
                            poster_pic = Image.open(BytesIO(poster_pic.content))
                        except UnidentifiedImageError:
                            break
                        poster_pic = ImageTk.PhotoImage(poster_pic.resize((400, 600)))
                        self.search_posters.append(poster_pic)
                        self.search_titles.append(this_title)
    def on_drag_start(self, event):
        print('on drag start')
        # Save the starting position of the drag event
        self.start_x = event.x

    def on_drag(self, event):
        print('on drag')
        # Calculate the distance moved in x and y directions
        delta_x = event.x - self.start_x
        end_of_frame = -self.end_pos

        # Update the position of the poster frame

        if self.poster_frame.winfo_x() + delta_x > 0:
            self.poster_frame.place(x=0)
        elif self.poster_frame.winfo_x() + delta_x < end_of_frame:
            self.poster_frame.place(x=end_of_frame)
        else:
            self.poster_frame.place(x=self.poster_frame.winfo_x() + delta_x)

        # Save the current position as the starting position for the next drag event
        self.start_x = event.x

    def hide(self):
        self.title_bar.hide()
        self.home_frame.pack_forget()

    def show_title(self, given_title):
        # Get the title associated with the selected poster
        self.app.create_title_screen(given_title)
        self.app.show_screen('title')


class WatchHistory:
    def __init__(self, app):
        self.watchlist_posters = []
        self.watchlist_titles = []
        self.watchlist = None
        self.on_drag_with_row = None
        self.show_title_obj = None
        self.app = app
        self.user = self.app.get_user()
        self.title_bar = TitleBar(app)
        self.current_frame = None
        self.start_y = None
        self.start_x = None
        self.end_pos = 0
        self.home_frame = ttk.Frame(app, width=1920, height=1080)
        # Create a canvas for the rows of movie posters
        self.poster_canvas = Canvas(self.home_frame, width=1920, height=1080, )
        self.poster_canvas.pack()
        # Create a frame for the movie posters
        self.poster_frame = ttk.Frame(self.poster_canvas)
        self.poster_frame.place(x=0, y=50)
        self.get_title_from_watchlist()
        self.create_row_from_watchlist()

    def show(self):
        self.title_bar.show()
        self.home_frame.pack(side=LEFT)

    def create_row_from_watchlist(self):
        j = 0
        for list_title in self.watchlist_titles:
            self.show_title_obj = lambda title_obj=list_title: self.show_title(title_obj)
            poster = ttk.Button(self.poster_frame, image=self.watchlist_posters[j],
                                command=self.show_title_obj)
            poster.grid(row=0, column=j)
            title_label = ttk.Label(self.poster_frame, text=list_title.getName())
            title_label.grid(row=1, column=j)
            self.end_pos += self.watchlist_posters[j].width()
            poster.bind('<Button-1>', self.on_drag_start)
            poster.bind('<B1-Motion>', self.on_drag)
            # Bind the left mouse button and drag events to a custom function
            j += 1

    def get_title_from_watchlist(self):
        self.watchlist = self.user.get_watchlist()
        for titles in self.watchlist:
            api_id = titles[0]
            movie = titles[1]
            this_title = title.Title(api_id, movie)
            poster_pic_url = 'https://image.tmdb.org/t/p/w500{}'.format(this_title.poster_image)
            poster_pic = rq.get(poster_pic_url)
            poster_pic = Image.open(BytesIO(poster_pic.content))
            poster_pic = ImageTk.PhotoImage(poster_pic.resize((400, 600)))
            self.watchlist_posters.append(poster_pic)
            self.watchlist_titles.append(this_title)

    def on_drag_start(self, event):
        print('on drag start')
        # Save the starting position of the drag event
        self.start_x = event.x

    def on_drag(self, event):
        print('on drag')
        # Calculate the distance moved in x and y directions
        delta_x = event.x - self.start_x
        end_of_frame = -self.end_pos

        # Update the position of the poster frame

        if self.poster_frame.winfo_x() + delta_x > 0:
            self.poster_frame.place(x=0)
        elif self.poster_frame.winfo_x() + delta_x < end_of_frame:
            self.poster_frame.place(x=end_of_frame)
        else:
            self.poster_frame.place(x=self.poster_frame.winfo_x() + delta_x)

        # Save the current position as the starting position for the next drag event
        self.start_x = event.x

    def hide(self):
        self.title_bar.hide()
        self.home_frame.pack_forget()

    def show_title(self, given_title):
        # Get the title associated with the selected poster
        self.app.create_title_screen(given_title)
        self.app.show_screen('title')



theapp = MyApp()
theapp.mainloop()
