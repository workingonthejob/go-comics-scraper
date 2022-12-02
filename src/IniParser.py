import configparser


class IniParser():

    def __init__(self, config):
        self.config_parser = configparser.ConfigParser()
        self.config_file = config
        self.config_parser.read(self.config_file)

    def get_properties(self, header, property):
        value = self.config_parser[header][property]
        values = value.split(",")
        return [val.strip() for val in values]

    def get_reddit_properties(self, property):
        properties = self.get_properties("Reddit", property)
        length = len(properties)
        return properties if length > 1 else properties[0]

    def get_gocomics_properties(self, property):
        properties = self.get_properties("GoComicsScraper", property)
        return properties

    def save_changes(self):
        with open(self.config_file, 'w') as file:
            self.config_parser.write(file)

    def update_property(self, property, value):
        self.config_parser["GoComicsScraper"][property] = str(value)


if __name__ == "__main__":
    cp = IniParser('config.ini')
    print(username)
    # cp.update_property("TEST", "Foo")
    # cp.save_changes()
