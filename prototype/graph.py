#!/usr/bin/python3

from lib.storage_util import open_schema, query_data

import matplotlib.pyplot as plt
import os
import numpy

DATA_FILE = os.path.abspath("data/elite-market-p1.db")
COMMODITY = 'Jaroua Rice'

QUERY_PRICE_STATS = """
    with d as (SELECT 
            commodity_id, 
            min(buy_price) as min_buy_price, 
            max(buy_price) as max_buy_price, 
            avg(buy_price) as avg_buy_price,
            min(sell_price) as min_sell_price, 
            max(sell_price) as max_sell_price, 
            avg(sell_price) as avg_sell_price
        FROM Prices p
        GROUP BY p.commodity_id
        ) 
        select 
            name,
            min_buy_price, 
            max_buy_price, 
            avg_buy_price,
            min_sell_price, 
            max_sell_price, 
            avg_sell_price
            from d
            inner join Commodities c
                on c.id = d.commodity_id
            order by c.name
    """

QUERY_COMMODITY_STATS = """
    select
        s.dst_sol,
        s.dst_star,
        p.sell_price,
        p.buy_price
    
        from Commodities c
        inner join prices p
            on p.commodity_id = c.id
        inner join Stations s
            on s.id = p.station_id
            
        where c.name = ?
"""


def filter_outliers(data):
    x = numpy.quantile(data, [.25, .75])
    i = (x[1] - x[0]) * 1.5
    l = x[0] - i
    h = x[1] + i

    return list(filter(lambda x: l < x < h, data))


def get_outlier_borders(data):
    x = numpy.quantile(data, [.25, .75])
    i = (x[1] - x[0]) * 1.5
    l = x[0] - i
    h = x[1] + i

    return l, h


def lorenz_curve(plt, data):
    data = numpy.asarray(data)
    x_lorenz = data.cumsum() / data.sum()
    x_lorenz = numpy.insert(x_lorenz, 0, 0)
    plt.scatter(
        numpy.arange(x_lorenz.size) / (x_lorenz.size - 1),
        x_lorenz,
        color='darkgreen',
        s=1)

    plt.plot([0, 1], [0, 1], color='k')
    plt.set_title("Lorenz curve")


def dst_vs_price(plt, data):
    x = []
    y = []
    data = sorted(data, key=lambda x: x[3])
    for dst_sol, dst_star, p_sell, p_buy in data:
        if dst_star is not None and p_sell is not None:
            x.append(dst_star)
            y.append(p_sell)

    x_lo, x_hi = get_outlier_borders(x)

    x_filtered = []
    y_filtered = []
    for i in range(0, len(x)):
        x_ok = x_lo <= x[i] <= x_hi
        if x_ok:
            x_filtered.append(x[i])
            y_filtered.append(y[i])

    plt.scatter(x_filtered, y_filtered, s=3)
    plt.set_title("Sell price by distance from central star")


if __name__ == '__main__':
    print("Query data... ", end='')
    conn = open_schema(DATA_FILE)
    price_data = query_data(conn, QUERY_PRICE_STATS, [])
    commodity_data = query_data(conn, QUERY_COMMODITY_STATS, [COMMODITY])
    print("done.")

    avg_sell = []
    avg_buy = []
    min_buy = []
    max_buy = []
    for name, min_buy_price, max_buy_price, avg_buy_price, min_sell_price, max_sell_price, avg_sell_price in price_data:
        if avg_sell_price is not None:
            avg_sell.append(avg_sell_price)

    avg_sell_filtered = filter_outliers(avg_sell)

    fig, ax = plt.subplots(2, 2)

    ax[0, 0].hist(avg_sell_filtered)
    ax[0, 0].set_title("Histogram of average sell price")

    ax[0, 1].boxplot(avg_sell)
    ax[0, 1].set_title("Boxplot of average sell price")

    dst_vs_price(ax[1, 0], commodity_data)
    lorenz_curve(ax[1, 1], avg_sell_filtered)

    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    plt.show()

# eof
