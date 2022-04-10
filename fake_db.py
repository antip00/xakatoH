from itertools import product
import pandas as pd

names = ["Отрицание", "Гнев", "Торг", "Депрессия", "Смирения"]
dates = ["2022-04-%02d" % i for i in range(1, 35)]
# https://codegolf.stackexchange.com/questions/49728/list-all-times-in-the-day-at-a-half-hour-rate
periods = ["%02d:%s0" % (h / 2, h % 2 * 3) for h in range(20, 40)]

# names = ["0"]
# dates = ["2022-04-10"]
# periods = ["10:00"]

df = pd.DataFrame(list(product(names, dates, periods, [None], [None], [None])), 
        columns=["room_name", "date", "time_id", "user", "service_col", "service_time"])
df["service_time"] = pd.to_datetime(df["service_time"])

# print(df.sort_values("time_id"))
df.to_pickle("db.pkl")
