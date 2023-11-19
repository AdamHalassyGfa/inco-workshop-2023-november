
import os
import numpy
import matplotlib.pyplot as plot

from lib.data_util import open_schema, query_data

DB_FILE = os.path.abspath('data.db')


def draw_histogram(ax, data):
    s = list(map(lambda d: d[1], data))
    q = numpy.quantile(s, [.25, .75])
    i = (q[1] - q[0]) * 1.5
    lo = q[0] - i
    hi = q[1] + i

    s = list(filter(lambda x: lo <= x <= hi, s))

    ax.hist(s)


def draw_boxplot(ax, data):
    s = list(map(lambda d: d[1], data))

    # Remove the infamous 'Hutton Orbital' station (and 2 other outliers):
    s = list(filter(lambda x: x < 70000, s))
    # Note: this is above a wrong solution, for boxplot we should have ALL the data

    ax.boxplot(s)


if __name__ == '__main__':
    conn = open_schema(DB_FILE)
    data = query_data(conn, "SELECT name, distance FROM Stations;", [])

    fig, ax = plot.subplots(1, 2)

    draw_histogram(ax[0], data)
    draw_boxplot(ax[1], data)

    plot.show()

# eof