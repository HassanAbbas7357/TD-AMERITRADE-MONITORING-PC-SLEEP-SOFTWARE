from cmath import log
import json
import ctypes
from logging import exception
from time import sleep
import datetime
import os
import subprocess
from tda import auth, client
import tda
import winsound
freq = 500
dur = 200
import gspread

# import sys
# import os
# os.chdir(sys._MEIPASS)

def logg(x):
    logstring = f'\n[{datetime.datetime.now()}] - {x}'
    print(logstring)
    if not os.path.exists("logs.txt"):
        with open('logs.txt', 'w+') as f:
            f.write(logstring)

    else:
        with open('logs.txt', 'a+') as f:
            f.write(logstring)



softwareLicense = "f91bc959f50fbcab585680ed533dbcd6a06a2c3f0d624602ef310d1d5741245c4b520b86d4066a881f1e55fcaac72922c007a13eb2c4d4794c77e8ccd902e745"

google_sheet_token = {}


gc = gspread.service_account_from_dict(google_sheet_token)

shh = gc.open_by_url(
    'https://docs.google.com/spreadsheets/d/1gHojHfCqPgIQz9Qn2UabO5GWVfO1ltP-g6OHXFMOJVk/edit#gid=0')
worksheet = shh.sheet1

licenses = worksheet.col_values(2)


token_path = os.getcwd()+'/token.json'
api_key = 'MRGOHERINKVAXE7NNCASFFWLOPGIDMIN@AMER.OAUTHAP'
redirect_uri = 'http://localhost'
try:
    c = auth.client_from_token_file(token_path, api_key)
except FileNotFoundError:
    logg("TOKEN FIle Not Found")
    for i in range(13):
        winsound.Beep(freq, dur)

    input()


COMPLETED_TRADES = []
TRANSACTION_IDS = []
SYMBOLS_DATA = {}  # Dictionary OF ALL BOUGHT SYMBOLS DATA
SYMBOLS_DATA_SHORT = {}  # Dictionary OF ALL BOUGHT SYMBOLS DATA IN SHORT
appRestartStatus = 0


def fillOrUpdate_SymbolsData(data):
    for trade in data:
        transactionID = trade['orderId']
        if transactionID in TRANSACTION_IDS:
            continue

        try:
            symbol = trade['orderLegCollection'][0]['instrument']['symbol']
            amount = trade['orderLegCollection'][0]['quantity']
            cost = trade['orderActivityCollection'][0]['executionLegs'][0]['price'] * \
                trade['orderLegCollection'][0]['quantity']
            #cost = abs(cost)
        except:
            continue

        if trade['orderLegCollection'][0]['instruction'] == "BUY":
            TRANSACTION_IDS.append(transactionID)
            if symbol in SYMBOLS_DATA:
                old_data = SYMBOLS_DATA[symbol]
                old_data['amount_shares'] = old_data['amount_shares'] + amount
                old_data['cost_buy'] = old_data['cost_buy'] + cost
                SYMBOLS_DATA[symbol] = old_data

            else:
                SYMBOLS_DATA[symbol] = {
                    'symbol': symbol,
                    'amount_shares': amount,
                    'cost_buy': cost,
                    'recieved_sell': 0,
                    'profit_loss': 0,
                    'completed_trades': 0
                }

        elif trade['orderLegCollection'][0]['instruction'] == "SELL":
            TRANSACTION_IDS.append(transactionID)
            if symbol in SYMBOLS_DATA:
                old_data = SYMBOLS_DATA[symbol]
                old_data['amount_shares'] = old_data['amount_shares'] - amount
                old_data['recieved_sell'] = old_data['recieved_sell'] + cost
                old_data['profit_loss'] = old_data['recieved_sell'] - \
                    old_data['cost_buy']
                SYMBOLS_DATA[symbol] = old_data

                if SYMBOLS_DATA[symbol]['amount_shares'] == 0:
                    status = None
                    newData = SYMBOLS_DATA[symbol]
                    newData['completed_trades'] = newData['completed_trades'] + 1
                    newData['recieved_sell'] = 0
                    newData['cost_buy'] = 0

                    if SYMBOLS_DATA[symbol]['profit_loss'] < 0:
                        status = 'loss'
                    else:
                        status = 'win'
                    COMPLETED_TRADES.append(status)
                    newData['profit_loss'] = 0
                    SYMBOLS_DATA[symbol] = newData


