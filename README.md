# How to Use
Navigate to the folder holding your txt file of propositions you want to test. Run either `python logictables2.py <filename>`, or with `--monitor` if you would like it to check for changes and re-emit the latex.
Then just copy your latex into a latex thing of choice.

To format a proposition file, make each line its own logical expression (see the contents of the source file for all valid symbols), and then use a === to seperate conclusions from premises. An example is below
```
H <-> M
M ^ -H
===
E
```
