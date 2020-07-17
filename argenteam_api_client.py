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

def response_summary(num_results):
    summary = str(num_results) + " resultado"
    if num_results != 1:
        summary += "s"
    summary += "."
    if num_results == 0:
        summary += "\n"
    return summary

def response_elements(response):
    elements = []
    for r in response['results']:
        elements.append(Result(r['id'], r['title'], r['type'], r['summary'], r.get('year')))
    return elements

def prompt_user(options, elements, output = None):
    for o in options:
        print(options[o])
    user_input = input("> ")
    if user_input == 'S' and "EXIT" in options:
        sys.exit(0)
    elif user_input == 'D' and "SUBS" in options and output:
        for season in output['seasons']:
            for episode in season['episodes']:
                dl_subs(episode['id'])
    elif user_input.isdigit() and int(user_input) > 0 and int(user_input) <= len(elements) and "VIEW" in options:
        result = elements[int(user_input) - 1]
        if result.type == 'tvshow':
            output = search_tvshow(result.id)
        options = { "SEARCH": "Buscar por película, serie, actor o director", 
            "SUBS": "[D]escargar subtítulos", 
            "EXIT": "[S]alir" }
    else:
        output = search(user_input)
        num_results = output['total']
        print(response_summary(num_results))
        if num_results > 0:
            elements = response_elements(output)
            for i in range(len(elements)):
                print("[" + str(i + 1) + "] - " + str(elements[i]))
            print()
            options = { "SEARCH": "Buscar por película, serie, actor o director", 
                "VIEW": "Número a la izquierda del título para ver el detalle", 
                "EXIT": "[S]alir" }
        
    return options, elements, output

def dl_subs(episode_id):
    episode = search_episode(episode_id)
    for release in episode['releases']:
        if 'subtitles' in release:
            for subs in release['subtitles']:
                if 'uri' in subs:
                    url = subs['uri']
                    local_filename = url.split("/")[-1]
                    r = requests.get(url, stream = True) # download streaming
                    with open(local_filename, 'wb') as f:
                        for chunk in r.iter_content(chunk_size = 1024):
	                        if chunk: # filter out keep-alive new chunks
		                        f.write(chunk)

def search(query):
    try:
        response = requests.post(SEARCH_URL, data={"q": query})
    except requests.exceptions.RequestException:
        print("ERROR! No se ha podido obtener respuesta del servidor")
        print("Revisa los datos de conexión")
        sys.exit(0)
    return response.json()

def search_episode(id):
    try:
        response = requests.post(EPISODE_URL, data={"id": id})
    except requests.exceptions.RequestException:
        print("ERROR! No se ha podido obtener respuesta del servidor")
        print("Revisa los datos de conexión")
        sys.exit(0)
    return response.json()    

def search_tvshow(id):
    try:
        response = requests.post(TVSHOW_URL, data={"id": id})
    except requests.exceptions.RequestException:
        print("ERROR! No se ha podido obtener respuesta del servidor")
        print("Revisa los datos de conexión")
        sys.exit(0)
    return response.json()

if __name__ == '__main__':
    print("aRGENTeaM API client (podría requerir el uso de VPN)")
    print("====================================================")
    print()
    options = { "SEARCH": "Buscar por película, serie, actor o director", "EXIT": "[S]alir" }
    elements = []
    output = None
    while True:
        options, elements, output = prompt_user(options, elements, output)
