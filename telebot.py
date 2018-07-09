from telethon import TelegramClient
import time
import random
from telethon.errors import PeerFloodError
# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
result = {}
path="settings"
with open(path, 'r', encoding='utf-8') as file:
    for line in file:
        value_pair = line.split('=')
        left = value_pair[0].strip()
        right = value_pair[1].strip()
        if right.isnumeric():
            result[left] = int(right)
        else:
            result[left] = right
print(result)

api_id = result['api_id'] 
api_hash = result['api_hash'] 

client = TelegramClient('session_name', api_id, api_hash)
client.start()
print("Connected to client.")
# Client message initialized
message1 = result['message1']
message2 = result['message2']
message3 = message1 + "\n" + message2

count = 0

with open("contacts.csv") as f:
    lines1 = f.readlines()
    num_lines = len([l for l in lines1])
    f.close()

with open("contacts.csv") as fileobject:
    for line in fileobject:
        try:
            print('Sending message to '+line)
            time.sleep(random.randint(0,1))
            client.send_message(line, message3)
        except PeerFloodError:
            Print("Limit has been reached")
            break
        except Exception as e:
            print(e)    
        count+=1
fileobject.close()   
            
print("All the messages have been sent sucessfully.")

print("Initial Users in file = " + str(num_lines))
print("Count of Messages sent to (Including non-usernames) = " + str(count))
print("Number of people to be saved back to file = " + str(num_lines - count))


lines2 = open('contacts.csv').readlines()
open('contacts.csv', 'w').writelines(lines2[count:])

#print(client.get_me().stringify())

# client.send_file('username', '/home/myself/Pictures/holidays.jpg')

# client.download_profile_photo('me')
# messages = client.get_messages('+917000000000')
# client.download_media(messages[0])
