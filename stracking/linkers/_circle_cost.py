from ._linker import SLinkerCost
import numpy as np
import datetime as dt
import os

class CircleCost(SLinkerCost):
    """
    Calculates the difference of distance^2 of two objects from a preset center point.
    """

    def __init__(self, x_center: float, y_center: float, max_cost = 100, log: bool = False):
        super().__init__(max_cost)
        self._center = (x_center, y_center)
        t = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
        self._logfile = None
        if log:
            self._logfile = open(os.getcwd() + '/%s.csv'%(t), 'w')
            if self._logfile is not None:
                print('Opened %s for writing.'%(self._logfile.name))


    def run(self, obj1, obj2, dt = 1):
        if len(obj1) == 4:
            raise RuntimeError('Not applicable on 3D tracks.')
        d1 = (obj1[1] - self._center[0])**2 + (obj1[2] - self._center[1])**2 # distance, or 'radius' of first point
        d2 = (obj2[1] - self._center[0])**2 + (obj2[2] - self._center[1])**2 # distance, or 'radius' of the second point
        cost = np.abs(d1 - d2) + (obj1[1] - obj2[1])**2 + (obj2[2] - obj2[2])**2 # and the distance between the two points
        if self._logfile is not None:
            self._logfile.write('%d,%f,%f,%d,%f,%f,%f,%f,%f\n'%(obj1[0], obj1[1], obj1[2], obj2[0], obj2[1], obj2[2], d1, d2, cost))
            self._logfile.flush()
        return cost # if the radii are close to equal, they are more likely to be connected