# Copyright 2021, Andres Fredes, <andres.hector.fredes@gmail.com>
# 
# This file is part of timesheet.
# 
#     timesheet is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     timesheet is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with timesheet.  If not, see <https://www.gnu.org/licenses/>.

"""Timesheet: task/project time keeping program.

model.py hosts the SQLITE3 / QtSql database model and any related classes
"""

import os, sqlite3
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtCore import Qt
from datetime import datetime as dt
from datetime import timedelta as delta

from config import DATA_DIR, DB_FILENAME, COLUMN_NAMES


class Model(QSqlTableModel):
    """Model subclasses PyQt5's QSqlTableModel for ease of use with PyQt5's
    views to display the database information. It is intended for use in a
    model/view architecture as per Qt standards.
    Database access is primarily managed using SQLITE3.

    Args:
        database (QSqlDatabase): Database to connect to and model. 
            This should be passed in by the hosting view.
    """
    def __init__(self, database):
        super().__init__(db=database)
        try:
            os.mkdir(DATA_DIR)
        except FileExistsError:
            pass
        self._connect()
        self.db.execute(
            'create table if not exists timesheet'
            '(id integer primary key, '
            'task text, '
            'project text, '
            'notes text, '
            'time_in timestamp, '
            'time_out timestamp)'
        )
        self.setTable('timesheet')
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.select()
        self.db_cols = {}
        for index, name in enumerate(COLUMN_NAMES):
            self.db_cols[name] = index
            self.setHeaderData(index, Qt.Horizontal, name)
        self.submitAll()



    def _connect(self):
        self.db = sqlite3.connect(
            DATA_DIR + DB_FILENAME,
            detect_types=(sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        )
        self.db.row_factory = sqlite3.Row



    def close(self):
        """Safely close database before exiting.
        """
        self.db.close()



    def add(self, task, project, notes):
        """Adds a record into the database consisting of the provided parameters
        and the additional defaults (id, time_in).

        Uses datetime.min as a placeholder to represent an ongoing task.
        This is referred to internally with the var 'active'.

        On submission of the record, QSqlTableModel automatically triggers the
        dataChanged() event, notifying the host view of the change.

        Args:
            task (str): User entered/chosen 'task' value
            project (str): User entered/chosen 'project' value
            notes (str): User entered 'notes' value
        """
        now = dt.now()
        active = dt.min
        with self.db:
            self.db.execute(
                'insert into timesheet'
                '(task, project, notes, time_in, time_out) '
                'values (?, ?, ?, ?, ?)',
                (task, project, notes, now, active)
            )
        self.submitAll()



    def set_time_out(self, notes):
        """Finalises the currently active record, by substituting the
        placeholder 'active' (datetime.min) with the current time.

        On submission of the record, QSqlTableModel automatically triggers the
        dataChanged() event, notifying the host view of the change.

        Args:
            notes (str): User updated 'notes' value - this will overwrite any
                existing notes.
        """
        now = dt.now()
        active = dt.min
        with self.db:
            self.db.execute(
                'update timesheet '
                'set notes=(?), time_out=(?) '
                'where time_out=(?)',
                (notes, now, active)
            )
        self.submitAll()



    def tasks_projects(self):
        """Queries the database and returns sorted lists of all tasks and
        projects respectively.

        Returns:
            (tuple): tuple containing:
                - tasks(list): all tasks, alpha-sorted
                - projects(list): all projects, alpha-sorted
        """
        tasks = set()
        projects = set()
        for row in self.db.execute(
            'select all task, project from timesheet'
        ):
            if row:
                tasks.add(row['task'])
                projects.add(row['project'])
        return sorted(tasks), sorted(projects)



    def current_task_project(self):
        """Queries the database and returns the details within the 'current'
        record as denoted by the placeholder of time_out == datetime.min.

        Returns:
            (tuple): tuple containing the below, or None:
                - task(str): task name
                - project(str): project name
                - notes(str): notes
                - time_in(str): time of clock in, in human-readable format
        """
        active = dt.min
        cursor = self.db.execute(
            'select all task, project, notes, time_in from timesheet '
            'where time_out=(?)',
            (active, )
        )
        current_row = cursor.fetchone()
        format = "%A  %d/%m/%y  %H:%M"
        if current_row:
            return (
                current_row['task'],
                current_row['project'],
                current_row['notes'],
                current_row['time_in'].strftime(format)
            )
        else:
            return None



    def most_recent(self):
        """Queries the database and returns the most recent record, which may
        or may not be currently active.

        Raises:
            Empty_DB_Exception: In case of fresh install or deleted records.

        Returns:
            (tuple): tuple containing:
                - task(str): task name
                - project(str): project name
        """
        cursor = self.db.execute(
            'select all task, project from timesheet '
            'order by id desc '
        )
        recent = cursor.fetchone()
        if not recent:
            raise Empty_DB_Exception()
        return (recent['task'], recent['project'])



    def get_total_time(self, item_type, item_name):
        """Provides total time elapsed for the chosen task or project (as
        defined by parameters).

        Args:
            item_type (str): column to search (task or project)
            item_name (str): keyword to search within column

        Returns:
            (tuple): tuple containing:
                - total(datetime.timedelta): total time elapsed
                - week_total(datetime.timedelta): time elapsed for this week
        """
        cursor = self.db.execute(
            'select all time_in, time_out from timesheet '
            'where ?=(?)',
            (item_type, item_name)
        )
        matching_rows = cursor.fetchall()
        total = delta(microseconds=1)
        week_total = delta(microseconds=1)
        for row in matching_rows:
            in_time = row['time_in']
            out_time = row['time_out']
            if out == dt.min:
                out = dt.now()
            total += (out_time - in_time)
            week_total += self._time_in_week(in_time, out_time)
        return (total, week_total)



    def _time_in_week(in_time, out_time):
        now = dt.now()
        now_time = now.time()
        week_start = now - delta(
            days=now.weekday(),
            hours=now_time.hour,
            minutes=now_time.minute,
            seconds=now_time.second,
            microseconds=now_time.microsecond
        )
        if week_start < out_time:
            if week_start < in_time:
                diff = out_time - in_time
            else:
                diff = out_time - week_start
        else:
            diff = delta(microseconds=1)
        return diff



    def flags(self, index):
        """Overloaded QSqlTableModel function to ensure that the view is
        read-only.

        For Qt internal model/view processing only.

        Args:
            index (QModelIndex): index object of selected element

        Returns:
            (enum): Qt values
        """
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable



    def data(self, index, role):
        """Overloaded QSqlTableModel function to allow a Qt view correct access
        to the model's contained data.

        For Qt internal model/view processing only.

        Args:
            index (QModelIndex): index object of selected element
            role (enum): Qt values representing the type of interaction that the
                view or delegate is intending to have.

        Returns:
            (QVariant): The record, or None if invalid or not for display.
        """
        if role == Qt.DisplayRole:
            record = QSqlTableModel.data(self, index, role)
            if record:
                if index.column() in [4, 5]:
                    if "0001" in record:
                        return "Running..."
                    format = "%Y-%m-%d %H:%M:%S.%f"
                    time = dt.strptime(record, format)
                    out_format = "%H:%M  %d/%m/%y"
                    record = time.strftime(out_format)
                return record
        return None
    

class Database(QSqlDatabase):
    """The SQLITE database with defined path/name.

    Args:
        filename (str): the path/filename of the database to access/create.
    """
    def __init__(self, filename):
        super().__init__('QSQLITE')
        self.setDatabaseName(filename)


class Empty_DB_Exception(Exception):
    """Subclassed exception, for clarity of code.
    No additional functionality.
    """
    pass