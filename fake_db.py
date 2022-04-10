from itertools import product
import pandas as pd

# names = map(str, range(4))
# dates = ["2022-04-%02d" % i for i in range(1, 31)]
# # https://codegolf.stackexchange.com/questions/49728/list-all-times-in-the-day-at-a-half-hour-rate
# periods = ["%02d:%s0" % (h / 2, h % 2 * 3) for h in range(20, 38)]

names = ["0"]
dates = ["2022-04-10"]
periods = ["09:00"]

df = pd.DataFrame(list(product(names, dates, periods, [None], [None], [None])), 
        columns=["room_name", "date", "time_id", "user", "service_col", "service_time"])
df["service_time"] = pd.to_datetime(df["service_time"])

df.to_pickle("db.pkl")
