class Logger:
    active_loggers = []
    loggers = []
    activated = False
    __slots__ = ["name", "spacing", "active"]

    def __init__(self, name):
        self.name = name
        Logger.loggers.append(self)

    @staticmethod
    def activate():
        for logger in Logger.loggers:
            logger.spacing = ' ' * (max(0, max(map(lambda x: len(x), Logger.active_loggers)) - len(logger.name)) + 1)
            logger.active = logger.name in Logger.active_loggers
        Logger.activated = True

    @staticmethod
    def activate_loggers(*loggers):
        Logger.active_loggers.extend(loggers)

    def log(self, text):
        if not Logger.activated:
            return
        if not self.active:
            return
        print(self.name + ':' + self.spacing + text)
