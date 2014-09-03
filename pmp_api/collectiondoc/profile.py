"""
"""
import json
import os
from pelecanus import PelicanJson


class InvalidProfile(Exception):
    pass


VERSION = "1.0"
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


def validate(data, profile_type="story"):
    # Do we want to return a Boolean or raise an error
    name, profile_file = profiles[profile_type]
    current_dir = os.path.abspath(os.path.dirname(__file__))
    profile_location = os.path.join(current_dir,
                                    'stored_profiles',
                                    profile_file)
    with open(profile_location, 'r') as f:
        profile = json.loads(f.read())
    required = profile['REQUIRED']
    temp_data = PelicanJson(data)
    try:
        next(temp_data.search_value(required))
        return False
    except StopIteration:
        pelican_profile = PelicanJson(profile)
        for path, value in data.paths():
            if type(value) != type(pelican_profile.get_nested_value(path)):
                return False
    return True


def new_profile(profile_type="story", collection=None):
    name, profile_file = profiles[profile_type]
    current_dir = os.path.abspath(os.path.dirname(__file__))
    profile_location = os.path.join(current_dir,
                                    'stored_profiles',
                                    profile_file)

    with open(profile_location, 'r') as f:
        data = json.loads(f.read())
        data['version'] = VERSION

        if collection is None:
            del data['links']['collection']
        else:
            data['links']['collection'][0]['href'] = collection
        del data['REQUIRED']
        del data['OPTIONAL']

    return data


def empty_values(data, profile_type="story"):
    name, profile_file = profiles[profile_type]
    current_dir = os.path.abspath(os.path.dirname(__file__))
    profile_location = os.path.join(current_dir,
                                    'stored_profiles',
                                    profile_file)
    with open(profile_location, 'r') as f:
        profile = json.loads(f.read())
    optional = profile['OPTIONAL']
    temp_data = PelicanJson(data)
    return list(temp_data.search_value(optional))


def edit_profile(profile, new_data):
    missing_paths = []
    pelican_profile = PelicanJson(profile)
    pelican_data = PelicanJson(new_data)
    for path, value in pelican_data.enumerate():
        try:
            pelican_profile.set_nested_value(path, value)
        except (IndexError, KeyError):
            missing_paths.append((path, value))
    return pelican_profile.convert()
