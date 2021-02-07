import http.client
import json
import argparse

# polaczenie z serwerem
def download_remote_text_file(host: str, url: str):
    version_provider_connection = http.client.HTTPSConnection(host)
    version_provider_connection.request('GET', url)
    response_payload = version_provider_connection.getresponse().read()
    
    version_provider_connection.close()
    return response_payload

def download_remote_text_file_from_url(full_url: str):
    from urllib.parse import urlparse
    parsed_url = urlparse(full_url)

    return download_remote_text_file(parsed_url.netloc, parsed_url.path)

def download_version_manifest():
    return download_remote_text_file('launchermeta.mojang.com', '/mc/game/version_manifest.json')

def json_version_manifest():
    return json.loads(download_version_manifest())

def download_detailed_version_manifest(detailed_version_manifest_url):
    return download_remote_text_file_from_url(detailed_version_manifest_url)

def json_detailed_version_manifest(detailed_version_manifest_url):
    return json.loads(download_detailed_version_manifest(detailed_version_manifest_url))

# uzytecznosci parsujace
def parse_latest_version_name(version_manifest):
    return version_manifest['latest']

def parse_latest_release_version_name(version_manifest):
    return parse_latest_version_name(version_manifest)['release']

def parse_all_versions_info(version_manifest):
    return version_manifest['versions']

def parse_version_info(version_manifest, version_name):
    # print('version: {}, infoid: {} '.format(version_name, version_manifest['versions'][0]['id']))
    version_info = [info for info in parse_all_versions_info(version_manifest) if str(info['id']) == version_name]
    # print(version_info)
    return version_info[0]

def parse_url_to_detailed_version_manifest_url(version_info):
    return version_info['url']

def get_detailed_version_manifest(version_manifest, version_name):
    info = parse_version_info(version_manifest, version_name)
    detailed_manifest_url = parse_url_to_detailed_version_manifest_url(info)
    return json_detailed_version_manifest(detailed_manifest_url)

def parse_version_download_info(detailed_manifest):
    return detailed_manifest['downloads']

def parse_server_download(version_download_info):
    return version_download_info['server']

def parse_download_url(download_info):
    return download_info['url']

def get_download_info(version_manifest, version_name):
    detailed_manifest = get_detailed_version_manifest(version_manifest, version_name)
    return parse_version_download_info(detailed_manifest)

def get_server_download_info(version_manifest, version_name):
    download_info = get_download_info(version_manifest, version_name)
    return parse_server_download(download_info)

# moduly
def list_all_versions(version_manifest):
    for version_info in version_manifest['versions']:
        print(version_info['id'])

def print_latest_version_name(version_manifest):
    print(parse_latest_version_name(version_manifest))

def print_lasetst_server_download_info(version_manifest):
    version = parse_latest_release_version_name(version_manifest)
    print("wersja: {}".format(version))
    print(get_server_download_info(version_manifest, version))


if __name__ == "__main__":    
    # parser = argparse.ArgumentParser(description='narzedzie automatycznego zarzadzania wersjami serwera mc')

    # parser.add_argument('--list-all', action='store_true', 
    #     help="wypisz wszystkie mozliwe wersje")
    # parser.add_argument('--info', action='store', choices=['WERSJA'],
    #     help="wypisz informacje dotyczace konkretnej wersji")
    # parser.add_argument('--download', action='store', 
    #     help="pobierz serwer danej wersji")
    # parser.add_argument('module', choices=['list-versions', 'download'])

    # parser.parse_args()

    # version_manifest = JSON_version_manifest()
    # version_name = parse_latest_release_version_name(version_manifest)
    # last_info = parse_version_info(version_manifest, version_name)
    # detailed_manifest_url = parse_url_to_detailed_version_manifest_url(version_info)
    # detailed_manifest = JSON_detailed_version_manifest(detailed_manifest_url)    

    # debug
    print( # dla werstwy serwisu
        # parse_latest_version_name(version_manifest)
        # parse_latest_release_version_name(version_manifest)
        # parse_all_versions_info(version_manifest)
        # parse_version_info(version_manifest, version_name)
        # parse_url_to_detailed_version_manifest_url(last_info)
        # get_detailed_version_manifest(version_manifest, version_name)
        # get_download_info(version_manifest, version_name)
        # get_server_download_info(version_manifest, version_name)
    )
    # dla warstwy modulow
    # list_all_versions(version_manifest)
    # print_latest_version_name(version_manifest)

    version_manifest = json_version_manifest()
    print_lasetst_server_download_info(version_manifest)


# TODO
# pobieranie ze sprawdzaniem sha1 czy server w folderze jest aktualny
# argumenty polecenia