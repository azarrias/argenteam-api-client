#!/usr/bin/env python

import requests
import sys

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

def dl_all_tvshow_subs(output):
    for season in output['seasons']:
        for episode in season['episodes']:
            dl_subs(episode['id'])
    options = { "SEARCH": "Buscar por película, serie, actor o director", "EXIT": "[S]alir" }
    print()
    return options, [], None

def dl_subs(episode_id):
    episode = get_details_episode(episode_id)
    for release in episode['releases']:
        if 'subtitles' in release:
            for subs in release['subtitles']:
                if 'uri' in subs:
                    url = subs['uri']
                    r = requests.get(url, stream = True) # download streaming
                    local_filename = "output_files/" + r.url.split("/")[-1]
                    with open(local_filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size = 1024):
	                        if chunk: # filter out keep-alive new chunks
		                        f.write(chunk)

def get_details_episode(id):
    try:
        response = requests.post(EPISODE_URL, data={"id": id})
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
        return dl_all_tvshow_subs(output)
    elif user_input.isdigit() and int(user_input) > 0 and int(user_input) <= len(elements) and "VIEW" in options:
        return view_item_details(user_input, options, elements, output)
    else:
        return get_search_results(user_input, options)

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
    if result.type == 'tvshow':
        output = get_details_tvshow(result.id)
    print(result)
    print(result.summary + "\n")
    options = { "SEARCH": "Buscar por película, serie, actor o director", "EXIT": "[S]alir",
        "SUBS" : "[D]escargar subtítulos" }
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
