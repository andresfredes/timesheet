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

from config import DATA_DIR

class Timesheet():
    def __init__():
        try:
            os.mkdir(DATA_DIR)
        except FileExistsError:
            pass
        