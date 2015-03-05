Reduce
======

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

-   **value**: (expression) The value for each signal to use in the computations
-   **group_by**: (expression) What to group the signals by. A different output signal will be produced for each group

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
