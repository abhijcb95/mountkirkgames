# Copyright 2018 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" This template creates a backend service. 

    block starting line 69 allows managed instance groups to be set as backend groups as well.
"""

REGIONAL_GLOBAL_TYPE_NAMES = {
    # https://cloud.google.com/compute/docs/reference/rest/v1/regionBackendServices
    True: 'gcp-types/compute-v1:regionBackendServices',
    # https://cloud.google.com/compute/docs/reference/rest/v1/backendServices
    False: 'gcp-types/compute-v1:backendServices'
}


def set_optional_property(destination, source, prop_name):
    """ Copies the property value if present. """

    if prop_name in source:
        destination[prop_name] = source[prop_name]


def get_backend_service_outputs(res_name, backend_name):
    """ Creates outputs for the backend service. """

    outputs = [
        {
            'name': 'name',
            'value': backend_name
        },
        {
            'name': 'selfLink',
            'value': '$(ref.{}.selfLink)'.format(res_name)
        }
    ]

    return outputs


def generate_config(context):
    """ Entry point for the deployment resources. """

    properties = context.properties
    res_name = context.env['name']
    name = properties.get('name', res_name)
    project_id = properties.get('project', context.env['project'])
    is_regional = False
    backend_properties = {
        'name': name,
        'project': project_id,
        'protocol': 'HTTP',
        'loadBalancingScheme': 'EXTERNAL',
        'portName': 'http',
        'backends': properties['backends'],
        'healthChecks': [properties.get('healthCheck_url')]
    }
    
    for backend in backend_properties['backends']:
        backend['group'] = 'https://www.googleapis.com/compute/v1/projects/' + project_id + '/regions/' + backend['region'] + '/instanceGroups/' + backend['name'] + '-backend-server'
        del backend['name']
        del backend['region']

    resource = {
        'name': res_name,
        'type': REGIONAL_GLOBAL_TYPE_NAMES[is_regional],
        'properties': backend_properties,
    }

    optional_properties = [
        'description',
        'iap',
        'timeoutSec',
        'region',
        'enableCDN',
        'sessionAffinity',
        'affinityCookieTtlSec',
        'connectionDraining',
        'cdnPolicy'
    ]

    for prop in optional_properties:
        set_optional_property(backend_properties, properties, prop)

    outputs = get_backend_service_outputs(res_name, name)

    return {'resources': [resource], 'outputs': outputs}
