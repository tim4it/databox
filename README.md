# Description
Extract data from `SiStat` and push metrics to `databox`.

Data comes from three sources, fourth source is calculated from previous ones. 

All four sources are pushed to `databox` as metrics with units.

# Running
Paython >3.10 is used. Run data pusher using `databox` python API:
```shell
python3 databox_main.py
```

# Testing

Run all the tests that starts with **test**:

```shell
python3 -m unittest discover
```

Run single test:
```shell
python3 -m unittest discover -s test -p 'test_response.py'
```
```shell
python3 -m unittest discover -s test -p 'test_*'
```
```shell
python3 -m unittest discover -s test -p '*helper.py'
```

Email address using for `databox` app:

`sasostor@gmail.com`

Dashboard:

https://app.databox.com/datawall/e297a4f03a6b722781e33ed3ecfc92235bb2380675a1e7a

TODO: 
timing - pool or event based
memory with queuing + batches
standard error
jwt token handling
