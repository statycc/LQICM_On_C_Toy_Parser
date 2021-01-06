# Loop Quasi-Invariant Chunk Motion

This is a pass which computes the invariance degree of each statement
in loops and inner loops in a way to peel them.

With a relation composition, it is able to hoist an entire invariant or
quasi-invariant inner loop.

## Prerequisites 

This uses the [pycparser](https://github.com/eliben/pycparser).

## Installation 

Install [pycparser](https://github.com/eliben/pycparser).

Run on examples:

    $ python LQICM.py yourfile.c

Example:

    $ python LQICM.py c_files/example2.c

Remark:

The `.c` file given needs to contain only functions (no
`includes` or other macros etc…)

## Testing

To run unit tests locally run:

```text
python LQICM.py
``` 

There will be no output if all tests pass.

For verbose test output run

```text
python -m doctest -v test_examples.txt
```
