import ConfigParser
import StringIO
import logging
import argparse

import version

logger = logging.getLogger(__name__)


class ProxyConfiguration:
    def __init__(self, config_file='https-proxy.cfg'):
        self.config_defaults = {
            # Tuple contains the default and the command line flag.
            'rules': ('/usr/src/https-everywhere/rules', 'r'),
            'action': ('server', 'a'),
            'configfile': ('/etc/https-proxy.cfg', 'c'),
            'database': ('/dev/shm/https-proxy.sqlite', 'd'),
            'database_persist': ('/var/lib/https-proxy/https-proxy.sqlite',
                                 'D'),
            'listen': ('127.0.0.1:8000', 'l'),
            'rule_extensions': ('.xml,.XML', None),
        }
        self._configfile = None
        self.init_arguments()

        self.configparser_defaults = {}
        for k, v in self.config_defaults.items():
            self.configparser_defaults[k] = v[0]

        self._configfile = ConfigParser.SafeConfigParser(self.configparser_defaults, # noqa
                                                         allow_no_value=True)
        self._configfile.add_section('section')

        try:
            with open(self['configfile'], 'r') as f:
                config_string = '[section]\n' + f.read()

            fp = StringIO.StringIO(config_string)
            self._configfile.readfp(fp)
        except Exception as e:
            if len(logger.handlers) == 0:
                logging.basicConfig()
            logger.warn('Could not open configuration file %s. ' \
                        'Using defaults.', self['configfile'])


    def default_configuration(self):
        fp = StringIO.StringIO()

        configfile = ConfigParser.SafeConfigParser(self.configparser_defaults,
                                                   allow_no_value=True)
        configfile.write(fp)

        return configfile.getvalue()

    def init_arguments(self):
        description = 'HTTP to HTTPS redirection server'
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('-v', action='version', version=version.VERSION,
                            help='Show version information')
        parser.add_argument('-a', metavar='ACTION',
                            default='server',
                            choices=['server', 'test', 'update'],
                            help='One of server, test, update (server)')
        parser.add_argument('-c', metavar='CONFIGFILE',
                            default='/etc/https-proxy.cfg',
                            help='Configuration file (/etc/https-proxy.cfg)'),
        parser.add_argument('-r', metavar='RULES',
                            default=argparse.SUPPRESS,
                            help='Rules directory (%s)' %
                            (self.config_defaults['rules'][0]))
        parser.add_argument('-d', metavar='DATABASE',
                            default=argparse.SUPPRESS,
                            help='SQLite database location (%s)' %
                            (self.config_defaults['database'][0]))
        parser.add_argument('-D', metavar='DATABASE_PERSIST',
                            default=argparse.SUPPRESS,
                            help='Persistent SQLite database location (%s) ' %
                            (self.config_defaults['database_persist'][0]))
        parser.add_argument('-l', metavar='LISTEN',
                            default=argparse.SUPPRESS,
                            help='Address and port to listen on (%s)' %
                            (self.config_defaults['listen'][0]))
        self.args = parser.parse_args()

    def get(self, option):
        config_file_value = self._configfile.get('section', option)

        if self.config_defaults[option][1] is None:
            argument_value = config_file_value
        else:
            argument_value = getattr(self.args,
                                     self.config_defaults[option][1],
                                     config_file_value)

        return argument_value

    def __getitem__(self, item):
        return self.get(item)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

logFormatter = logging.Formatter("%(asctime)s [%(name)15s:%(levelname)-5.5s] %(message)s")
consoleHandler.setFormatter(logFormatter)

Configuration = ProxyConfiguration()
