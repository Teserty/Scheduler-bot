from urllib.parse import urlencode
import os, datetime, time, json, requests, sys
import pandas as pd
mouths = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь",
          "Декабрь"]

LATE_TIME=os.environ.get('LATE_TIME')
MORNING_TIME=os.environ.get('MORNING_TIME')


def get_file(file_name: str):
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    public_key = os.environ.get('API_KEY')
    final_url = base_url + urlencode(dict(public_key=public_key))
    response = requests.get(final_url)
    download_url = response.json()['href']
    download_response = requests.get(download_url)
    with open(file_name, 'wb') as f:
        f.write(download_response.content)


def get_next_monitor(today_m: int, today_d: int):
    dfs = pd.read_excel("downloaded_file.xlsx", sheet_name=os.environ.get('SHEET_NAME'))
    fromi, toi = 0, 0
    print(today_m, today_d)
    for i in range(dfs.size):
        try:
            if str(dfs.iat[i, 2]) in mouths[today_m - 1]:
                fromi = i
            if str(dfs.iat[i, 2]) in mouths[today_m]:
                toi = i
        except:
            pass
    d = {}
    for i in range(fromi, toi):
        try:
            if len(dfs.iat[i, 1].split(" "))==2:
                d[dfs.iat[i, 1]] = dfs.iat[i, today_d+1]
        except:
            pass
    return d


def get_data(shift: int = 1):
    td = datetime.date.today() + datetime.timedelta(days=shift)
    today_m = int(td.strftime("%m"))
    today_d = int(td.strftime("%d"))
    return get_next_monitor(today_m, today_d)


def sendMessage(text):
    headers = {
        'Authorization': os.environ.get('AUTH_TOKEN'),
        'Content-Type': 'application/json'}
    data = {
        'chat_id': os.environ.get('CHAT_ID'),
        'text': text
    }
    print('Chat_Id: ', data["chat_id"])
    resp = requests.post(url='https://botapi.messenger.yandex.net/bot/v1/messages/sendText/',
                         data=json.dumps(data),
                         headers=headers)
    sys.stdout.write('Sended\n')
    sys.stdout.write(f'{resp.text}\n')


def getTextToday():
    text = '```ES.TEAM Daily today\n{}```️\n'.format(datetime.date.today().strftime("%d.%m"))
    monitors = []
    input_data = get_data(0)
    for i in input_data:
        if input_data[i] == 'м':
            monitors.append(i)
    text+="⏰️Мониторящий сегодня: 🍀**{}**🍀\n".format(", ".join(monitors))
    sys.stdout.write(f'{text}\n')
    return text


def getTextNextDay():
    next_day = datetime.date.today() + datetime.timedelta(days=1)
    text = '```ES.TEAM Daily tomorrow\n{}```️\n'.format(next_day.strftime("%d.%m"))
    monitors = []
    input_data = get_data(1)
    for i in input_data:
        if input_data[i] == 'м':
            monitors.append(i)
    text += "⏰️Мониторящий завтра: 🍀**{}**🍀".format(", ".join(monitors))
    sys.stdout.write(f'{text}\n')
    return text


sys.stdout.write('Started\n')
while 1:
    try:
        dt = datetime.datetime.utcnow().strftime("%H:%M")
        if dt == LATE_TIME:
            sys.stdout.write(f'{dt} \n')
            get_file("downloaded_file.xlsx")
            time.sleep(6000)
            sendMessage(getTextNextDay())
        elif dt == MORNING_TIME:
            sys.stdout.write(f'{dt} \n')
            get_file("downloaded_file.xlsx")
            sendMessage(getTextToday())
            time.sleep(6000)
    except Exception as e:
        sys.stdout.write(f'!!!\n{e} \n')
    time.sleep(30)
