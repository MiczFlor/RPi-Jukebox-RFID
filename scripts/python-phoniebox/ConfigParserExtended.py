# from configparser import RawConfigParser
import configparser


class ConfigParserExtended(configparser.ConfigParser):

    def as_dict(self, section="all"):
        if section == "all":
            d = self.__dict__['_sections']
        else:
            d = self.__dict__['_sections'][section]
        return d

    def as_json(self, section="all"):
        import json
        if section == "all":
            d = self.__dict__['_sections']
        else:
            d = self.__dict__['_sections'][section]
        return json.dumps(d, separators=(',', ':'), indent=4, sort_keys=True,
                            ensure_ascii=False).encode('utf8')

    def print_ini(self, section="all"):
        if section == "all":
            sections = self.sections()
        else:
            sections = [section]
        for section_name in sections:
            print("[{}]".format(section_name))
            for key, value in self.items(section_name):
                print('{} = {}'.format(key, value))
