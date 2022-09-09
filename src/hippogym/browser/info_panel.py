class InfoPanel:
    def __init__(self, queue, text=None, items=[], kv=[]):
        self.queue = queue
        self.text = text if type(text) == str else None
        self.items = items if type(items) == list else []
        self.kv = kv if type(kv) == dict else {}

    def send(self):
        info_panel = {"InfoPanel": None}
        if self.text or len(self.items) != 0 or len(self.kv) != 0:
            info_panel = {
                "InfoPanel": {"text": self.text, "items": self.items, "kv": self.kv}
            }
        self.queue.put_nowait(info_panel)

    def add_item(self, item):
        self.items.append(item)
        return self.items

    def reset_items(self):
        self.items = []

    def update_kv(self, key, value):
        self.kv[key] = value
        return self.kv

    def get_kv(self):
        return self.kv

    def reset_kv(self):
        self.kv = {}

    def reset_text(self):
        self.text = None

    def reset(self):
        self.reset_text()
        self.reset_items()
        self.reset_kv()
        self.send()

    def update(self, text=None, items=None, kv=None):
        if text and type(text) == str:
            self.text = text
        if type(items) == list:
            self.items = items
        if type(kv) == dict:
            self.kv = kv
        self.send()
