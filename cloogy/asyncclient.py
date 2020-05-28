from typing import Dict

import aiohttp
import pandas as pd

from .client import CloogyClient


class AsyncCloogyClient(CloogyClient):
    def __init__(self, token: str, session: aiohttp.ClientSession):
        super(AsyncCloogyClient, self).__init__()
        self.token = token
        self.session = session

    async def get_readings_dataframe(self, granularity, tags, start, end, instants_type=None, metric='Read', rename_tags=False) -> pd.DataFrame:
        if rename_tags is True:
            raise NotImplementedError('No async implementation for renaming tags yet')

        df = await self.get_consumptions_dataframe(
            granularity=granularity,
            tags=tags,
            start=start,
            end=end,
            instants_type=instants_type
        )

        df = self._format_readings_dataframe(df, metric=metric, rename_tags=rename_tags, tags=tags)

        return df

    async def get_consumptions_dataframe(self, granularity, tags, start, end, instants_type=None) -> pd.DataFrame:
        cons = await self.get_consumptions(
            granularity=granularity,
            tags=tags,
            start=int(start.timestamp() * 1000),
            end=int(end.timestamp() * 1000),
            instants_type=instants_type
        )
        df = self._parse_consumptions_to_dataframe(cons=cons)
        return df

    async def get_consumptions(self, granularity, tags, start, end, instants_type=None) -> Dict:
        arguments = self._get_consumptions_arguments(
            granularity=granularity,
            start=start,
            end=end,
            tags=tags,
            instants_type=instants_type
        )
        arguments['headers'].update(self._headers)
        async with self.session.get(**arguments) as r:
            r.raise_for_status()
            return await r.json()
