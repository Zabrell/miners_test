import requests, smtplib, time, os
# Добавляем необходимые подклассы - MIME-типы
from email.mime.multipart import MIMEMultipart      # Многокомпонентный объект
from email.mime.text import MIMEText                # Текст/HTML
def write2file(filename, text):
  x = open(filename, 'w')
  x.write(text)
  x.close()
try: hosts = open('hosts.txt', 'r').read().split()
except:
  write2file('hosts.txt', input('Список хостов и хешрейты(через пробел): ').lower())
  hosts = open('hosts.txt', 'r').read().split()
treshold = {}#'acer': 40, 'acer1': 40, 'acer2': 40, 'asus': 35, 'msi': 36, 'mainhm': 35
for i in range(len(hosts)):
  if i%2 == 0: treshold[hosts[i]] = int(hosts[i+1])
try: host = open('host.txt', 'r').read()
except: host = str(input('Имя хоста: ')).lower()
write2file('host.txt', host)
if host not in list(treshold.keys()):
  treshold[host] = int(input('Минимальный хешрейт: '))
  write2file('hosts.txt', open('hosts.txt', 'r').read()+' '+host+' '+str(treshold[host]))
try: endpoint = open('endpoint.txt', 'r').read()
except:
  endpoint = str(input('Адрес API кошелька: '))
  write2file('endpoint.txt', endpoint)
write2file('restarts.txt', '1')
while 1:
  r = requests.get(endpoint).json()
  rep = {}
  offline = []
  problems = []
  for i in r['workers']: rep[i.lower()] = int(r['workers'][i]['rhr'] / 1000000)
  if sorted(list(rep.keys())) != sorted(list(treshold.keys())):
    for w in treshold.keys():
      if w not in rep.keys():
        offline.append(w)
  for i in r['workers']:
    if r['workers'][i]['offline'] == True: offline.append(i)
  for w in rep:
    if rep[w] <= treshold[w]:
      problems.append(w)

  print(f'{time.strftime("%H:%M:%S %d.%m.%Y", time.localtime())} Скрипт в работе: {rep}')
  if ((host in problems) or (host in offline)) and open('restarts.txt', 'r').read() == '0':

    addr_from = "zabrell@bk.ru"                 # Адресат
    addr_to   = "zabrell@bk.ru"                   # Получатель
    password  = ""                                  # Пароль

    msg = MIMEMultipart()                               # Создаем сообщение
    msg['From']    = addr_from                          # Адресат
    msg['To']      = addr_to                            # Получатель
    msg['Subject'] = f'Вокреры оффлайн: {offline}, проблемы на: {problems}'                   # Тема сообщения
    body = str(rep) + f'\n {host} был перезагружен'
    msg.attach(MIMEText(body, 'plain'))                 # Добавляем в сообщение текст
    server = smtplib.SMTP_SSL('smtp.mail.ru', 465, '1')      # Создаем объект SMTP
    server.login(addr_from, password)                   # Получаем доступ
    server.send_message(msg)                            # Отправляем сообщение
    server.quit()                                       # Выходим
    if host != 'asus':
      os.system("shutdown /r /t 30")
      if str(input('Отменить перезагрузку? ')).lower() in ['да','+','y','yes']:
        os.system('shutdown /a')
  else:
    write2file('restarts.txt', '0')
  time.sleep(15*60)

