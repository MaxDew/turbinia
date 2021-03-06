# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Basic Turbinia config."""

import imp
import itertools
import logging
import os
import sys

log = logging.getLogger('turbinia')

# Look for config files with these names
CONFIGFILES = ['.turbiniarc', 'turbinia_config.py']
# Look in homedir and in the current config dir for config files
CONFIGPATH = [
    os.path.expanduser('~'),
    os.path.dirname(os.path.abspath(__file__))]
# Config vars that we expect to exist in the configuration
CONFIGVARS = [
    # Turbinia Config
    'TASK_MANAGER',
    'LOG_FILE',
    'OUTPUT_DIR',
    'SLEEP_TIME',
    'SINGLE_RUN',
    # GCE CONFIG
    'PROJECT',
    'ZONE',
    'INSTANCE',
    'DEVICE_NAME',
    'SCRATCH_PATH',
    'BUCKET_NAME',
    'PSQ_TOPIC',
    'PUBSUB_TOPIC',
    # REDIS CONFIG
    'REDIS_HOST',
    'REDIS_PORT',
    # Timesketch config
    'TIMESKETCH_HOST',
    'TIMESKETCH_USER',
    'TIMESKETCH_PASSWORD',]
# Environment variable to look for path data in
ENVCONFIGVAR = 'TURBINIA_CONFIG_PATH'

CONFIG = None


class TurbiniaConfigException(Exception):
  pass


def LoadConfig():
  """Finds Turbinia config file and loads it."""
  # TODO(aarontp): Find way to not require global var here.  Maybe a singleton
  # pattern on the config class.
  global CONFIG
  if CONFIG:
    return CONFIG

  if os.environ.has_key(ENVCONFIGVAR):
    CONFIGPATH.extend(os.environ[ENVCONFIGVAR].split(':'))

  config_file = None
  # Load first file found
  for _dir, _file in itertools.product(CONFIGPATH, CONFIGFILES):
    if os.path.exists(os.path.join(_dir, _file)):
      config_file = os.path.join(_dir, _file)
      break

  if config_file is None:
    raise TurbiniaConfigException(u'No config files found')

  log.info('Loading config from {0:s}'.format(config_file))
  _config = imp.load_source('config', config_file)
  _config.configSource = config_file
  ValidateAndSetConfig(_config)
  CONFIG = _config
  return _config


def ValidateAndSetConfig(_config):
  """Makes sure that the config has the vars loaded and set in the module."""
  # TODO(aarontp): Allow for non-mandatory config options
  for var in CONFIGVARS:
    if not hasattr(_config, var):
      raise TurbiniaConfigException(
          u'No config attribute {0:s}:{1:s}'.format(_config.configSource, var))
    if getattr(_config, var) is None:
      raise TurbiniaConfigException(
          u'Config attribute {0:s}:{1:s} is not set'.format(
              _config.configSource, var))

    # Set the attribute in the current module
    setattr(sys.modules[__name__], var, getattr(_config, var))
