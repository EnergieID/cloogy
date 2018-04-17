class Tag(dict):
    def __init__(self, attributes, client=None):
        """
        Parameters
        ----------
        client : CloogyClient
        attributes : dict
        """
        super(Tag, self).__init__(attributes)
        self._client = client

    def get_last_communication_date(self):
        """
        Get the date and time for the units last communication

        Returns
        -------
        pd.Timestamp
        """
        import pandas as pd
        epochms = self.get('LastCommunication')
        timestamp = pd.to_datetime(epochms, unit='ms', utc=True)
        return timestamp
