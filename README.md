# mobisession
A proof of concept for mobile sessions

## Installation and configuration
First of all, it's probably a good idea to use virtualenv and pip install. You will also need sqlite3. Once you have your virtual environment set up, install Flask, e g ```pip install Flask```.

Now, cd into the project directory and start a python shell. Execute the following:
```
>>> import mobisession
>>> mobisession.init_db()
```

Now, run ``` python mobisession.py```

## Usage
Open a browser, go to http://localhost:5000. Open a different browser or a private tab and go to the same address. You'll notice they have different session IDs. Entering text into the text box and clocking the button will associate that data with the current session ID and save it to the database.

Appending a forward slash followed by another session ID will change to that session and load that data.

## What's the point?
This is the first draft for an experiment with sharing sessions between different devices.
