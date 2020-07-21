#!/usr/bin/env python

import requests
import sys
from zipfile import ZipFile
import os

# use paths relative to this script, regardless of the path from which it is invoked
this_path = os.path.dirname(os.path.realpath(__file__))

API_URL = "http://argenteam.net/api/v1/"
SEARCH_URL = API_URL + "search"
TVSHOW_URL = API_URL + "tvshow"
MOVIE_URL = API_URL + "movie"
EPISODE_URL = API_URL + "episode"
OUTPUT_PATH = os.path.join(this_path, "output_files/")

class Result(object):
    def __init__(self, _id, title, _type, summary, year=None):
        self.id = _id
        self.title = title
        self.type = _type
        self.summary = summary
        self.year = year

    def __str__(self):
        s = self.title
        if self.year:
            s += " (" + str(self.year) + ")"
        if self.type == 'tvshow':
            s += " (Serie TV)"
        elif self.type == 'movie':
            s += " (Película)"
        elif self.type == 'episode':
            s += " (Episodio)"
        return s

def append_line_to_file(path, line):
    # Open the file in append & read mode ('a+')
    with open(path, "a+") as f:
        # Move read cursor to the start of file.
        f.seek(0)
        # If file is not empty then append '\n'
        data = f.read(100)
        if len(data) > 0 :
            f.write("\n")
        # Append text at the end of file
        f.write(line)

def dl_all_tvshow_subs(show_id):
    tvshow = get_details_tvshow(show_id)
    for season in tvshow['seasons']:
        for episode in season['episodes']:
            options, elements, output = dl_episode_subs(episode['id'])
    return options, elements, output

def dl_all_tvshow_torrents(show_id):
    tvshow = get_details_tvshow(show_id)
    for season in tvshow['seasons']:
        for episode in season['episodes']:
            options, elements, output = dl_episode_torrents(episode['id'], tvshow)
    return options, elements, output

def dl_episode_subs(episode_id):
    episode = get_details_episode(episode_id)
    return dl_item_subs(episode)

def dl_episode_torrents(episode_id, tvshow = None):
    episode = get_details_episode(episode_id)
    return dl_item_torrents(episode, tvshow)

def dl_item_subs(item):
    counter = 0
    options = { "SEARCH": "Buscar por película, serie, actor o director", "EXIT": "[C]errar" }
    for release in item['releases']:
        if 'subtitles' in release:
            for subs in release['subtitles']:
                if 'uri' in subs:
                    counter += 1
                    url = subs['uri']
                    try:
                        r = requests.get(url, stream = True) # download streaming
                    except requests.exceptions.RequestException:
                        print("Error: no se pudo descargar el fichero de " + url)
                        continue
                    filename = r.url.split("/")[-1]
                    print("Info: descargando y extrayendo subtítulo de '" + filename + "'")
                    path = OUTPUT_PATH + "/" + filename
                    with open(path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size = 1024):
	                        if chunk: # filter out keep-alive new chunks
		                        f.write(chunk)
                    with ZipFile(path, 'r') as zipfile:
                        zipfile.extractall(OUTPUT_PATH)
                    os.remove(path)
    if counter == 0:
        print("Info: no se encontraron subtítulos para el item '" + item['title'] + "'")
    return options, [], None

def dl_item_torrents(item, tvshow = None):
    counter = 0
    options = { "SEARCH": "Buscar por película, serie, actor o director", "EXIT": "[C]errar" }
    for release in item['releases']:
        path_magnets, path_elinks = get_release_filenames(release, item, tvshow)
        #remove_existing_files([path_magnets, path_elinks])
        if 'torrents' in release:
            for torrent in release['torrents']:
                if 'uri' in torrent:
                    handle_torrent_types(torrent, 'uri', path_magnets)
                    counter += 1
                if 'alt' in torrent:
                    handle_torrent_types(torrent, 'alt', path_magnets)
                    counter += 1
        if 'elinks' in release:
            for elink in release['elinks']:
                if 'uri' in elink:
                    counter += 1
                    append_line_to_file(path_elinks, elink['uri'])
                    print("Info: añadiendo elink a '" + path_elinks + "'")
    if counter == 0:
        print("Info: no se encontraron torrents o magnets para el item '" + item['title'] + "'")
    return options, [], None

def dl_movie_subs(movie_id):
    movie = get_details_movie(movie_id)
    return dl_item_subs(movie)

def dl_movie_torrents(movie_id):
    movie = get_details_movie(movie_id)
    return dl_item_torrents(movie)

def get_details_episode(id):
    try:
        response = requests.post(EPISODE_URL, data={"id": id})
    except requests.exceptions.RequestException:
        print("ERROR! No se ha podido obtener respuesta del servidor")
        print("Revisa los datos de conexión")
        sys.exit(0)
    return response.json()

def get_details_movie(id):
    try:
        response = requests.post(MOVIE_URL, data={"id": id})
    except requests.exceptions.RequestException:
        print("ERROR! No se ha podido obtener respuesta del servidor")
        print("Revisa los datos de conexión")
        sys.exit(0)
    return response.json()

def get_details_tvshow(id):
    try:
        response = requests.post(TVSHOW_URL, data={"id": id})
    except requests.exceptions.RequestException:
        print("ERROR! No se ha podido obtener respuesta del servidor")
        print("Revisa los datos de conexión")
        sys.exit(0)
    return response.json()