def fillOrUpdate_SymbolsData_SHORT(data):
    for trade in data:
        transactionID = trade['orderId']
        if transactionID in TRANSACTION_IDS:
            continue

        try:
            symbol = trade['orderLegCollection'][0]['instrument']['symbol']
            amount = trade['orderLegCollection'][0]['quantity']
            cost = trade['orderActivityCollection'][0]['executionLegs'][0]['price'] * \
                trade['orderLegCollection'][0]['quantity']
            #cost = abs(cost)
        except:
            continue

        if trade['orderLegCollection'][0]['instruction'] == "SELL_SHORT":
            TRANSACTION_IDS.append(transactionID)
            if symbol in SYMBOLS_DATA_SHORT:
                old_data = SYMBOLS_DATA_SHORT[symbol]
                old_data['amount_shares'] = old_data['amount_shares'] + amount
                old_data['cost_buy'] = old_data['cost_buy'] + cost
                SYMBOLS_DATA_SHORT[symbol] = old_data

            else:
                SYMBOLS_DATA_SHORT[symbol] = {
                    'symbol': symbol,
                    'amount_shares': amount,
                    'cost_buy': cost,
                    'recieved_sell': 0,
                    'profit_loss': 0,
                    'completed_trades': 0
                }

        elif trade['orderLegCollection'][0]['instruction'] == "BUY_TO_COVER":
            TRANSACTION_IDS.append(transactionID)
            if symbol in SYMBOLS_DATA_SHORT:
                old_data = SYMBOLS_DATA_SHORT[symbol]
                old_data['amount_shares'] = old_data['amount_shares'] - amount
                old_data['recieved_sell'] = old_data['recieved_sell'] + cost
                old_data['profit_loss'] = old_data['cost_buy'] - \
                    old_data['recieved_sell']
                SYMBOLS_DATA_SHORT[symbol] = old_data

                if SYMBOLS_DATA_SHORT[symbol]['amount_shares'] == 0:
                    status = None
                    newData = SYMBOLS_DATA_SHORT[symbol]
                    newData['completed_trades'] = newData['completed_trades'] + 1
                    newData['recieved_sell'] = 0
                    newData['cost_buy'] = 0

                    if SYMBOLS_DATA_SHORT[symbol]['profit_loss'] < 0:
                        status = 'loss'
                    else:
                        status = 'win'
                    COMPLETED_TRADES.append(status)
                    newData['profit_loss'] = 0
                    SYMBOLS_DATA_SHORT[symbol] = newData


def dump_sleepTime():

    def getSleepTime():
        now = datetime.datetime.now()
        now_plus_10 = now + datetime.timedelta(minutes=1)
        return now_plus_10

    def myconverter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    with open('time.json', 'w') as outfile:
        json.dump({'time': getSleepTime()}, outfile, default=myconverter)


def initTime():
    def myconverter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    with open('time.json', 'w') as outfile:
        json.dump({'time': datetime.datetime.now()},
                  outfile, default=myconverter)


def checkTime():
    with open('time.json', 'r') as f:
        data_time = json.load(f)
    old_time = datetime.datetime.strptime(
        data_time['time'], '%Y-%m-%d %H:%M:%S.%f')
    now = datetime.datetime.now()
    if now > old_time:
        return True
    else:
        return False


def checkPCLOCKED():
    process_name = 'LogonUI.exe'
    callall = 'TASKLIST'
    outputall = subprocess.check_output(callall)
    outputstringall = str(outputall)
    if process_name in outputstringall:
        return True
    else:
        return False




def forceLOCK():
    while True:
        t = checkTime()
        if t is True:
            logg("LOCK TIME IS OVER")
            break
        else:
            pcINFO = checkPCLOCKED()
            if pcINFO is False:
                logg("PC is Locking Again focefully")
                ctypes.windll.user32.LockWorkStation()


def getLossCounts():
    actualLoss = 0
    loss = 0
    for trade in COMPLETED_TRADES:
        if loss >= 2:
            actualLoss += 1

        if trade == 'loss':
            loss += 1
        else:
            loss = 0

    if loss >= 2:
        actualLoss += 1

    if actualLoss > 0:
        return True
    else:
        return False


