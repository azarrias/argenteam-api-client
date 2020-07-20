#!/usr/bin/env python

import requests
import sys
from zipfile import ZipFile
from os import remove

API_URL = "http://argenteam.net/api/v1/"
SEARCH_URL = API_URL + "search"
TVSHOW_URL = API_URL + "tvshow"
MOVIE_URL = API_URL + "movie"
EPISODE_URL = API_URL + "episode"

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

def dl_all_tvshow_subs(show_id):
    tvshow = get_details_tvshow(show_id)
    for season in tvshow['seasons']:
        for episode in season['episodes']:
            options, elements, output = dl_episode_subs(episode['id'])
    return options, elements, output

def dl_episode_subs(episode_id):
    episode = get_details_episode(episode_id)
    return dl_item_subs(episode)

def dl_item_subs(item):
    counter = 0
    options = { "SEARCH": "Buscar por película, serie, actor o director", "EXIT": "[S]alir" }
    for release in item['releases']:
        if 'subtitles' in release:
            for subs in release['subtitles']:
                if 'uri' in subs:
                    counter += 1
                    url = subs['uri']
                    r = requests.get(url, stream = True) # download streaming
                    filename = r.url.split("/")[-1]
                    print("Info: descargando y extrayendo subtítulo de '" + filename + "'")
                    path = "output_files/" + filename
                    with open(path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size = 1024):
	                        if chunk: # filter out keep-alive new chunks
		                        f.write(chunk)
                    with ZipFile(path, 'r') as zipfile:
                        zipfile.extractall("output_files")
                    remove(path)
    if counter == 0:
        print("Info: no se encontraron subtítulos para el item '" + item['title'] + "'")
    return options, [], None

def dl_movie_subs(movie_id):
    movie = get_details_movie(movie_id)
    return dl_item_subs(movie)

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
        options = { "SEARCH": "Buscar por película, serie, actor o director", "EXIT": "[S]alir",
            "VIEW" : "Número a la izquierda del título para ver el detalle" }
    return options, elements, output

def prompt_user(options):
    for o in options:
        print("* " + options[o])
    user_input = input("> ")
    return user_input

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
    if user_input == 'S' and "EXIT" in options:
        sys.exit(0)
    elif user_input == 'D' and "SUBS" in options and output:
        if output["type"] == "tvshow":
            options, elements, output = dl_all_tvshow_subs(output["id"])
        elif output["type"] == "movie":
            options, elements, output = dl_movie_subs(output["id"])
        elif output["type"] == "episode":
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
    options = { "SEARCH": "Buscar por película, serie, actor o director", "EXIT": "[S]alir",
        "SUBS" : "[D]escargar subtítulos" }
    output = output['results'][int(user_input) - 1]
    return options, elements, output

if __name__ == '__main__':
    print("aRGENTeaM API client (podría requerir el uso de VPN)")
    print("====================================================")
    print()
    elements = []
    output = None
    options = { "SEARCH": "Buscar por película, serie, actor o director", "EXIT": "[S]alir" }
    while True:
        user_input = prompt_user(options)
        options, elements, output = run_option(user_input, options, elements, output)
