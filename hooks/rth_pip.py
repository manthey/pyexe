from pip._vendor.distlib import resources, __loader__

resources.register_finder(__loader__, resources.ResourceFinder)
