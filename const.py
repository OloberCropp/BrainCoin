API_TOKEN2 = '570906577:AAEAXQvzcQceBm58FQ7eXG2zrD5Zbh6T2Uk'
API_TOKEN = '689716948:AAEWhKvnGb6EkYFS8OCWIqATM0Pr-UaTDHA'

TRADE_TOKEN = 'BHs4Roojirevfg8QbMtJR67LEGkSmgls'
BOT_GET_WALLET = 'http://195.123.216.184:20246/api/getnum'
BOT_CHECK_PAY = "http://195.123.216.184:20246/api/checkpay"
BOT_PAY_OUT = "http://195.123.216.184:20246/api/outqiwi"

seconds = 8
bet = 25
map_25 = []
map_50 = []
map_100 = []
map_200 = []
map_free = []

users_time = {}
pay_req = {}
last_sended_message = {}
# user_id : [link battle, pay/non-pay]
battle_array = {}
in_game = {}
count_questions = 5


time = "Время на ответ: {}\n\n"
theme = "Первая тема - {}\nВторая тема - {}\nТретья тема - {}"
end_str = "{}\n\nКоличество очков у вас - {}\nКоличество очков у соперника - {}\n\n{}"
win = "Вы выиграли."
lose = "Вы проиграли."
ne_vam_ne_nam = "Победила дружба!"


# webhook settings

WEBHOOK_HOST = '142.93.100.13'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '142.93.100.13'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)