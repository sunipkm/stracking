Guide
=====

**STracking** is a python framework to develop particles tracking pipeline. This library has been developed to track
intra-cellular object in microscopy 2D+t and 3D+t images, but can be use for any spots tracking application in 
2D+t and 3D+t images.

A particles tracking pipeline is decomposed into sequential steps. First the particles are **detected** individually and
independently in each time frame of the image. Then a **linker** algorithm is used to link particles between frames and
form the tracks. Then we calculate the **properties** of the particles (size, intensity...) and the **features** of the
tracks (length, distance...) to analyse them. A final step is the tracks **filtering** that uses the properties and 
features to select tracks of interest.


Library components
------------------
The **STracking** library is made of one module per step of the pipeline. Plus one module for data containers and on module for pipeline:

* **Containers**: ``SParticles`` and ``STracks`` containers based on ``napari`` points and track layer data structures to store particles and tracks
* **Detectors**: define a detector interface and implementations of particle detection algorithm for 2D and 3D image sequences
* **Linkers**: define a linker interface and implementation of particle linkers (or trackers) for 2D and 3D image sequences
* **properties**: define an interface and implementations of algorithms to measure properties of particles (intensity...)
* **feature**: define an interface and implementations of algorithms to measure tracks properties (length, displacement...)
* **filters**: define an interface and implementations of algorithms to select tracks
* **pipeline**: Define a class to run a STracking pipeline defined in a json file

Containers
~~~~~~~~~~

The containers module has two classes ``SParticles`` and ``STracks`` to facilitate the management of the *particles* and *tracks*
data and metadata. The containers have been designed to be compatible with the napari layers data structures.

A ``SParticles`` object contains a list of particles and their metadata in a 2D+t or 3D+t image. It contains 3 attributes:

    data : array (N, D+1)
        Coordinates for N points in D+1 dimensions. ID,T,(Z),Y,X. The first
        axis is the integer ID of the track. D is either 3 or 4 for planar
        or volumetric time series respectively.
    properties : dict {str: array (N,)}, DataFrame
        Properties for each point. Each property should be an array of length N,
        where N is the number of points.
    scale : tuple of float
        Scale factors for the image data.

A ``STracks`` object contains a list of tracks and their metadata in a 2D+t or 3D+t image. It contains 5 attributes:

    data : array (N, D+1)
        Coordinates for N points in D+1 dimensions. ID,T,(Z),Y,X. The first
        axis is the integer ID of the track. D is either 3 or 4 for planar
        or volumetric time series respectively.
    properties : dict {str: array (N,)}, DataFrame
        Properties for each point. Each property should be an array of length N,
        where N is the number of points.
    graph : dict {int: list}
        Graph representing associations between tracks. Dictionary defines the
        mapping between a track ID and the parents of the track. This can be
        one (the track has one parent, and the parent has >=1 child) in the
        case of track splitting, or more than one (the track has multiple
        parents, but only one child) in the case of track merging.
        See examples/tracks_3d_with_graph.py
    features: dict {str: dict}
            Properties for each tracks. Each feature should be an map of
            trackID=feature. Ex: features['length'][12]=25.2
    scale : tuple of float
        Scale factors for the image data.


Detectors
~~~~~~~~~

``SDetector`` are objects with the same interface. They have a ``run`` method that takes a numpy array ( 2D+t or 3D+t image) as 
an input and returns detections in a ``SParticles`` object. The parameters of the detector have to be passed to it constructor.

.. code-block:: python

    from stracking.detectors import DoGDetector
    ...
    detector = DoGDetector(min_sigma=4, max_sigma=5, threshold=0.2)
    particles = detector.run(image)
    ...


To create a new detector developers just need to inherit `SDetector`:

.. code-block:: python

    from stracking.detectors import SDetector

    class MyDetector(SDetector):
        def __init__(self):
            super().__init__()

        def run(self, image, scale=None):
            # Implement the detector here
            spots_ = ...
            return SParticles(data=spots_, properties={}, scale=scale)


Linkers
~~~~~~~

``SLinker`` are objects with the same interface. They have a ``run`` method that takes the detections (in a ``SParticles`` 
object) and optionally a numpy array (the 2D+t or 3D+t image), and return the calculated tracks in a ``STracks`` object.
The parameters of a linker have to be passed in the constructor. For example, the ``SPLinker`` (Shortest Path) linker need a 
cost function, and a frame gap parameters: 

