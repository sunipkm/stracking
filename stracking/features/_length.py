import math
import numpy as np
from ._feature import SFeature


class LengthFeature(SFeature):
    """Calculate track length features.

    Length is defined here as the number of point in a track

    """
    def __init__(self):
        pass

    def measure(self, stracks, image=None):
        data = stracks.data
        tracks_ids = np.unique(data[:, 0])
        length_features = dict()
        for t_id in tracks_ids:
            length_features[t_id] = np.count_nonzero(data[:, 0] == t_id)
        stracks.features['length'] = length_features
        return stracks


class DistanceFeature(SFeature):
    """Calculate track length features.

    Length is defined here as the number of point in a track

    """
    def __init__(self):
        pass

    def measure(self, stracks, image=None):
        if stracks.shape[1] < 5:
            return self._measure_2d(stracks)
        else:
            return self._measure_3d(stracks)

    def _measure_2d(self, stracks):
        data = stracks.data
        tracks_ids = np.unique(data[:, 0])
        distance_features = dict()

        scale_x = 1
        scale_y = 1
        if len(stracks.scale) == 3:
            scale_x = pow(stracks.scale[1], 2)
            scale_y = pow(stracks.scale[2], 2)

        for t_id in tracks_ids:
            track = data[data[:, 0] == t_id]
            distance = 0
            for i in range(track.shape[0]-1):
                distance += \
                    math.sqrt(scale_x*pow(track[i+1, 2]-track[i, 2], 2) +
                              scale_y*pow(track[i+1, 3]-track[i, 3], 2))
            distance_features[t_id] = distance

        stracks.features['distance'] = distance_features
        return stracks

    def _measure_3d(self, stracks):
        data = stracks.data
        tracks_ids = np.unique(data[:, 0])
        distance_features = dict()

        scale_x = 1
        scale_y = 1
        scale_z = 1
        if len(stracks.scale) == 3:
            scale_x = pow(stracks.scale[2], 2)
            scale_y = pow(stracks.scale[3], 2)
            scale_z = pow(stracks.scale[1], 2)

        for t_id in tracks_ids:
            track = data[data[:, 0] == t_id]
            distance = 0
            for i in range(track.shape[0]-1):
                distance += \
                    math.sqrt(scale_x*pow(track[i+1, 2]-track[i, 2], 2) +
                              scale_y*pow(track[i+1, 3]-track[i, 3], 2) +
                              scale_z*pow(track[i+1, 4]-track[i, 4], 2))
            distance_features[t_id] = distance

        stracks.features['distance'] = distance_features
        return stracks


class DisplacementFeature(SFeature):
    """Calculate track length features.

    Length is defined here as the number of point in a track

    """
    def __init__(self):
        pass

    def measure(self, stracks, image=None):
        if stracks.shape[1] < 5:
            return self._measure_2d(stracks)
        else:
            return self._measure_3d(stracks)

    def _measure_2d(self, stracks):
        data = stracks.data
        tracks_ids = np.unique(data[:, 0])
        displacement_features = dict()

        scale_x = 1
        scale_y = 1
        if len(stracks.scale) == 3:
            scale_x = pow(stracks.scale[1], 2)
            scale_y = pow(stracks.scale[2], 2)

        for t_id in tracks_ids:
            track = data[data[:, 0] == t_id]
            i_end = track.shape[0]-1
            displacement = \
                math.sqrt(scale_x*pow(track[i_end, 2]-track[0, 2], 2) +
                          scale_y*pow(track[i_end, 3]-track[0, 3], 2))
            displacement_features[t_id] = displacement

        stracks.features['displacement'] = displacement_features
        return stracks

    def _measure_3d(self, stracks):
        data = stracks.data
        tracks_ids = np.unique(data[:, 0])
        displacement_features = dict()

        scale_x = 1
        scale_y = 1
        scale_z = 1
        if len(stracks.scale) == 3:
            scale_x = pow(stracks.scale[2], 2)
            scale_y = pow(stracks.scale[3], 2)
            scale_z = pow(stracks.scale[1], 2)

        for t_id in tracks_ids:
            track = data[data[:, 0] == t_id]
            i_end = track.shape[0]-1
            displacement = \
                math.sqrt(scale_x*pow(track[i_end, 2]-track[0, 2], 2) +
                          scale_y*pow(track[i_end, 3]-track[0, 3], 2) +
                          scale_z*pow(track[i_end, 4]-track[0, 4], 2))
            displacement_features[t_id] = displacement

        stracks.features['displacement'] = displacement_features
        return stracks
