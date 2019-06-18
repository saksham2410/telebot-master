#!/usr/bin/python3
from random import randint

from settings import USERS
from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsSearch, PeerChannel, InputUser, User, Channel, Chat, InputChannel, \
    UserStatusRecently, UserStatusOnline
from telethon.tl.functions.channels import GetParticipantsRequest, InviteToChannelRequest, JoinChannelRequest,EditBannedRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
import os
import time
import sys
import json
from telethon.errors import SessionPasswordNeededError,FloodWaitError
# import socks
def telegram_connect(user):
    client = TelegramClient(user['phone'], user['api_id'], user['api_hash'])
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

def scrape(client):
    dialogs, entities = client.get_dialogs(2)

    avail_channels = {}

    channel_id = None
    for i, entity in enumerate(entities):
        if not isinstance(entity, User) and not isinstance(entity, Chat):
            avail_channels[str(i)] = [entity.title, entity.id]

    for k, v in avail_channels.items():
        print(k, v[0])

    if len(avail_channels) < 1:
        print('No super groups to scrape from.')
        sys.exit()

    channel_index = input("Please select number of super group you want to scrape> ")
    channel = client.get_entity(PeerChannel(avail_channels[channel_index][1]))

    # dialogs=client.get_dialogs(500)
    # entity=None
    # for dialog in self.dialogs:
    #     if not isinstance(dialog.input_entity, InputPeerUser) and not isinstance(dialog.input_entity,InputPeerSelf):
    #             avail_channels.append(dialog.name)

    #     if isinstance(dialog.input_entity, InputPeerChannel) and dialog.name==target_group:
    #             entity=dialog.input_entity



    offset = 0
    limit = 200
    all_participants = []
    users = []

    while True:
        try:
            participants = client.invoke(GetParticipantsRequest(channel, ChannelParticipantsSearch(''), offset,limit))
            if not participants.users:
                break
            all_participants.extend(participants.users)
            offset += len(participants.users)

        except Exception as e:
            print(e)
            sys.exit()

    for item in all_participants:       
        if (isinstance(item.status,UserStatusRecently)) or (isinstance(item.status, UserStatusOnline)):
            users.append(
                {'username': item.username, 'id': item.id, 'access_hash': item.access_hash})
            print(item+'\n')



    file_name = avail_channels[channel_index][0].replace(' ', '_')
    file_name = file_name.replace('&', '')
    file_name = file_name.replace('$', '')
    file_name = file_name.replace('/', '')
    file_name = file_name.replace('*', '')
    file_name = file_name.replace('^', '')
    file_name = file_name.replace('~', '')
    file_name = file_name.replace('|', '')

    with open('saksham.json', 'w') as f:
        json.dump(users, f, indent=4)

    print("All users of the channel " + avail_channels[channel_index][
        0] + " has been stored into " +  "saksham.json file.")

def add_users(client, file_name):
        dialogs, entities = client.get_dialogs(100)

        avail_channels = {}

        channel = None
        channel_id = None
        channel_access_hash = None
        for i, entity in enumerate(entities):
                if not isinstance(entity, User) and not isinstance(entity, Chat):
                        avail_channels[str(i)] = [entity, entity.id, entity.access_hash, entity.title]

        for k,v in  avail_channels.items():
                print(k, v[3])

        channel_index = input("Please select number of supergroup where you want to add users> ")

        #participants = client.invoke(GetParticipantsRequest(avail_channels[channel_index][0], ChannelParticipantsSearch(''), 0, 0))
        #count_of_members_before_adding = len(participants.users)

        users = None
        try:
                with open(file_name, 'r') as f:
                        users = json.load(f)

        except Exception:
                print('Invalid file name, make sure you have added extension or if file even exists, if not, run scrape_channel_users.py to create one!')
                sys.exit()

        count = int(input('Do you want to add only subset of users('+ str(len(users)) +')? if so, enter the number of users to be added: '))

        users_to_save_back = users[count:] # only users, which didnt be used, will be saved to file again
        print(str(len(users_to_save_back)) + ' users to be saved back to json file!')
        users = users[:count] # users to be added
        print(str(len(users)) + ' users to be removed from list!')
        print()

        with open(file_name, 'w') as f:
                json.dump(users_to_save_back, f, indent=4)

        input_users = []
        for item in users:
                input_users.append(InputUser(item['id'], item['access_hash']))


        user_chunks = list(chunks(input_users, 40))

        for item in user_chunks:
                try:
                        client(InviteToChannelRequest(InputChannel(avail_channels[channel_index][1], avail_channels[channel_index][2]), item))

                        print('Adding chunk of '+ str(len(item)) +' users...')
                        time.sleep(2)
                except Exception as e:
                        print(str(e))
                        print('some error occurred, skipping to next chunk.')
                        time.sleep(2)

        print('There was attempt to add ' + str(len(input_users)) + ' users in total.')

        #participants = client.invoke(GetParticipantsRequest(avail_channels[channel_index][0], ChannelParticipantsSearch(''), 0, 0))
        #count_of_members_after_adding = len(participants.users)

        #print('Count of members before adding: ' + str(count_of_members_before_adding))
        #print('Count of members after adding: ' + str(count_of_members_after_adding))
        print()
        #print('True number of added users: ' + str(count_of_members_after_adding - count_of_members_before_adding))
        print('added')


