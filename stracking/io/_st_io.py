import os
import json

from ._io import STrackIO
from stracking.containers import STracks


class StIO(STrackIO):
    """Read/write tracking with the native stracking format

    This format has been created for this library to easily read and write data
    stored in the STracks container

    Parameters
    ----------
    file_path: str
        Path of the .st.json file

    """
    def __init__(self, file_path):
        super().__init__(file_path)
        self.indent = None

    def is_compatible(self):
        if self.file_path.endswith('.st.json'):
            return True
        return False

    def read(self):
        if os.path.getsize(self.file_path) > 0:
            with open(self.file_path) as json_file:
                json_data = json.load(json_file)

        tracks = STracks()
        if 'tracks' in json_data:
            tracks.data = json_data['tracks']
        else:
            raise Exception('StIO reader: no tracks found in the input file')

        if 'properties' in json_data:
            tracks.properties = json_data['properties']

        if 'graph' in json_data:
            tracks.properties = json_data['graph']

        if 'features' in json_data:
            tracks.properties = json_data['features']

        if 'scale' in json_data:
            tracks.properties = tuple(json_data['scale'])

    def write(self):
        json_data = dict()
        json_data['tracks'] = self.stracks.data.tolist()
        json_data['properties'] = self.stracks.properties
        json_data['graph'] = self.stracks.graph
        json_data['features'] = self.stracks.features
        json_data['scale'] = list(self.stracks.scale)

        # write the data to file
        with open(self.file_path, 'w') as outfile:
            json.dump(json_data, outfile, indent=self.indent)
