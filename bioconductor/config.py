# A simple configuration module to reduce duplication.

import os
import os.path
import platform
import logging
import ConfigParser

# log.basicConfig(format='%(levelname)s: %(asctime)s %(filename)s - %(message)s',
#                     datefmt='%m/%d/%Y %I:%M:%S %p',
#                     level=log.DEBUG)

log = logging.getLogger("bioconductor.common")
log.debug("Loading configuration")

P_EXTENSION = '.properties'
GLOBAL_PROPERTIES_FILE = os.path.join(os.getcwd(), 'bioconductor' + P_EXTENSION)

def readFile(filename):
    if (os.path.isfile(filename) and os.access(filename, os.R_OK)):
        return True
    else:
        return False

if not readFile(GLOBAL_PROPERTIES_FILE):
    errMsg = "Global properties file '{filename}' is missing or unreadable.  " \
    "Can not continue.".format(filename = GLOBAL_PROPERTIES_FILE)
    log.error(errMsg)
    raise Exception(errMsg)

# Parse and read the file
globalConfigParser = ConfigParser.RawConfigParser()
globalConfigParser.read(GLOBAL_PROPERTIES_FILE)

CONFIG_ENVIRONMENT = globalConfigParser.get('Environment', 'environment');
ENVIRONMENT_PROPERTIES_FILE = os.path.join(os.getcwd(), CONFIG_ENVIRONMENT + P_EXTENSION)
# git clone https://github.com/Bioconductor/spb-properties in current directory
# (that's a private repo to hold sensitive info)
SENSITIVE_PROPERTIES_FILE = os.path.join(os.getcwd(), "spb-properties", "spb" + P_EXTENSION)

if not readFile(ENVIRONMENT_PROPERTIES_FILE):
    errMsg = "A properties file '{filename}' is required to configure the environment.  "\
    "Can not continue.".format(filename = ENVIRONMENT_PROPERTIES_FILE)
    log.error(errMsg)
    raise Exception(errMsg)

log.info("Environment is set to: '{env}'.".format(env = CONFIG_ENVIRONMENT))

# Parse and read the environment specific configuration
envSpecificConfigParser = ConfigParser.RawConfigParser()
envSpecificConfigParser.read(ENVIRONMENT_PROPERTIES_FILE)

sensitiveConfigParser = ConfigParser.RawConfigParser()
sensitiveConfigParser.read(SENSITIVE_PROPERTIES_FILE)

# FIXME: Rather than attempting to read the same properties in any environment,
#           it'd be much better if the config module's constructor (or factory)
#           offered a callback mechanism, to load the properties file and then
#           dispatch to environment specific functionality.

# Only used in the packagebuilder for now (we need to adjust it's properties)
BUILD_NODES = envSpecificConfigParser.get('Properties', 'builders').split(",")
BROKER = {
    "host": envSpecificConfigParser.get('Properties', 'stomp.host'),
    "port": int(envSpecificConfigParser.get('Properties', 'stomp.port'))
}
log.info("The following build nodes are enabled: %s.", BUILD_NODES)
if envSpecificConfigParser.has_option('Properties', 'activemq.username'):
    ACTIVEMQ_USER = envSpecificConfigParser.get('Properties', 'activemq.username')
else:
    ACTIVEMQ_USER = None
if envSpecificConfigParser.has_option('Properties', 'activemq.password'):
    ACTIVEMQ_PASS = envSpecificConfigParser.get('Properties', 'activemq.password')
else:
    ACTIVEMQ_PASS = None

if envSpecificConfigParser.has_option('Properties', 'github.issue.tracker.repo'):
    GITHUB_ISSUE_TRACKER_REPO = envSpecificConfigParser.get('Properties',
      'github.issue.tracker.repo')
else:
    GITHUB_ISSUE_TRACKER_REPO = None


BIOC_VERSION = globalConfigParser.get('UniversalProperties', 'bbs.bioc.version')

# TODO: Consider a better way to determine this
BIOC_R_MAP = {"2.7": "2.12", "2.8": "2.13", "2.9": "2.14",
    "2.10": "2.15", "2.14": "3.1", "3.0": "3.1",
    "3.1": "3.2", "3.2": "3.2", "3.3": "3.3",
    "3.4": "3.3", "3.5": "3.4", "3.6": "3.4"}

BUILDER_ID = platform.node().lower().replace(".fhcrc.org","")
BUILDER_ID = BUILDER_ID.replace(".local", "")

HOST_SPECIFIC_PROPERTIES_FILE = os.path.join(os.getcwd(), BUILDER_ID + P_EXTENSION)
if (os.path.exists(HOST_SPECIFIC_PROPERTIES_FILE)):
    hostSpecificConfigParser = ConfigParser.RawConfigParser()
    hostSpecificConfigParser.read(HOST_SPECIFIC_PROPERTIES_FILE)
else:
    hostSpecificConfigParser = envSpecificConfigParser



ENVIR = {
    'bbs_home': hostSpecificConfigParser.get('Properties', 'bbs.home'),
    'bbs_R_home': hostSpecificConfigParser.get('Properties', 'bbs.r.home'),
    'bbs_node_hostname': BUILDER_ID,
    'bbs_R_cmd': hostSpecificConfigParser.get('Properties', 'bbs.r.cmd'),
    'bbs_Bioc_version': BIOC_VERSION,

    'packagebuilder_home': hostSpecificConfigParser.get('Properties', 'packagebuilder.home'),

    'bbs_RSA_key': hostSpecificConfigParser.get('Properties', 'bbs.rsa.key'),
    'packagebuilder_RSA_key': hostSpecificConfigParser.get('Properties', 'spb.rsa.key'),
    'svn_user': sensitiveConfigParser.get('Sensitive', 'svn.user'),
    'svn_pass': sensitiveConfigParser.get('Sensitive', 'svn.user'),
    'tracker_user': sensitiveConfigParser.get('Sensitive', 'tracker.user'),
    'tracker_pass': sensitiveConfigParser.get('Sensitive', 'tracker.pass'),
    'github_token': sensitiveConfigParser.get('Sensitive', 'github.token')
}

TOPICS = {
    "jobs": "/topic/buildjobs",
    "events": "/topic/builderevents"
}

HOSTS = {
    'svn': 'https://hedgehog.fhcrc.org',
    'tracker': 'https://tracker.bioconductor.org',
    'bioc': 'https://bioconductor.org'
}


log.info("Finished loading configuration.")