.. code-block:: python

    from stracking.linkers import SPLinker, EuclideanCost
    ...
    euclidean_cost = EuclideanCost(max_cost=3000)
    my_tracker = SPLinker(cost=euclidean_cost, gap=1)
    tracks = my_tracker.run(particles)
    ...


To create a new linker developers just need to inherit `SLinker`:

.. code-block:: python

    from stracking.linkers import SDetector

    class MyLinker(SLinker):
        def __init__(self, cost=None):
            super().__init__(cost)

        def run(self, particles, image=None):
            # Implement the linker here
            mydata = ...
            return STracks(data=mydata, properties=None, graph={}, scale=particles.scale)

Properties
~~~~~~~~~~~

``SProperty`` based objects are objects with the same interface. They have a ``run`` method that takes the detections (in a ``SParticles`` 
object) and a numpy array (the 2D+t or 3D+t image), and returns the input ``SParticles`` where the calculated properties have been added
to the ``SParticles.properties`` dictionary. All the ``SProperty`` parameters have to be send to the constructor. Here is an 
example with the ``IntensityProperty`` algorithm that calculate the `min`, `max`, `mean` and `std` intensities inside the spots using a
given radius:

.. code-block:: python

    from stracking.properties import IntensityProperty
    ...
    property_calc = IntensityProperty(radius=2)
    property_calc.run(particles, image)
    ...


To create a new property developers just need to inherit `SProperty`:

.. code-block:: python

    from stracking.properties import SProperty

    class MyProperty(SProperty):
        def __init__(self, radius):
            super().__init__()

        def run(self, sparticles, image):
            # Calculate here some properties and add them to sparticles.properties
            ...
            return sparticles

Features
~~~~~~~~

``SFeature`` based objects are objects with the same interface. They have a ``run`` method that takes the tracks (in a ``STRacks``
object) and optionally a numpy array (the 2D+t or 3D+t image), and returns the input ``STracks`` object where the calculated
features have been added to the ``STracks.features`` dictionary. Here is an example of the ``DistanceFeature`` that calculate
the distance a particle moved:

.. code-block:: python

    from stracking.filters import DistanceFeature
    ...
    feature_calc = DistanceFeature()
    feature_calc.run(tracks)
    ...

To create a new feature developers just need to inherit `SFeature`:

.. code-block:: python

    from stracking.features import SFeature

    class MyFeature(SFeature):
        def __init__(self):
            super().__init__()

        def run(self, stracks, image=None):
            # Calculate here some features and add them to stracks.features
            ...
            return stracks

filters
~~~~~~~~

``SFilter`` based objects are objects with the same interface. The have a ``Run`` method that takes the tracks (in a ``STRacks``
object) as input and return the same tracks object where filtered tracks have been removed:

.. code-block:: python

    from stracking.filters import FeatureFilter
    ...
    filter_calc = FeatureFilter(feature_name='distance', min_val='20', max_val='120')
    filter_calc.run(tracks)


To create a new filter developers just need to inherit `SFilter`:

.. code-block:: python

    from stracking.filters import SFilter

    class FeatureFilter(STracksFilter):
        def __init__(self):
            super().__init__()

        def run(self, stracks):
            # Implement here the algorithm to select some tracks
            new_stracks = ...
            return new_stracks


Read and Write
--------------

The **STracking** library provides an extra module called **io**. It allows to read tracks data from many formats (JSON, CSV, 
Icy xml, ISBI xml, TrackMate xml...) and write the tracks in JSON format.
To read a file, you can use the convenient method ``read_tracks`` that takes the path of an input file and return a ``STracks`` 
object:

.. code-block:: python

    from stracking.io import read_tracks
    tracks = read_tracks('path/to/the/tracks/file.xml'))

You can also alternatively call the IO class from the dedicated format. Read tracks are then available in the ``tracks``
attribute of the IO object.

.. code-block:: python

    from stracking.io import TrackMateIO

    trackmate_reader = TrackMateIO('path/to/the/trackmate/model/file.xml')
    trackmate_reader.read()
    print(trackmate_reader.stracks.data)


To write ``STracks`` into a file, the current version of **STracking** only support the *JSON* format from the native 
**stracking** IO class:

.. code-block:: python

    from stracking.io import StIO
    ...
    writer = StIO('path/to/the/tracks/file.json')
    writer.write(mytracks)
    ...

a more convenient function is the ``write_tracks`` function:

