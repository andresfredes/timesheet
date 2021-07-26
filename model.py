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

import os
from PyQt5.QtCore import QAbstractTableModel, Qt
import numpy as np

from config import DATA_DIR, COLUMN_HEADERS

class JSON_Model(QAbstractTableModel):
    def __init__(self):
        super(JSON_Model, self).__init__()
        self._data = np.array([[1,2,3,4,5],[4,5,6,7,8],[7,8,9,10,11]])
        try:
            os.mkdir(DATA_DIR)
        except FileExistsError:
            pass

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return str(self._data[index.row(), index.column()])

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return COLUMN_HEADERS[section]