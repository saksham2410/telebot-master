from telethon import TelegramClient
import time
import random
from settings import USERS

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.def telegram_connect(user):
def telegram_connect(user):
    client = TelegramClient('sessions/' + user['phone'], user['api_id'], user['api_hash'])
    client.connect()

    if not client.is_user_authorized():
        try:
            print('Generating code for ' +'('+ user['phone'] +'), please wait...')
            client.send_code_request(user['phone'])
            client.sign_in(user['phone'], input('Enter the code: '))

            while not client.is_user_authorized():
                print('Bad passcode. Press "s" to skip this user.')
                code = input('Enter the code: ')

                if code == 's':
                    print('Skipping authorization of user ' + user['phone'])
                    break

                time.sleep(2)

                client.sign_in(user['phone'], code)

            if client.is_user_authorized():
                    print(user['phone'] + ' successfully authorized.')
                    time.sleep(5)
                    pass

        except Exception as e:
            print(e)
            print('Skipping this user...')
            time.sleep(5)
            pass

    else:
        print(user['phone'] + ' already authorized.')

    time.sleep(5)
    return client

# Client message initialized
def message(clinet):

    with open ("message.txt", "r") as myfile:
        data=myfile.read()
    count = 0

    with open("contacts.csv") as f:
        lines1 = f.readlines()
        num_lines = len([l for l in lines1])
        f.close()

    with open("contacts.csv") as fileobject:
        for line in fileobject:
            try:
                print('Sending message to '+line)
                time.sleep(random.randint(0,5))
                client.send_message(line, data)
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

if __name__ == '__main__':
    for user in USERS:
    #user = check_arguments()
        client=telegram_connect(user)
        message(client)
        client.disconnect()                

#print(client.get_me().stringify())

# client.send_file('username', '/home/myself/Pictures/holidays.jpg')

# client.download_profile_photo('me')
# messages = client.get_messages('+917000000000')
# client.download_media(messages[0])
