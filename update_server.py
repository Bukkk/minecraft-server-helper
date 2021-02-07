from http.client import HTTPSConnection
from json import loads as parse_json
from datetime import datetime, timedelta, timezone

# connection layer
def https_get_to_host(host: str, remote_path: str):
    https_connection = HTTPSConnection(host)    
    https_connection.request('GET', remote_path)

    response_payload = https_connection.getresponse().read()    
    https_connection.close()

    return response_payload

def https_get_to_url(full_url: str):
    from urllib.parse import urlparse
    parsed_url = urlparse(full_url)

    return https_get_to_host(parsed_url.netloc, parsed_url.path)

# download layer
def fetch_version_manifest(version_manifest_url):
    return parse_json(https_get_to_url(version_manifest_url))

def fetch_detailed_version_manifest(detailed_version_manifest_url):
    return parse_json(https_get_to_url(detailed_version_manifest_url))

# abstraction layer
class VersionInfo:
    "abstraction of api at launchermeta.mojang.com"

    def __init__(self):
        self.version_manifest = fetch_version_manifest('https://launchermeta.mojang.com/mc/game/version_manifest.json')

    def all_version_names(self):
        "list - version names newer first"

        return [index['id'] for index in self.version_manifest['versions']]

    def latest_release_name(self):
        return self.version_manifest['latest']['release']
    
    def latest_snapshot_name(self):
        return self.version_manifest['latest']['snapshot']

    def version_details(self, version_name):
        "dict - some usable info"

        details = {}

        short_info = {}
        try:
            short_info = self.__find_version_in_manifest(version_name)
        except IndexError as e:
            print("given version does not exist!!!!")
            raise e

        details['version_name'] = short_info['id']
        details['type'] = short_info['type']
        details['date'] = datetime.fromisoformat(short_info['releaseTime']).astimezone(timezone.utc)

        long_info = fetch_detailed_version_manifest(short_info['url'])

        details['assets_version'] = long_info['assetIndex']['id']
        details['client_sha1'] = long_info['downloads']['client']['sha1']
        details['client_url'] = long_info['downloads']['client']['url']
        details['server_sha1'] = long_info['downloads']['server']['sha1']
        details['server_url'] = long_info['downloads']['server']['url']

        return details

    def __find_version_in_manifest(self, version_name):
        version_info = [info for info in self.version_manifest['versions'] if str(info['id']) == version_name]
        return version_info[0] # throws if not found

# modules
def list_all_versions(database: VersionInfo):
    for name in database.all_version_names():
        print(name)

def latest_version(database: VersionInfo):
    print('release: {}'.format(database.latest_release_name()))
    print('snapshot: {}'.format(database.latest_snapshot_name()))

def quiet_latest_release(database: VersionInfo):
    print(database.latest_release_name())

def quiet_latest_snapshot(database: VersionInfo):
    print(database.latest_snapshot_name())

def latest_server_link(database: VersionInfo):
    version = database.latest_release_name()
    details = database.version_details(version)
    
    print('version: {}'.format(version))
    print('type: {}'.format(details['type']))
    print('download link: {}'.format(details['server_url']))
    print('sha1: {}'.format(details['server_sha1']))
    print('release date: {}'.format((details['date'])))
    print('age: {} ago'.format(datetime.now().astimezone(timezone.utc) - details['date']))

def useful_info(database: VersionInfo, version):
    # print(database.version_details(version))

    details = database.version_details(version)
    for key in details:
        print('{}: {}'.format(key, details[key]))
    print('age: {} ago'.format(datetime.now().astimezone(timezone.utc) - details['date']))

# main
if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description='mojang api helper')

    parser.add_argument('-L', '--list_all', action='store_true', 
        help='print all versions')
    parser.add_argument('-r', '--release', action='store_true',
        help='last release - quiet')
    parser.add_argument('-s', '--snapshot', action='store_true',
        help='last snapshot - quiet')
    parser.add_argument('-l', '--last_versions', action='store_true',
        help='print last versions of release and snapshot releases')
    parser.add_argument('-u', '--version_info',
        help='print some info for a given version')
    

    args = parser.parse_args()

    database = VersionInfo()

    if args.list_all:
        list_all_versions(database)
    elif args.release:
        quiet_latest_release(database)
    elif args.snapshot:
        quiet_latest_snapshot(database)
    elif args.last_versions:
        latest_version(database)
    elif args.version_info:
        useful_info(database, args.version_info)    
    else:
        latest_server_link(database)

