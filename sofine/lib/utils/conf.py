"""Loads global sofine configuration in from a configuration file. The file must be stored 
in the project root and must be called either `sofine.conf` or `example.sofine.conf`. If 
`sofine.conf` is found it will be used over `example.sofine.conf`.

Current supported configuration keys are:

* `plugin_path` - The path to the user's plugins directory. This can be any reachable path 
that sofine has permission to read.
* `http_plugin_url` - The user-defined base URL to call for user HTTP plugins.
* `data_format_plugin_path` - The path to the user's data format plugin directory. Data format plugins govern the data format (e.g. the default, JSON) of returned data sets.
* `rest_port` - The port for running the sofine REST server under the `localhost` domain. 
The default value is `10000` defined in `example.sofine.conf`.
"""


from __future__ import print_function
import inspect
import sys
import json
import os


CUSTOM_PLUGIN_BASE_PATH = None
"""The user-defined plugin directory. The idea is that users of sofine simply install the 
library, configure this value, and then can deploy, version control, write tests for and 
otherwise manage their plugins in a separate directory, which sofine CLI and REST calls 
transparently look in to load plugins. This value is defined in the JSON configuration file 
`sofine.conf` under the key `plugin_path`.
"""

DEFAULT_DATA_FORMAT = 'format_json'
"""The default data format for deserializing input and serializing output. If the client call 
does not specify a data format using the `--SF-d|--SF-data-format` argument, then JSON will be used."""


CUSTOM_DATA_FORMAT_PLUGIN_PATH = None
"""The user-defined output plugin directory. Users who want to define custom plugins can 
define this value as an environment variable or config and deploy their output plugins there."""


REST_PORT = None
"""The port for running the sofine REST server under the `localhost` domain. This value 
is defined in the JSON configuration file `sofine.conf` under the key `rest_port`. The default 
value is defined in `example.sofine.conf` and will be used if the user doesn't override it in 
`sofine.conf`.
"""


def get_plugin_conf():
    plugin_conf_path = '/'.join(inspect.stack()[0][1].split('/')[:-4])

    plugin_conf = None
    try:
        plugin_conf = json.load(open(plugin_conf_path + '/sofine.conf'))
    except:
        pass

    return plugin_conf


def load_plugin_path(environ_var, conf_key, warn=True):
    # Check environment variables for and prefer those if found
    path = os.environ.get(environ_var)
    if path:
        sys.path.insert(0, path) 
    else:
        plugin_conf = get_plugin_conf()
        if plugin_conf:
            path = plugin_conf[conf_key]
            sys.path.insert(0, path) 

    if not path and warn:
        print('Plugin Path not defined in {0} environment variable or {1} key in "sofine.conf" in sofine root directory'.format(environ_var, conf_key), file=sys.stderr)
    else:
        return path


# Add the plugins directory to the system path so the dynamic module load
#  finds any plugins in their and load_module just works
PLUGIN_BASE_PATH = '/'.join(inspect.stack()[0][1].split('/')[:-3]) + '/plugins'
sys.path.insert(0, PLUGIN_BASE_PATH) 

CUSTOM_PLUGIN_BASE_PATH = load_plugin_path('SOFINE_PLUGIN_PATH', 'plugin_path')

CUSTOM_HTTP_PLUGIN_URL = load_plugin_path('SOFINE_HTTP_PLUGIN_URL', 'http_plugin_url')

DATA_FORMAT_PLUGIN_BASE_PATH = '/'.join(inspect.stack()[0][1].split('/')[:-3]) + '/data_format_plugins'
sys.path.insert(0, DATA_FORMAT_PLUGIN_BASE_PATH) 

# Check environment variables for and prefer those if found
warn = False
CUSTOM_DATA_FORMAT_PLUGIN_PATH = load_plugin_path('SOFINE_DATA_FORMAT_PLUGIN_PATH', 'data_format_plugin_path', warn)


REST_PORT = os.environ.get('SOFINE_REST_PORT')
if REST_PORT:
    REST_PORT = int(REST_PORT)
else:
    plugin_conf = get_plugin_conf()
    REST_PORT = plugin_conf['rest_port']

if not REST_PORT:
    print('REST port not defined in SOFINE_REST_PORT environment variable or "rest_port" key in "sofine.conf" in sofine root directory', file=sys.stderr) 

