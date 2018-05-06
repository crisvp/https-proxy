import ConfigParser
import StringIO


class ProxyConfiguration:
    def __init__(self, config_file='https-proxy.cfg'):
        config_defaults = {
            'rules': './https-everywhere/rules',
            'database': '/dev/shm/https-proxy.sqlite',
            'database_persist': '/var/lib/https-proxy.sqlite',
            'rule_extensions': '.xml,.XML'
        }
        self._config = ConfigParser.SafeConfigParser(config_defaults,
                                                     allow_no_value=True)
        with open(config_file, 'r') as f:
            config_string = '[section]\n' + f.read()

        fp = StringIO.StringIO(config_string)
        self._config.readfp(fp)

    def get(self, option):
        return self._config.get('section', option)
