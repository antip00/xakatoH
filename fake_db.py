from itertools import product
import pandas as pd

dates = ["2022-05-%02d" % i for i in range(1, 31)]

# https://codegolf.stackexchange.com/questions/49728/list-all-times-in-the-day-at-a-half-hour-rate
periods = ["'%02d:%s0'" % (h / 2, h % 2 * 3) for h in range(20, 38)]

df = pd.DataFrame(list(product(range(4), dates, periods, [None])), columns=["room_name", "date", "time_id", "user"])
df.to_pickle("db.pkl")
