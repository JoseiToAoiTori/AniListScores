# AniList Server Score Tools

Calculates mean anime scores for a large number of people (10+) using their AniList profiles.

Python Scores Script was written by mcady#1738 and JSON Generation Script was written by me. Requires [AniScipts](http://www.brendberg.no/anilist/aniscripts/) for importing the JSON produced by the JS script.

## Requirements

To get things set up, you need:

- NodeJS
- yarn
- Python3 (with pip and venv module)

```bash
$ python3 -m venv env
$ source env/bin/activate
$ pip3 install -r requirements.txt
$ deactivate
$ yarn
```

Running `yarn` isn't necessary if you're not dumping the scores to an AniList account.

This should get your dependencies set up. Note that the commands used may be different on Windows unless you're using WSL.

## How to use

Open `generate_scores.py` and edit the `names`, `minUsers` and `restrictions` fields with all the AniList usernames of people to include, the minimum number of users that must have seen a show to include it and whether to include drops etc.

If you want to create an AniList account with all the scores, make sure you ran `yarn` already and have the AniScripts extension installed. Edit the generated Excel sheet to remove the headers and then save it as a CSV file called `scores.csv`. This will generate a JSON file. After installing AniScripts and creating an AniList account, go into Settings -> Apps and scroll to the bottom to click on `Sign in with the script`. After authorizing, you can go to Settings -> Import Lists where you'll see `Anilist JSON: Import Anime List`. Drop your JSON there, hit the import button and wait until importing finishes.
