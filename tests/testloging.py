import logging

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


class Pizza:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.InfoLogger = setup_logger("InfoLogger", "info.log", level=logging.INFO)
        self.DebugLogger = setup_logger("DebugLoger", "info.log", level=logging.DEBUG)

        self.InfoLogger.info("Pizza created: {} (${})".format(self.name, self.price))

    def make(self, quantity=1):
        self.DebugLogger.debug("Made {} {} pizza(s)".format(quantity, self.name))

    def eat(self, quantity=1):
        self.InfoLogger.info("Ate {} pizza(s)".format(quantity, self.name))


pizza_01 = Pizza("Sicilian", 18)
pizza_01.make(5)
pizza_01.eat(4)

pizza_02 = Pizza("quattro formaggi", 16)
pizza_02.make(2)
pizza_02.eat(2)
