# Internal modules
from input_parser.ParamsParser import ParamsParser 

def main():
    params = ParamsParser()
    

    import requests
    import json
    r = requests.get('https://nominatim.openstreetmap.org/search.php?q=germany&polygon_geojson=1&format=jsonv2')
    parsed = json.loads(r.content.decode('utf-8'))
    with open('germany.json', 'w') as file:
        print(type(str(parsed[0])))
        file.write(str(parsed))



if __name__ == '__main__':
    main()