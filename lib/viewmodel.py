class Item(object):
    def __init__(self, raw, value, anchor):
        self.raw = raw
        self.value = value
        self.anchor = anchor


class ColumnTemplate(object):
    def __init__(self, name, path=None, format=lambda x: x, anchor_link=None):
        self.name = name
        self.path = name if path is None else path
        self.format = format
        self.anchor_link = anchor_link

    def to_item(self, json):
        # TODO: resolve paths
        value = json[self.path]
        fmt_val = self.format(value)
        anchor = None
        if self.anchor_link:
            anchor = self.anchor_link.format(value)
        return Item(value, fmt_val, anchor)


class TableTemplate(object):
    def __init__(self, columns):
        self.columns = columns


class Table(object):
    def __init__(self, template, json):
        self.template = template
        self.json = json

    def headers(self):
        return [c.name for c in self.template.columns]

    def rows(self):
        return [[c.to_item(item) for c in self.template.columns] for item in self.json]
