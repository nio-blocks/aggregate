Aggregate
=========
The Aggregate block takes an attribute from the incoming signal and emits a signal containing the attribute's average, count, max, min, and sum.  The attribute should be a list of numbers.

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
- **groups**: Returns a list of the block’s current signal groupings.

AggregateStream
===============
The AggregateStream block calculates the same statistics as the [Aggregate](https://blocks.n.io/Aggregate) block, but rather than using a single signal's list, it uses an attribute that is a number and calculates the stats over the configured **averaging interval**.

Properties
----------
- **averaging_interval**: What period of time to compute the averages/count/min/max/sum for. This is a 'trailing' field, so setting it to 24 hours will always notify information about the *trailing* 24 hours.
- **backup_interval**: An interval of time that specifies how often persisted data is saved.
- **group_by**: The signal attribute on the incoming signal whose values will be used to define groups on the outgoing signal.
- **load_from_persistence**: If `True`, the block’s state will be saved when the block is stopped, and reloaded once the block is restarted.
- **report_interval**: How often to emit signals from this block. Note that signals are not emitted based on incoming signals, but rather this time interval.
- **value**: The value for each signal to use in the computations.

Inputs
------
- **default**: Any list of signals with numeric values.

Outputs
-------
- **default**: The computed sum, average, count, minimum, and maximum for the incoming data stream over the specified interval.

Commands
--------
- **groups**: Returns a list of the block’s current signal groupings.

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