.. code-block:: python

    from stracking.io import write_tracks
    ...
    write_tracks('path/to/the/tracks/file.json', mytracks)
    ...

It is also possible to save the particles in a file. The supported format is a CSV file where each columns is a particle property.
Mandatory properties are 'T', 'Y', 'X' coordinates for 2D+t particles and  'T', 'Z', 'Y', 'X' coordinates for 3D+t particles.
To write particles to file you can use the ``write_particles`` function:
.. code-block:: python

    from stracking.io import write_particles
    ...
    write_particles('path/to/the/tracks/file.csv', particles)
    ...

And to read particles, the ``read_particles`` function:

.. code-block:: python

    from stracking.io import read_particles
    ...
    particles read_particles('path/to/the/tracks/file.csv')
    ...



Pipeline
--------   

Writing a tracking pipeline with **STracking** is straightforward. You just need to call the different modules in a sequence:

.. code-block:: python

    from stracking.data import fake_tracks1
    from stracking.detectors import DoGDetector
    from stracking.linkers import SPLinker, EuclideanCost
    from stracking.features import DistanceFeature
    from stracking.filters import FeatureFilter
    from stracking.io import write_tracks
    import napari

    # Load data
    image = fake_tracks1()

    # Open napari
    viewer = napari.Viewer(axis_labels='tyx')
    viewer.add_image(image, contrast_limits=[0, 300])

    # Detection
    detector = DoGDetector(min_sigma=3, max_sigma=5, threshold=0.2)
    particles = detector.run(image)

    # Display spots
    viewer.add_points(particles.data, size=4, face_color="red", edge_color="red", blending='opaque')

    # Linking
    euclidean_cost = EuclideanCost(max_cost=3000)
    my_tracker = SPLinker(cost=euclidean_cost, gap=1)
    tracks = my_tracker.run(particles)

    # Display tracks
    viewer.add_tracks(tracks.data, name='Tracks', colormap="hsv")

    # Calculate distance feature
    feature_calc = DistanceFeature()
    feature_calc.run(tracks)

    # Keep only tracks that moves less than 60 pixels
    filter_calc = FeatureFilter(feature_name='distance', min_val=20, max_val=60)
    filter_calc.run(tracks)

    # Display filtered tracks
    viewer.add_tracks(tracks.data, name='Filtered Tracks',colormap="hsv")
    napari.run()

    # Save the tracks
    write_tracks('path/to/the/tracks/file.json', tracks)


The STracking library also provides a ``STrackingPipeline`` class that allows to run a tracking pipeline from
a pipeline description file (JSON format):

.. code-block:: json

    {
      "name": "pipeline1",
      "author": "Sylvain Prigent",
      "date": "2022-04-13",
      "stracking_version": "0.1.8",
      "steps": {
        "detector": {
          "name": "DoGDetector",
          "parameters": {
            "min_sigma": 4,
            "max_sigma": 5,
            "sigma_ratio": 1.1,
            "threshold": 0.15,
            "overlap": 0
          }
        },
        "linker": {
          "name": "SPLinker",
          "cost": {
              "name": "EuclideanCost",
              "parameters": {}
          },
          "parameters": {
            "gap": 1,
            "min_track_length": 2
          }
        },
        "properties": [
          {
            "name": "IntensityProperty",
            "parameters": {
              "radius": 2.5
            }
          }
        ],
        "features": [
          {
            "name": "LengthFeature"
          },
          {
            "name": "DistanceFeature"
          },
          {
            "name": "DisplacementFeature"
          }
        ],
        "filters": [
          {
            "name": "FeatureFilter",
            "parameters": {
              "feature_name": "distance",
              "min_val": 20,
              "max_val": 60
            }
          }
        ]
      }
    }

Then, a pipeline can be run with the ``STrackingPipeline`` class

.. code-block:: python

    from stracking.data import fake_tracks1
    from stracking.io import write_tracks
    from stracking.pipelines import STrackingPipeline
    import napari

    # Load data
    image = fake_tracks1()

    # Run pipeline
    pipeline = STrackingPipeline()
    pipeline.load('path/to/the/pipeline.json')
    tracks = pipeline.run(image)

    # display
    viewer = napari.Viewer(axis_labels='tyx')
    viewer.add_image(image, contrast_limits=[0, 300])
    viewer.add_tracks(tracks.data, name='Pipeline Tracks',colormap="hsv")
    napari.run()

    # save
    write_tracks('pipeline_tracks.csv', tracks, format_='csv')
