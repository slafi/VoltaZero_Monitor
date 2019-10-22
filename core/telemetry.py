from common import utils


class Telemetry():

    """This is a conceptual class representation of a telemetry record.

        :param timestamp: telemetry timestamp, defaults to None
        :param t0: onboard temperature sensor value, defaults to None
        :param t1: external temperature sensor value, defaults to None
        :param th: thermocouple value, defaults to None
        :param bz: buzzer state value, defaults to None
        :param ls: light sensor value, defaults to None
        :param ir: infrared sensor value, defaults to None
        :param id: instance identifier, defaults to None
    """

    def __init__(self, timestamp=None, t0=None, t1=None, th=None, bz=None, ls=None, ir=None, id=None):

        """Initializes the Telemetry instance

        :param timestamp: telemetry timestamp, defaults to None
        :param t0: onboard temperature sensor value, defaults to None
        :param t1: external temperature sensor value, defaults to None
        :param th: thermocouple value, defaults to None
        :param bz: buzzer state value, defaults to None
        :param ls: light sensor value, defaults to None
        :param ir: infrared sensor value, defaults to None
        :param id: instance identifier, defaults to None
        """

        if timestamp is None:
            self.timestamp = utils.get_unix_timestamp()
        else:
            self.timestamp = timestamp

        self.t0 = t0
        self.t1 = t1
        self.th = th
        self.bz = bz
        self.ls = ls
        self.ir = ir
        self.id = id


    def __repr__(self):

        """Represents the Telemetry instance as a string

        :return: string representation
        """

        return f"{self.id} @ {self.timestamp} => (t0: {self.t0}, t1: {self.t1}, " \
               f"th: {self.th}, ls: {self.ls}, ir: {self.ir}, bz: {self.bz})"
