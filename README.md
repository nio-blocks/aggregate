Aggregate
=========
Computes some arithmetic information about groups of signals.

Properties
----------
- **group_by**: Attribute to group signals by. A different output signal will be produced for each group.
- **value**: The value for each signal to use in the computations.

Inputs
------
- **default**: Any list of signals with numeric values.

Outputs
-------
- **default**: The computed sum, average, count, minimum, and maximum for the list of values specified.

Commands
--------
- **groups**: Displays the current groupings of signals.

***

AggregateStream
===============
Computes some arithmetic information about a streams of data and notifies the computations on an interval basis.

Properties
----------
- **averaging_interval**: What period of time to compute the averages/min/max/etc for. This is a 'trailing' field, so setting it to 24 hours will always notify information about the **trailing** 24 hours.
- **backup_interval**: Period at which stream states are backed up to disk using persistance.
- **group_by**: Attribute to group signals by. A different output signal will be produced for each group.
- **load_from_persistence**: If true, the previous state of the stream/interval is loaded upon block restart.
- **report_interval**: How often to notify signals from this block. Note that signals are not notified based on incoming signals, but rather this interval.
- **value**: The value for each signal to use in the computations.

Inputs
------
- **default**: Any list of signals with numeric values.

Outputs
-------
- **default**: The computed sum, average, count, minimum, and maximum for the incoming data stream over the specified interval.

Commands
--------
- **groups**: Displays the current groupings of signals.

***

Reduce
======
DEPRECATED, USE Aggregate INSTEAD - Computes some arithmetic information about groups of signals.

Properties
----------
- **group_by**: Attribute to group signals by. A different output signal will be produced for each group.
- **value**: The value for each signal to use in the computations.

Inputs
------
- **default**: Any list of signals with numeric values.

Outputs
-------
- **default**: The computed sum, average, count, minimum, and maximum for the list of values specified.

Commands
--------
- **groups**: Displays the current groupings of signals.

Dependencies
------------
None

***

ReduceStream
============
DEPRECATED, USE AggregateStream INSTEAD - Computes some arithmetic information about a streams of data and notifies the computations on an interval basis.

Properties
----------
- **averaging_interval**: What period of time to compute the averages/min/max/etc for. This is a 'trailing' field, so setting it to 24 hours will always notify information about the **trailing** 24 hours.
- **backup_interval**: Period at which stream states are backed up to disk using persistance.
- **group_by**: Attribute to group signals by. A different output signal will be produced for each group.
- **load_from_persistence**: If true, the previous state of the stream/interval is loaded upon block restart.
- **report_interval**: How often to notify signals from this block. Note that signals are not notified based on incoming signals, but rather this interval.
- **value**: The value for each signal to use in the computations.

Inputs
------
- **default**: Any list of signals with numeric values.

Outputs
-------
- **default**: The computed sum, average, count, minimum, and maximum for the incoming data stream over the specified interval.

Commands
--------
- **groups**: Displays the current groupings of signals.

Dependencies
------------
None

Example
-------
_Block Config_:
```python
value : {{ len($my_list) }}
```
_Signals Input_:
```python
{ "my_list": ['A', 'B', 'C'] },
{ "my_list": ['D', 'B'] },
{ "my_list": ['E'] },
```
_Signal Output_:
```python
{
    "sum": 6,
    "average": 2.0,
    "count": 3,
    "min": 1,
    "max": 3
}
```