def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        yield l[i:i+n]


def remove():
    users = None
    with open(file_name, 'r') as f:
        users = json.load(f)
    value1=int(input("The file has" + str(len(users)) + ".Enter how many you want to remove :"))
    print("Removing" + str(value1) + "users") 
    users_to_save_back = users[value1:] # only users, which didnt be used, will be saved to file again
    print(str(len(users_to_save_back)) + ' users to be saved back to json file!')
    with open(file_name, 'w') as f:
        try:
            json.dump(users_to_save_back, f, indent=4)
        except Exception as e:
            print(e)




def options(client,file_name):
    client1=client
    file_name1=file_name
    while True:
        value=input("Press 1 for addition if not 50, 2 for deletion from json, else to end :")
        if value=="1":
            add_users(client1,file_name1)
        elif value=="2":
            remove()       
        else:
            break
def lawucu(fname):
 with open(fname) as f:
    content = f.readlines()

 content = [x.strip() for x in content]
 return content
def kemerdekaan(file_name):
    users = None
    try:
      with open(file_name, 'r') as f:
        users = json.load(f)

    except Exception as e:
       print(e)
       sys.exit()
    return users
def setelahDiHapus(file_name,member2):
    with open(file_name, 'w') as f:
                try:
                 json.dump(member2, f, indent=4)
                except Exception as e:
                 print(e)
def addUser(client,usr):
        print("add member")
        sementara=[]
        i=0
        for a in allGroupAndChannel(client[0]):
          i+=1
          print(str(i)+". "+a.title)
          sementara.append(a)
          
        pilihan=input("please pick one group or channel to add member to : ")
        
        # groupname=input("please input your channel like(t.me/panjuk) or supergroup invite link like(https://t.me/joinchat/FSEe_U94-87k0hQyvFjHgA):")
        # entity1 =client.get_entity(groupname)
        # inputanku=input("please input file name containing username or phonenumber like(default to user.txt):")
        member=kemerdekaan("user.txt")
        member2=kemerdekaan("user.txt")
        member3=[]
        for z in member:
            member3.append(z)
        from telethon.tl.functions.channels import InviteToChannelRequest
        h=0
        ff=0
        pertama=0
        for a in member3:
            if ff<200:
                ff=ff+1
                #  print(pertama)
                try:
                    # print(a)
                    client[pertama](InviteToChannelRequest(
                        sementara[int(pilihan) - 1],
                        [client[pertama].get_entity(a)]
                    ))
                    print(str(h) + ".adding " + str(a) + " with number : "+usr['phone'])
                    member2.remove(a)
                    setelahDiHapus("user.txt", member2)
                    #time.sleep(randint(30, 60))
                except Exception as e:
                    member2.remove(a)
                    setelahDiHapus("user.txt", member2)
                    #    client[pertama].disconnect()
                    #    print("please use another phone number")
                    print(e)
                    #time.sleep(randint(30, 60))
                #    exit()
               # if h == 250:
                 #   client[pertama].disconnect()
                #    break
                #h += 1

         
        client[pertama].disconnect()    
        
         
         

        
def banUser(client,usr):
        print("Banning Member")
       
        sementara=[]
        i=0
        for a in allGroupAndChannel(client[0]):
          i+=1
          print(str(i)+". "+a.title)
          sementara.append(a)
          
        pilihan=input("please pick one :")
        # inputanku=input("please input file name containing username or phonenumber like(default to user.txt):")
        member=kemerdekaan("user.txt")
        member3=[]
        for z in member:
            member3.append(z)
        member2=kemerdekaan("user.txt")
        from telethon.tl.types import ChannelBannedRights
        from telethon.tl.functions.channels import InviteToChannelRequest
        h=0
        pertama=0
        ss=0
        for a in member3:
            if ss<200:
                print(str(pertama) + ".using " + usr['phone']) # USERS[pertama]['phone'])
                ss = ss + 1

                try:

                    client[pertama](EditBannedRequest(sementara[int(pilihan) - 1], client[pertama].get_entity(a),
                                                      ChannelBannedRights(until_date=None, view_messages=True,
                                                                          send_messages=True, send_media=True,
                                                                          send_stickers=True, send_gifs=True,
                                                                          send_games=True, send_inline=True,
                                                                          embed_links=True)))
                    print(str(h) + ". banned " + a)
                    member2.remove(a)
                    setelahDiHapus("user.txt", member2)

                except Exception as e:
                    member2.remove(a)
                    setelahDiHapus("user.txt", member2)
                    #  client[pertama].disconnect()
                    #  print("please use another number")
                    print(e)
                #  exit()

