# Cloogy
Python client for Cloogy

## See Demo.ipynb for a working Jupyter Notebook


# 0. Install cloogy

In your terminal: `pip3 install cloogy`

or in a python shell or notebook:

```python
import pip
pip.main(['install', 'cloogy'])
```


```python
import yaml

from cloogy import CloogyClient
```

# 1. Get your credentials

Get your login and password.

In this example we'll load it from a YAML file.


```python
with open('credentials.yaml', 'r') as f:
    credentials = yaml.load(f)
```


```python
login = credentials['login']
password = credentials['password']
```

# 2. Create a CloogyClient

If you supply a login and password, authentication will be handled for you.


```python
client = CloogyClient(login=login, password=password)
```

# 3. List your Units


```python
units = client.get_units()
```


```python
units
```

# 4. Get a specific Unit by ID


```python
# Lets grab the first ID from the list above
unit_id = units[0]['Id']
print(unit_id)
```


```python
unit = client.get_unit(unit_id=unit_id)
```


```python
unit
```

# 5. Find out some stuff about your unit

The `Unit` class is an extension to the regular python dict. This means it behaves like a normal dict, but adds some extra features.


```python
# Get date and time of the last communication
unit.get_last_communication_date()
```

# 6. List all available Tags for your login


```python
client.get_tags()
```

# 7. List available Tags for a Unit


```python
tags = unit.get_tags()
```


```python
tags
```


```python
[tag['Id'] for tag in tags]
```

# 8. Get a specific Tag directly


```python
tag_id = tags[0]['Id']
print(tag_id)
```


```python
tag = client.get_tag(tag_id=tag_id)
```


```python
tag
```


```python
tag.get_last_communication_date()
```

# 9. Get consumptions


```python
# pick a start and end time, as POSIX timestamp

import pandas as pd
start = int(pd.Timestamp('20180414').timestamp() * 1000)
end = int(pd.Timestamp('20180416').timestamp() * 1000)
print(start, end)
```


```python
client.get_consumptions(
    granularity='hourly', # can be Instant, Hourly, Daily, Monthly, Yearly
    start=start,
    end=end,
    tags=[tag_id], # List of tag Id's
    instants_type=None  # How instant measurements should be aggregated. Can be Avg, Max, Min, Stdev. Default is Avg.
)
```

# 10. Get consumptions as a DataFrame

For some easy analysis, methods to get data as a Pandas DataFrame are included

Let's say we want to analyse the active energy consumption, which has TagTypeId 20001


```python
tags = client.get_tags(where='TagTypeId=20001')
tag_ids = [tag['Id'] for tag in tags]

start = pd.Timestamp('20180101')
end = pd.Timestamp('20180417')
```


```python
client.get_consumptions_dataframe(granularity='monthly', start=start, end=end, tags=tag_ids)
```

A flat table like this is nice, but it can contain multiple TagIds, and it has way to many columns we don't need.

We can also get a table for only the readings:


```python
df = client.get_readings_dataframe(granularity='monthly', start=start, end=end, tags=tag_ids, metric='Read')
```


```python
df
```


```python
# make a plot!

%matplotlib inline
df.plot.bar()
```
