"""
"""
import json
import os
import copy
from itertools import chain

from ..utils.json_utils import get_path
from ..utils.json_utils import gen_path
from ..utils.json_utils import find_value
from ..utils.json_utils import get_nested_val
from ..utils.json_utils import set_value


class InvalidProfile(Exception):
    pass


class Profile:
    """
    """
    def __init__(self, profile_type="story"):
        # A good list but by no means all of the profiles available
        profiles = {'contributor': ('Contributor Profile',
                                    'contr_profile.json'),
                    'topic': ('Topic Profile',
                              'topic_profile.json'),
                    'episode': ('Episode Profile',
                                'episode_profile.json'),
                    'series': ('Series Profile',
                               'series_profile.json'),
                    'property': ('Property Profile',
                                 'property_profile.json'),
                    'group': ('Group Profile',
                              'group_profile.json'),
                    'audio': ('Audio Profile',
                              'audio_profile.json'),
                    'video': ('Video Profile',
                              'video_profile.json'),
                    'media': ('Media Profile',
                              'media_profile.json'),
                    'image': ('Image Profile',
                              'image_profile.json'),
                    'story': ('Story Profile',
                              'story_profile.json'),
                    'organization': ('Organization Profile',
                                     'organization_profile')}
        profile_name, profile_file = profiles[profile_type]
        current_dir = os.path.abspath(os.path.dirname(__file__))
        profile_location = os.path.join(current_dir,
                                        'stored_profiles',
                                        profile_file)
        self._load_profile(profile_location)

    def _load_profile(self, prof_location):
        with open(prof_location, 'r') as f:
            self.profile = json.loads(f.read())
        self.data = copy.copy(self.profile)

    @property
    def is_valid(self, data):
        result = list(find_value(data, [Inf]))
        if len(result) > 0:
            errmsg = "Invalid profile: Missing values for following paths: `{}`"
            raise InvalidProfile(errmsg.format(".".join(result)))

        # Also need to type-check the whole thing! So a list
        # value doesn't get clobbered by a string!
        # We pretty much need a way to iterate these things, some generic
        # iterate protocol. Possibly subclass dict and create an __iter__ for it
        return True

    def empty_values(self, data):
        """
        """
        return find_value(data, None)

    def serialize(self):
        """Returns valid JSON representation of the profiled object that conforms
        to profile parameters and with any None values removed.

        Unsafe if values have not been finalized: this will raise
        InvalidProfile because it checks if profile is valid before
        serializing.
        """
        # Should probably be checked by code that calls this.
        assert self.is_valid
        finished_data = copy.deepcopy(self.data)
        empties = empty_values(finished_data)
        for empty in empties:
            *elements, key = empty
            if elements:
                inner_object = get_nested_val(finished_data, elements)
                del inner_object[key]
            else:
                del finished_data[key]
        return json.dumps(finished_data)
