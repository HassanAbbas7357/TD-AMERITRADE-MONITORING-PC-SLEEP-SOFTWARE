from tda import auth, client
import json
import os
from datetime import datetime, timedelta,date
import tda

token_path = os.getcwd()+'/token.json'
api_key = ''
redirect_uri = 'http://localhost'
try:
    c = auth.client_from_token_file(token_path, api_key)
except FileNotFoundError:
    print("FIle Not Found")

# r = c.get_account(238967723)
# # assert r.status_code == 200, r.raise_for_status()
# print(json.dumps(r.json(), indent=4))

print("----------------------------------")
today = datetime.today()
yesterday = today - timedelta(days=1)
hoursss = today-timedelta(hours=10)
ten = today - timedelta(9)

def getTodayTime():
    dates = str(date.today())+' 00:00:00'
    fromdate = datetime.strptime(dates,'%Y-%m-%d %H:%M:%S')

    dates = str(date.today())+' 23:59:00'
    toDate = datetime.strptime(dates,'%Y-%m-%d %H:%M:%S')

    return fromdate,toDate


w = c.get_orders_by_path(account_id= 238967723, from_entered_datetime=getTodayTime()[0], to_entered_datetime=getTodayTime()[1],status=tda.client.Client.Order.Status.FILLED)
print(json.dumps(w.json(), indent=4))
with open('output.json', 'w') as outfile:
    json.dump(w.json(), outfile)