# Aani

Aani is a simple and lightweight documentation framework for project
directories as they typically appear in scientific environments. 
It integrates readme.md files from all subdirectories and module level comments
from python scripts into one documentation.html file.

It automatically ignores all files and directories which's name start with a
dot, and all files in your .gitignore

For an example look at the
[html](https://htmlpreview.github.io/?https://github.com/knorrfg/aani/main/test_dir/documentation.html) in test_dir.
To get started simply create a readme.md and run `aani` in the top level
directory of your project.

To install Aani simply run
```
   pip install git+git://github.com/knorrfg/aani.git
```
