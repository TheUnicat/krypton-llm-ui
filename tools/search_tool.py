import requests
import json

with open("krypton_storage/secrets.json", "r") as file:
    google_key = json.load(file)["google_search"]

def google(args):
    query = args['query']
    endpoint = 'https://www.googleapis.com/customsearch/v1'

    try:
        response = requests.get(endpoint, params={
            'key': google_key,
            'cx': 'e0e238e9c124b4784',
            'q': query
        })

        print(response)

        if response.json().get('items'):
            print("returning google results")
            yield json.dumps({"result": '<br>'.join([
                f"<a href='{item['link']}' target='_blank'>{item['title']}</a><br>{item['snippet']}"
                for item in response.json()['items'][:3]]), "done": True})
        else:
            yield {"result": 'No results found for the provided query.', "done": True}

    except Exception as error:
        print('Error fetching search results:', error)
        return 'An error occurred while fetching the search results.'
