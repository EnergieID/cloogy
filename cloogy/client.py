from functools import wraps
import requests
import datetime as dt

from .unit import Unit
from .tag import Tag

__title__ = "cloogy"
__version__ = "0.0.1"
__author__ = "EnergieID.be"
__license__ = "MIT"

URL = 'https://api.cloogy.com/api/1.4/'


class NotAuthenticatedError(Exception):
    pass


def authenticated(func):
    """
    Decorator to check if the token has expired.
    If it has, use the refresh token to request a new token
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        if self.refresh_token is not None and self.token_expiration_time <= dt.datetime.utcnow():
            self.re_authenticate()
        if not self.token:
            raise NotAuthenticatedError("Please authenticate first")
        return func(*args, **kwargs)
    return wrapper


class CloogyClient:
    def __init__(self, login=None, password=None):
        self.token = None
        self.refresh_token = None
        self.token_expiration_time = None

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

        if login and password:
            self.authenticate(login=login, password=password)

    def authenticate(self, login, password):
        """
        Uses login and password to request a token,
        refresh token and expiry date.

        Parameters
        ----------
        login : str
        password : str

        Returns
        -------
        Nothing
            token is saved in self.token
            refresh token is saved in self.refresh_token
            expiration time is set in self.token_expiration_time as
            datetime.datetime
        """
        url = URL + 'sessions'
        body = {
            'Login': login,
            'Password': password
        }
        r = self.session.post(url=url, json=body)
        r.raise_for_status()

        j = r.json()
        self.token = j['Token']
        self.refresh_token = j['RefreshToken']
        self._set_token_expiration_time(expires_in=j['Timeout'])

    def _set_token_expiration_time(self, expires_in):
        """
        Saves the token expiration time by adding the 'expires in' parameter
        to the current datetime (in utc).

        Parameters
        ----------
        expires_in : int
            number of seconds from the time of the request until expiration

        Returns
        -------
        Nothing
            saves expiration time in self.token_expiration_time as
            datetime.datetime
        """
        self.token_expiration_time = dt.datetime.utcnow() + \
                                     dt.timedelta(0, expires_in)  # timedelta(days, seconds)

    def re_authenticate(self):
        """
        Uses the refresh token to request a new token, refresh token and
        expiration date.

        Returns
        -------
        Nothing
            token is saved in self.token
            refresh token is saved in self.refresh_token
            expiration time is set in self.token_expiration_time as
            datetime.datetime
        """
        url = URL + 'session/refresh'
        params = {
            'token': self.token,
            'refresh_token': self.refresh_token
        }
        r = self.session.put(url=url, params=params)
        r.raise_for_status()

        j = r.json()
        self.token = j['Token']
        self.refresh_token = j['RefreshToken']
        self._set_token_expiration_time(expires_in=j['Timeout'])

    @authenticated
    def get_units(self, include=None, where=None, order=None):
        """
        Query the API for a list of units

        Parameters
        ----------
        include : str
        where : str
        order : str

        Returns
        -------
        [Unit]
        """
        url = URL + 'units'
        headers = {'Authorization': 'ISA ' + self.token}
        params = {}
        if include:
            params.update({'Include': include})
        if where:
            params.update({'Where': where})
        if order:
            params.update({'Order': order})
        r = self.session.get(url=url, headers=headers, params=params)
        r.raise_for_status()
        j = r.json()
        units = [Unit(attributes=d, client=self) for d in j['List']]
        return units

    def get_unit(self, unit_id):
        """
        Query the API for a specific Unit

        Parameters
        ----------
        unit_id : int

        Returns
        -------
        Unit
        """
        where = "Id=" + str(unit_id)
        units = self.get_units(where=where)
        unit = units[0]
        return unit

    @authenticated
    def get_tags(self, include=None, where=None, order=None):
        """
        Query the API for a list of tags

        Parameters
        ----------
        include : str
        where : str
        order : str

        Returns
        -------
        [Tag]
        """
        url = URL + 'tags'
        headers = {'Authorization': 'ISA ' + self.token}
        params = {}
        if include:
            params.update({'Include': include})
        if where:
            params.update({'Where': where})
        if order:
            params.update({'Order': order})
        r = self.session.get(url=url, headers=headers, params=params)
        r.raise_for_status()
        j = r.json()
        tags = [Tag(attributes=d, client=self) for d in j['List']]
        return tags

    def get_tag(self, tag_id):
        """
        Query the API for a specific Tag

        Parameters
        ----------
        tag_id : int

        Returns
        -------
        Tag
        """
        where = "Id=" + str(tag_id)
        tags = self.get_tags(where=where)
        tag = tags[0]
        return tag

    def get_consumptions(self, granularity, tags, start, end, instants_type=None):
        """
        Parameters
        ----------
        granularity : str
            Instant, Hourly, Daily, Monthly, Yearly
        tags : [str]
        start : int
            epochms
        end : int
            epochms
        instants_type : str
            Avg, Max, Min, Stdev

        Returns
        -------
        dict
        """
        url = URL + 'consumptions/' + granularity
        headers = {'Authorization': 'ISA ' + self.token}
        params = {
            'from': int(start),
            'to': int(end),
            'tags': str(tags)
        }
        if instants_type:
            params.update({'instantsType': instants_type})
        r = self.session.get(url=url, headers=headers, params=params)
        r.raise_for_status()
        return r.json()

    def get_consumptions_dataframe(self, granularity, tags, start, end, instants_type=None):
        """
        Get consumptions and parse them into a flat DataFrame

        Parameters
        ----------
        granularity : str
            Instant, Hourly, Daily, Monthly, Yearly
        tags : [str]
        start : pd.Timestamp
        end : pd.Timestamp
        instants_type : str
            Avg, Max, Min, Stdev

        Returns
        -------
        pd.DataFrame
        """
        import pandas as pd
        cons = self.get_consumptions(
            granularity=granularity,
            tags=tags,
            start=int(start.timestamp() * 1000),
            end=int(end.timestamp() * 1000),
            instants_type=instants_type
        )
        df = pd.DataFrame.from_records(cons)
        df.Date = pd.to_datetime(df.Date, unit='ms', utc=True)
        return df

    def get_readings_dataframe(self, granularity, tags, start, end, instants_type=None, metric='Read', rename_tags=True):
        """
        Get a useful DataFrame for a specific metric (default is "Read")
        with a DatetimeIndex and a column per Tag.
        Also renames the columns to the Tag names.

        Parameters
        ----------
        granularity : str
            Instant, Hourly, Daily, Monthly, Yearly
        tags : [str]
        start : pd.Timestamp
        end : pd.Timestamp
        instants_type : str
            Avg, Max, Min, Stdev
        metric : str
        rename_tags : bool

        Returns
        -------
        pd.DataFrame
        """
        df = self.get_consumptions_dataframe(
            granularity=granularity,
            tags=tags,
            start=start,
            end=end,
            instants_type=instants_type
        )
        df.set_index(['TagId', 'Date'], inplace=True)
        df = df[metric].unstack().T
        df.index.name = None
        df.columns.name = None

        df.sort_index(inplace=True)

        if rename_tags:
            tag_objs = self.get_tags(where='Id in {}'.format(tags))
            tag_names = {tag['Id']: tag['Name'] for tag in tag_objs}
            df.rename(columns=tag_names, inplace=True)

        return df
