"""
"""
import json
import os
from pelecanus import PelicanJson


class InvalidProfile(Exception):
    pass


VERSION = "1.0"
# Other profiles have yet to be written...
profiles = {'story': ('Story Profile',
                      'story_profile.json')}


def new_profile(profile_type="story", collection=None):
    """This function can create a new profile from the JSON object
    stored in the stored_profiles.
    """
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


def edit_profile(profile, new_data):
    """EXPERIMENTAL function for cramming data into a profile.
    """
    pelican_profile = PelicanJson(profile)
    pelican_data = PelicanJson(new_data)
    for path, value in pelican_data.enumerate():
        pelican_profile.set_nested_value(path, value, force=True)
    return pelican_profile.convert()


def empty_values(data, profile_type="story"):
    """Function that lists all of the fields missing values.
    """
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


def validate(data, profile_type="story"):
    """Validator for a profile: it will return False if profile
    contains required fields that have not been filled in.
    """
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
        pass

    # next step is to type-check all the values:
    pelican_profile = PelicanJson(profile)
    for path, value in temp_data.enumerate():
        try:
            if type(value) != type(pelican_profile.get_nested_value(path)):
                return False, path
        except (TypeError, IndexError, KeyError):
            return False, path
    return True, None
