#!/usr/bin/env python

import requests
import sys

API_URL = "http://argenteam.net/api/v1/"
SEARCH_URL = API_URL + "search"
TVSHOW_URL = API_URL + "tvshow"
MOVIE_URL = API_URL + "movie"
EPISODE_URL = API_URL + "episode"

class Result(object):
    def __init__(self, title, _type, summary, year=None):
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
        elements.append(Result(r['title'], r['type'], r['summary'], r.get('year')))
    return elements

def promptUser(options):
    for o in options:
        print(options[o])
    user_input = input("> ")
    if user_input == 'S' and "EXIT" in options:
        sys.exit(0)
    return search(user_input)

def search(query):
    try:
        response = requests.post(SEARCH_URL, data={"q": query})
    except requests.exceptions.RequestException:
        print("ERROR! No se ha podido obtener respuesta del servidor")
        print("Revisa los datos de conexión")
        sys.exit(0)
    return response.json()

if __name__ == '__main__':
    print("aRGENTeaM API client (podría requerir el uso de VPN)")
    print("====================================================")
    print()
    options = { "SEARCH": "Buscar por película, serie, actor o director", "EXIT": "[S] para salir" }
    elements = []
    while True:
        output = promptUser(options)
        num_results = output['total']
        print(response_summary(num_results))
        if num_results == 0:
            continue
        elements = response_elements(output)
        for i in range(len(elements)):
            print("[" + str(i + 1) + "] - " + str(elements[i]))
        print()
        options = { "SEARCH": "Buscar por película, serie, actor o director", 
            "VIEW": "Número a la izquierda del título para ver el detalle", 
            "EXIT": "[S] para salir" }
