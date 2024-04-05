import requests
import json

with open("krypton_storage/secrets.json", "r") as file:
    google_key = json.load(file)["google"]

def google(query):
    endpoint = 'https://www.googleapis.com/customsearch/v1'

    try:
        response = requests.get(endpoint, params={
            'key': google_key,
            'cx': 'e0e238e9c124b4784',
            'q': query
        })

        if response.json().get('items'):
            return '<br>'.join([
                f"<a href='{item['link']}' target='_blank'>{item['title']}</a><br>{item['snippet']}"
                for item in response.json()['items'][:3]]), '<br><br>'.join([
                f"<a href='{item['link']}' target='_blank'>{item['title']}</a><br>{item['snippet']}"
                for item in response.json()['items'][:3]])
        else:
            return 'No results found for the provided query.', 'No results found for the provided query.'

    except Exception as error:
        print('Error fetching search results:', error)
        return 'An error occurred while fetching the search results.', 'An error occurred while fetching the search results.'
