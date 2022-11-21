#TASK 1

'''
Inner Join
It matches the common ids from both tables based on which it is joined.
Basically only returns matching rows

Left Join
It returns all the rows of left table and only returns matching rows of right table

Right Join
It returns all the rows of right table and only returns matching rows of left table

Other Join
Returns all the rows of both table. Including the matching one

'''


#TASK 2

import pandas as pd
import pandasql as ps
flights = pd.read_csv("candidateEvalData/flights.csv")
airports = pd.read_csv("candidateEvalData/airports.csv")
weather = pd.read_csv("candidateEvalData/weather.csv")
airlines = pd.read_csv("candidateEvalData/airlines.csv")

p_sql = ps.sqldf("SELECT f.origin, count(f.flight) as count_flights FROM flights f LEFT JOIN airlines a ON f.carrier = a.carrier WHERE a.name like '%JetBlue%' GROUP BY 1 HAVING count_flights > 10000 ORDER BY count_flights ASC")

# p_sql_1 = ps.sqldf('SELECT f.*, a.name as airline_name FROM flights f LEFT JOIN airlines a ON f.carrier	= a.carrier')
# p_sql_2 = ps.sqldf("SELECT * FROM p_sql_1 ps where ps.airline_name like '%JetBlue%'")
# p_sql_3 = ps.sqldf("SELECT origin, count(flight) as count_flights FROM p_sql_2 GROUP BY 1 ORDER BY count_flights ASC")
# p_sql_4 = ps.sqldf("SELECT * FROM p_sql_3 GROUP BY 1 HAVING count_flights > 10000 ORDER BY count_flights ASC")

print(p_sql)