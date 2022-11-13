import requests
# import urllib
# from urllib.parse import urlparse
# from urllib.parse import urlunparse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from mastodon import Mastodon
from string import Template
import json

credentials = {}
settings = {}

with open('credentials.json', 'r') as f:
    credentials = json.load(f)

with open('settings.json', 'r') as f:
    settings = json.load(f)

def create_app():
    Mastodon.create_app(
        'pythonscraper',
        api_base_url = settings['baseurl'],
        to_file = 'clientcred.secret'
    )

def find_avatar_links(ob):
    out = {}
    try:
        for k,v in ob.items():
            if 'account' == k:
                out[str(v['acct'])] = str(v['avatar'])
            else:
                out = out | find_avatar_links(v)
    except:
        pass
    return out

def get_all_toots():
    try:
        mastodon = Mastodon(
            client_id = 'clientcred.secret',
            api_base_url = settings['baseurl']
        )
    except:
        create_app()
        mastodon = Mastodon(
            client_id = 'clientcred.secret',
            api_base_url = settings['baseurl']
        )

    mastodon.log_in(
        credentials['login'],
        credentials['pass'],
        to_file = 'usercred.secret'
    )

    mastodon = Mastodon(
        access_token = 'usercred.secret',
        api_base_url = settings['baseurl']
    )
    avatar_links = {}
    home_tl = mastodon.timeline_home()
    last_id = 0
    while home_tl:
        for p in home_tl:
            print(p['id'])
            last_id = p['id']
            avatar_links = avatar_links | find_avatar_links(p)
            # print(p['id'])
        home_tl = mastodon.timeline_home(max_id=last_id)
    
    print(avatar_links)

    with open('./output/avatar_links.json','w') as of:
        json.dump(avatar_links,of)
    return avatar_links

def filter_broken_urls(urls):
    userstofetch = []

    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    with requests.Session() as s:
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        for k,v in urls.items():
            print(v)
            r = s.get(v)
            print(r.status_code)
            if r.status_code > 400:
                userstofetch.append(k)

    with open('./output/userstofetch.json','w') as of:
        json.dump(userstofetch,of)
    return userstofetch

def make_batch_script(users):
    commands = []
    for u in users:
        commands.append( settings['bash_prefix'] + 'tootctl accounts refresh ' + u)

    out = ' && '.join(commands)
    with open('./output/fetch_bad_users.sh','w') as of:
        of.write(out)
    return out

# Alle toots en boosts van de home timeline ophalen
urls = get_all_toots()

# De niet werkende urls ophalen
brokens = filter_broken_urls(urls)

# bash script maken om de getroffen users te refreshen
bash = make_batch_script(brokens)

print(bash)