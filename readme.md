# Re-fetch missing account images

On my Mastodon instance, doing `tootctl accounts refresh --all` always crashes halfway through, so I created this script to load the home timeline, check for missing account avatars, and then create the bash script necessary to fetch those images. You can then run that script on your instance.

This whole thing was written in a few hours late at night, so it's probably not perfect. But hopefully it's useful.

## How to get going

### virtual environment

Best way to get going is to create a Python virtual environment for this script with `python3 venv .  --upgrade-deps`.

You can then run that environment with `source bin/activate` and install all requirements with `pip install -r requirements.txt`.

### Credentials and settings

You need a `settings.json` and `credentials.json` file. There are examples for both included.

* `settings.json` contains the baseurl of your instance, and the prefix that should be added to each `tootctl account refresh` command. In my case this is the `docker exec` to run the command inside my docker container. But it could be anything, or an empty string.

* `credentials.json` contains the credentials with which you want to log in to your Mastodon instance to access the home timeline. This can be any user, but the missing avatars detected will only be accounts visible to that user somehow.

### Running the script

Simply going into the Python venv (`source bin/activate` ) and then running the script with `python scrape.py` should do the trick. Two extra `.secret` files will be created, these contain sensitive information so shouldn't be shared or made public.