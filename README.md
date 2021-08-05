timesheet
=========

Description
-----------
Records time of clocking in and out, along with task for given time period.
Also allows viewing and editing of previous timesheets.

Documentation
-------------
Refer to docs/build/html/index.html

Usage
-----
`python timesheet.py`
Will start the GUI

Files
-----
## config.py
Definition of configuration variables and constants

## custom_widgets.py
The definition of all custom classes based on PyQT5 widgets.

## gui.py
The main Graphical User interface code and core logic for the program as a whole.

## model.py
The business logic of the program that interacts with time-taking and data storage

## README.md
This file.

## requirements.txt
list of required python packages to run program

## timesheet.py
The main run file to start the GUI.

Requirements
------------
Python 3.8+
Packages listed in requirements.txt

License
-------
Copyright 2021, Andres Fredes, <andres.hector.fredes@gmail.com>

This file is part of timesheet.
 
    timesheet is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    timesheet is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with timesheet.  If not, see <https://www.gnu.org/licenses/>.