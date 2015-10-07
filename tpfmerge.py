#!/usr/bin/python2

"""
tpfmerge - Merge your TPF availability plans

Copyright (C) Konrad Talik <konrad.talik@slimak.matinf.uj.edu.pl>

tpfmerge is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

tpfmerge is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with tpfmerge.  If not, see <http://www.gnu.org/licenses/>.
"""

import csv
import os
import re

HOUR_RE = re.compile(r"^\d\d:\d\d$")

BASE_VALUE = 0

VALUE_RATINGS = {
    'x': -1,
    '.': 0,
    'e': 0.1,
    'v': 1
}


def readplan(plan):
    """Read plan file to a rows array"""
    rows = []
    with open(plan, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ')
        rows = [row[4:] for row in reader]

    # Pop empty lines
    i = 0
    while i < len(rows):
        if rows[i] == []:
            rows.pop(i)
        i += 1

    # Pop the header and any additional info
    while rows[0] != []:
        rows.pop(0)

    # Pop empty lines
    i = 0
    while i < len(rows):
        if rows[i] == []:
            rows.pop(i)
        i += 1

    return rows


def availdict(planrows, templaterows):
    """Avialability dictionary"""
    # We need first column of values for validation
    keys, t_values = templaterows[0], templaterows[1:]
    p_values = planrows[1:]
    t_hours = [v[0] for v in t_values if HOUR_RE.match(v[0])]

    p_avail = dict()
    for row in p_values:
        hour = row[0]
        if hour in t_hours:
            p_avail[hour] = row[1:]

    return p_avail


def merge(availdictlist, ratings):
    result = dict()

    for hour in availdictlist[0].keys():
        if not hour in result:
            result[hour] = [BASE_VALUE] * len(availdictlist[0][hour])
        for avail in availdictlist:
            a = map(float, result[hour])
            b = map(float, [ratings.get(v, ratings['x']) for v in avail[hour]])
            result[hour] = [a[i] + b[i] for i in xrange(len(a))]

    return result


if __name__ == '__main__':
    files = [f for f in os.listdir('.') if '.tpf' in f]
    template = files[0]
    t_rows = readplan(template)
    header = t_rows[0]
    avails = [availdict(readplan(f), t_rows) for f in files]
    merged = merge(avails, VALUE_RATINGS)

    print 'Merge result'
    print '============'
    print ''
    print (' ' * 4) + '     '.join(header)
    for key in sorted(merged.keys()):
        print (' ' * 4) + key, \
        reduce(lambda x,y: str(x).rjust(5) + ' ' + str(y).rjust(5), merged[key])
