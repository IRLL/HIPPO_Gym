class InfoPanel:
    def __init__(self, queue, text=None, items=None, kv=None):
        self.queue = queue
        self.text = text if type(text) == str else None
        self.items = items if type(items) == list else None
        self.kv = kv if type(kv) == list else None

    def send(self):
        info_panel = {'InfoPanel': None}
        if self.text or self.items or self.kv:
            info_panel = {'InfoPanel': {
                'text': self.text,
                'items': self.items,
                'kv': self.kv
            }}
        self.queue.put_nowait(info_panel)

    def add_item(self, item):
        self.items.append(item)
        return self.items

    def reset_items(self):
        self.items = None

    def add_kv(self, kv):
        self.kv.append(kv)
        return self.kv

    def reset_kv(self):
        self.kv = None

    def reset_text(self):
        self.text = None

    def reset(self):
        self.text = None
        self.items = None
        self.kv = None
        self.send()

    def update(self, text=None, items=None, kv=None):
        if text and type(text) == str:
            self.text = text
        if items and type(items) == list:
            self.items = items
        if kv and type(kv) == list:
            self.kv = kv
        self.send()
