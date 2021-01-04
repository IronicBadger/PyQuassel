from quassel import *
import re
import base64
import http.client, urllib

conn = http.client.HTTPSConnection("api.pushover.net:443")
pushNotification = None

def onMessageReceived(bot, message):
    global pushNotification
    sendNotification = False

    if getattr(bot.config, 'pushoverAppToken', None) is None:
        return
    
    if message['type'] == Message.Type.Plain or message['type'] == Message.Type.Action:
        # Token match
        keywords = bot.config.pushIfKeyword
        pattern = r'\b(' + '|'.join(keywords) + r')\b'
        if re.search(pattern, message['content'], flags=re.IGNORECASE):
            sendNotification = True

        # Is Highlight
        if message['flags'] & Message.Flag.Highlight:
            sendNotification = True

        if message['bufferInfo']['type'] == BufferInfo.Type.QueryBuffer:
            sendNotification = True

    if message['flags'] & Message.Flag.Self:
        sendNotification = False

    if sendNotification:
        print(message)
        #if pushNotification is None:

            # from pushnotification import PushOverNotification
            # pushNotification = PushBulletNotification(bot.config.pushbulletAccessToken)
            # if bot.config.pushbulletDeviceName:
            #     device = pushNotification.get_device(nickname=bot.config.pushbulletDeviceName)
            #     pushNotification.device = device

        data = {}
        if 'webapp' in bot.config.enabledPlugins:
            data['type'] = 'link'
            data['url'] = '{}#buffer-{}'.format(*[
                bot.config.webappUrl,
                message['bufferInfo']['id'],
            ])

        conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": bot.config.pushoverAppToken,
            "user": bot.config.pushoverUserToken,
            #"message": message
            "message": (
                message['bufferInfo']['name'],
                message['sender'].split('!')[0],
                message['content']
                ),
        }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
        conn.close()

        print("end")