def putPC_on_Sleep():
    global COMPLETED_TRADES
    count = getLossCounts()
    if count == True:
        logg(f"Putting PC on Sleep {COMPLETED_TRADES}")
        COMPLETED_TRADES = []
        dump_sleepTime()
        ctypes.windll.user32.LockWorkStation()
        forceLOCK()


def getTodayTime():
    dates = str(datetime.date.today())+' 00:00:00'
    fromdate = datetime.datetime.strptime(dates, '%Y-%m-%d %H:%M:%S')

    datess = str(datetime.date.today())+' 23:59:00'
    toDate = datetime.datetime.strptime(datess, '%Y-%m-%d %H:%M:%S')

    return fromdate, toDate


if not softwareLicense in licenses:
    logg("Your software license has been expired")
    for i in range(13):
        winsound.Beep(freq, dur)
    quit()


def setScriptData():
    global COMPLETED_TRADES, TRANSACTION_IDS, SYMBOLS_DATA, SYMBOLS_DATA_SHORT
    dat = {
        "COMPLETED_TRADES": COMPLETED_TRADES,
        "TRANSACTION_IDS": TRANSACTION_IDS,
        "SYMBOLS_DATA": SYMBOLS_DATA,
        "SYMBOLS_DATA_SHORT": SYMBOLS_DATA_SHORT}
    print("setting data ", dat)
    with open('scriptData.json', 'w') as outfile:
        json.dump({
            "COMPLETED_TRADES": COMPLETED_TRADES,
            "TRANSACTION_IDS": TRANSACTION_IDS,
            "SYMBOLS_DATA": SYMBOLS_DATA,
            "SYMBOLS_DATA_SHORT": SYMBOLS_DATA_SHORT}, outfile)


def getScriptData():
    global COMPLETED_TRADES, TRANSACTION_IDS, SYMBOLS_DATA, SYMBOLS_DATA_SHORT

    with open('scriptData.json', 'r') as outfile:
        data = json.load(outfile)

    COMPLETED_TRADES = data["COMPLETED_TRADES"]
    TRANSACTION_IDS = data["TRANSACTION_IDS"]
    SYMBOLS_DATA = data["SYMBOLS_DATA"]
    SYMBOLS_DATA_SHORT = data["SYMBOLS_DATA_SHORT"]


def main():
    global appRestartStatus, COMPLETED_TRADES, TRANSACTION_IDS, SYMBOLS_DATA, SYMBOLS_DATA_SHORT
    print(COMPLETED_TRADES, TRANSACTION_IDS, SYMBOLS_DATA, SYMBOLS_DATA_SHORT)
    if not os.path.exists("time.json"):
        initTime()

    if not os.path.exists("scriptData.json"):
        setScriptData()

    if appRestartStatus == 0:
        logg("App was restarted getting data from Json file")
        appRestartStatus = 1
        if os.path.exists("scriptData.json"):
            getScriptData()
        else:
            setScriptData()

    forceLOCK()

    w = c.get_orders_by_path(account_id=238967723, from_entered_datetime=getTodayTime()[
                             0], to_entered_datetime=getTodayTime()[1], status=tda.client.Client.Order.Status.FILLED)
    logg(
        f'Hit API Date Parameters - From ~ {getTodayTime()[0]} - TO ~ {getTodayTime()[1]}')
    data_files = w.json()

    # print(data_files)
    if data_files == []:
        logg("Setting Data to scriptData.json file")
        setScriptData()
        logg(
            f"No Records Found Today - length of API Data is {len(data_files)}")
        return None

    data_file = data_files[::-1]

    logg("Setting New Data to scriptData.json file")
    setScriptData()

    try:
        fillOrUpdate_SymbolsData(data_file)
        fillOrUpdate_SymbolsData_SHORT(data_file)

        logg(
            f'\t\t\t\t------------------         BUY SELL TRADES          ---------\n\n {SYMBOLS_DATA}\n\n')
        logg(
            f'\t\t\t\t------------------      BUY SELL SHORT TRADES       ---------\n\n {SYMBOLS_DATA_SHORT}\n\n')
        logg(
            f'\t\t\t\t------------------         COMPLETED TRADES        ---------\n\n {COMPLETED_TRADES}\n\n')
        putPC_on_Sleep()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    while True:
        main()
        sleep(10)
