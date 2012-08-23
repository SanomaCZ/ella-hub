class PublishableLocked(Exception):
    def init(self, lock):
        super(PublishableLocked, self).__init__(unicode(lock))
        self.lock = lock
