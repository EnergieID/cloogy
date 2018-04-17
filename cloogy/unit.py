class Unit(dict):
    def __init__(self, attributes, client=None):
        """
        Parameters
        ----------
        client : CloogyClient
        attributes : dict
        """
        super(Unit, self).__init__(attributes)
        self._client = client

    def get_last_communication_date(self):
        """
        Get the date and time for the units last communication

        Returns
        -------
        pd.Timestamp
        """
        import pandas as pd
        epochms = self.get('LastComm')
        timestamp = pd.to_datetime(epochms, unit='ms', utc=True)
        return timestamp

    def get_tags(self, include=None, where="", order=None):
        if where != "":
            where = where + '+'
        where = where + "UnitId=" + str(self.get('Id'))

        tags = self._client.get_tags(include=include, where=where, order=order)
        return tags