#                if h == 290:
 #                   client[pertama].disconnect()
  #                  break
   #             h += 1
          
          
           
        
        client[pertama].disconnect()
         
        
def scrapeThis(client):
        print("scraping member")
        sementara=[]
        i=0
        for a in allGroupAndChannel(client):
          i+=1
          print(str(i)+". "+a.title)
          sementara.append(a)

          
        pilihan=input("please pick one :")
        # try:
        #   susu=client.get_participants(sementara[int(pilihan)-1])
        # except Exception as e:
        #   print("Scraping Error ")
        #   print(e)
        #   sys.exit()
        # print(len(susu)) 
        # await client.send_message(entity1, 'Hello!')
        # berapa=int(input("how much member you want to scrape: "))
        from telethon.tl.functions.channels import GetParticipantsRequest
        from telethon.tl.types import ChannelParticipantsSearch
        from time import sleep
        droptop=[]
        for b in USERS:
          droptop.append(b['phone'].replace("+",""))
        offset = 0
        limit = 100
        all_participants = []
        
        flame=[]
        try:
            while True:
                #sleep(randint(30,60))
                participants = client(GetParticipantsRequest(
                    sementara[int(pilihan) - 1], ChannelParticipantsSearch(''), offset, limit
                ))
                if not participants.users:
                    break
                for z in participants.users:
                    #  print(z)
                    try:
                        droptop.index(z.phone)
                    except Exception as e:
                        if z.username != None and (isinstance(z.status,UserStatusOnline) or isinstance(z.status, UserStatusRecently)):
                            print(z.username)
                            all_participants.append(z.username)

                offset += len(participants.users)
        except Exception as e:
            print(e)
        
        with open("user.txt", 'w') as f:
                try:
                 json.dump(all_participants, f, indent=4)
                except Exception as e:
                 print(e)
        # print(all_participants[0])
        client.disconnect()
def loginFirst(number):
   soki=[]
   for user in USERS:
        # print(user['api_hash'])
        client =  TelegramClient(number, user['api_id'], user['api_hash'])
        client.connect()
        koki=client.is_user_authorized()
        if not koki:
         client.send_code_request(number)
         client.sign_in(number, input('Enter the code: <'+number+'>'))
        soki.append(client)
        # client.disconnect()
   return soki
def allGroupAndChannel(client):
    allmakes=[]
    l=0
    for j in range(0,len(client.get_dialogs())):
        for k in range(0,len(client.get_dialogs()[j])):
            l+=1
    print("getting list of group")
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    # print(client.get_dialogs()[len(client.get_dialogs())-1])
    z=0
    for j in range(0,len(client.get_dialogs())):
        for k in range(0,len(client.get_dialogs()[j])):
            z+=1
            printProgressBar(z, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
            if isinstance(client.get_dialogs()[j][k], Channel):
                allmakes.append(client.get_dialogs()[j][k])
    # for w in client.get_dialogs():
    #     if isinstance(w.draft.entity, Channel):
    #     #   print(w.draft.entity.title)
    #       allmakes.append(w.draft.entity)
    return allmakes
          
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()
if __name__ == '__main__':
 
    # client =  TelegramClient(USERS[0]['phone'], USERS[0]['api_id'], USERS[0]['api_hash'])
    # client.connect()
    # print(allGroupAndChannel(client))
    # client.disconnect()
    for user in USERS:
       # number = input("please input your phone number: ")
        print(user['phone'])
        client = loginFirst(user['phone'])

    for user in USERS:
        # number = input("please input your phone number: ")
        print(user['phone'])
        client = loginFirst(user['phone'])
        pilihan = input("please choose one \n1.to add member \n2.to ban member \n3.to scrape \nplease choose one : ")
        print(pilihan)
        if pilihan == "1":
            addUser(client,user)
        if pilihan == "2":
            banUser(client,user)
        elif pilihan == "3":
            scrapeThis(client[0])
        else:
            exit()

            # entity1=client.get_entity('girlspod')
            # client(JoinChannelRequest(entity1))
            # entity2=client.get_entity('dx5Lcs')
            # client(JoinChannelRequest(entity2))
            # try:
            #    updates = client(ImportChatInviteRequest('IE9TC0U1ENCkA5LVPIzLrQ'))
            # except Exception as e:
            #    pass
            # scrape(client)
            # file_name= "saksham.json"
            # add_users(client, file_name)
            # options(client,file_name)



