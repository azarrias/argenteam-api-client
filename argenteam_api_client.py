#!/usr/bin/env python

import requests
import sys

API_URL = "http://argenteam.net/api/v1/"
SEARCH_URL = API_URL + "search"
TVSHOW_URL = API_URL + "tvshow"
MOVIE_URL = API_URL + "movie"
EPISODE_URL = API_URL + "episode"

def response_summary(num_results):
    summary = "Found " + str(num_results) + " element"
    if num_results != 1:
        summary += "s"
    summary += "."
    if num_results == 0:
        summary += "\n"
    return summary

def response_elements(response):
    elements = ""
    for r in response['results']:
        elements += "- " + r['title']
        if 'year' in r:
            elements += " (" + str(r['year']) + ")"
        if r['type'] == 'tvshow':
            elements += " (Serie TV)"
        elif r['type'] == 'movie':
            elements += " (Película)"
        elif r['type'] == 'episode':
            elements += " (Episodio)"
        elements += "\n"
    return elements

def promptUser():
    print("Buscar por película, serie, actor o director:")
    print("[S] para salir")
    user_input = input("> ")
    if user_input == 'S':
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
    while True:
        output = promptUser()
        num_results = output['total']
        print(response_summary(num_results))
        if num_results == 0:
            continue
        print(response_elements(output))
    