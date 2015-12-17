## Blocks
- [Reduce](#reduce)
- [ReduceStream](#reducestream)

# Reduce

Computes some arithmetic information about groups of signals.

This block can be passed a list of signals and it will output aggregate information about one of the attributes (or something more complex) about the signals. The aggregate information currently output is the sum, average, count, minimum, and maximum. Since the output is numeric, it will require the value to be operated on to also be numeric. Non-numeric values will be ignored.

Additionally, the *value* property can be configured to output a list of numbers instead of a single number. In this case, that list of numbers will be iterated over just like a list of signals.

**Example:**

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

Properties
---------

-   **Reduce Input Value**: (expression) The value for each signal to use in the computations
-   **Group By**: (expression) What to group the signals by. A different output signal will be produced for each group

Dependencies
------------
None

Commands
--------
None

Input
-----
Any list of signals.

Output
------
One signal per group, containing the following attributes:

- sum
- count
- average
- min
- max
- group


# ReduceStream

Similar to the Reduce block, but instead works on streams of data and notifies average stats on a regular interval.

Where the Reduce block will notify an aggregate signal for an incoming list, the ReduceStream block will notify aggregate signals periodically regardless if a signal came through or not. It is expected to take in streams of signals and maintain the same stats as Reduce over time.

The block operates in a "trailing" manner, meaning that if you configure the block to maintain information for 5 minutes, it will always represent the trailing 5 minutes, not 5 minute buckets.

The block will maintain one Stats object for every list of signals that it receives. Once a stats object is outside of the averaging interval, it will be deleted and deallocated. Because there is only one stats object for an incoming list, it can sometimes be a performance enhancement to put a Buffer block before the ReduceStream block. Sending 5 individual signals to this block will cause 5 objects to be created; sending a list of those same 5 signals will result in the same calculation to occur but only one object will be created.

Stats objects are optionally persisted across block/service restarts.

Properties
---------

-   **Reduce Input Value**: (expression) The value for each signal to use in the computations
-   **Group By**: (expression) What to group the signals by. A different output signal will be produced for each group
-   **Averaging Interval**: (timedelta) What period of time to compute the averages/min/max/etc for. This is a "trailing" field, so setting it to 24 hours will always notify information about the **trailing** 24 hours.
-   **Reporting Interval**: (timedelta) How often to notify signals from this block. Note that signals are not notified based on incoming signals, but rather this interval.

Dependencies
------------
None

Commands
--------
None

Input
-----
Any list of signals.

Output
------
One signal per group every reporting interval period, containing the following attributes:

- sum
- count
- average
- min
- max
- group