def get_release_filenames(release, item, tvshow):
    if tvshow:
        filename = tvshow['title']
    else:
        filename = item['title']
    if 'tags' in release and len(release['tags']) > 0:
        filename += ' ' + release['tags']
    if 'source' in release and len(release['source']) > 0:
        filename += ' ' + release['source']
    if 'codec' in release and len(release['codec']) > 0:
        filename += ' ' + release['codec']
    if 'team' in release and len(release['team']) > 0:
        filename += ' ' + release['team']
    filename = filename.translate ({ord(c): "_" for c in r"!@#$%^&*[]{};:,./<>?\|`~-=_+"})
    magnets_path = OUTPUT_PATH + filename + ' (magnets).txt'
    elinks_path = OUTPUT_PATH + filename + ' (elinks).txt'
    return magnets_path, elinks_path

def get_search_results(user_input, options):
    elements = []
    output = search(user_input)
    num_results = output['total']
    print(response_summary(num_results))
    if num_results > 0:
        elements = response_elements(output)
        for i in range(len(elements)):
            print("[" + str(i + 1) + "] - " + str(elements[i]))
        print()
        options = { "SEARCH": "Buscar por película, serie, actor o director", "EXIT": "[C]errar",
            "VIEW" : "Número a la izquierda del título para ver el detalle" }
    return options, elements, output

def handle_torrent_types(torrent, key, path_magnets):
    if torrent[key].startswith('magnet'):
        append_line_to_file(path_magnets, torrent[key])
        print("Info: añadiendo magnet a '" + path_magnets + "'")
    else:
        url = torrent[key]
        try:
            r = requests.get(url, stream = True) # download streaming
        except requests.exceptions.RequestException:
            print("Error: no se pudo descargar el fichero de " + url)
            return
        filename = r.url.split("/")[-1]
        print("Info: descargando torrent '" + filename + "'")
        path = OUTPUT_PATH + "/" + filename
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size = 1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

def prompt_user(options):
    for o in options:
        print("* " + options[o])
    user_input = input("> ")
    return user_input

def remove_existing_files(files_list):
    for file in files_list:
        if os.path.exists(file):
            os.remove(file)

def response_elements(response):
    elements = []
    for r in response['results']:
        elements.append(Result(r['id'], r['title'], r['type'], r['summary'], r.get('year')))
    return elements

def response_summary(num_results):
    summary = str(num_results) + " resultado"
    if num_results != 1:
        summary += "s"
    summary += "."
    if num_results == 0:
        summary += "\n"
    return summary

def run_option(user_input, options, elements, output = None):
    if user_input == 'C' and "EXIT" in options:
        sys.exit(0)
    elif user_input == 'S' and "SUBS" in options and output:
        if output["type"] == "tvshow":
            options, elements, output = dl_all_tvshow_subs(output["id"])
        elif output["type"] == "movie":
            options, elements, output = dl_movie_subs(output["id"])
        elif output["type"] == "episode":
            options, elements, output = dl_episode_subs(output["id"])
        print()
        return options, elements, output
    elif user_input == 'T' and "TORRENTS" in options and output:
        if output["type"] == "tvshow":
            options, elements, output = dl_all_tvshow_torrents(output["id"])
        elif output["type"] == "movie":
            options, elements, output = dl_movie_torrents(output["id"])
        elif output["type"] == "episode":
            options, elements, output = dl_episode_torrents(output["id"])
        print()
        return options, elements, output
    elif user_input == 'D' and "ALL" in options and output:
        if output["type"] == "tvshow":
            dl_all_tvshow_torrents(output["id"])
            options, elements, output = dl_all_tvshow_subs(output["id"])
        elif output["type"] == "movie":
            dl_movie_torrents(output["id"])
            options, elements, output = dl_movie_subs(output["id"])
        elif output["type"] == "episode":
            dl_episode_torrents(output["id"])
            options, elements, output = dl_episode_subs(output["id"])
        print()
        return options, elements, output
    elif user_input.isdigit() and int(user_input) > 0 and int(user_input) <= len(elements) and "VIEW" in options:
        return view_item_details(user_input, options, elements, output)
    else:
        options, elements, output = get_search_results(user_input, options)
        if len(elements) == 1:
            options, elements, output = view_item_details(1, options, elements, output)
        return options, elements, output

def search(query):
    try:
        response = requests.post(SEARCH_URL, data={"q": query})
    except requests.exceptions.RequestException:
        print("ERROR! No se ha podido obtener respuesta del servidor")
        print("Revisa los datos de conexión")
        sys.exit(0)
    return response.json()

def view_item_details(user_input, options, elements, output):
    result = elements[int(user_input) - 1]
    print(result)
    print(result.summary + "\n")
    options = { "SEARCH": "Buscar por película, serie, actor o director", "EXIT": "[C]errar",
        "SUBS" : "Descargar [S]ubtítulos", "TORRENTS" : "Descargar [T]orrents, Magnets y eLinks",
        "ALL" : "[D]escargar todo" }
    output = output['results'][int(user_input) - 1]
    return options, elements, output

if __name__ == '__main__':
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    print("aRGENTeaM API client (podría requerir el uso de VPN)")
    print("====================================================")
    print()
    elements = []
    output = None
    options = { "SEARCH": "Buscar por película, serie, actor o director", "EXIT": "[C]errar" }
    while True:
        user_input = prompt_user(options)
        options, elements, output = run_option(user_input, options, elements, output)
