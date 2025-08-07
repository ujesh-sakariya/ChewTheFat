#import pickle
import pickle

import os

def ensure_files_exist():
    if not os.path.exists("friendsList.pkl") and not os.path.exists("convos.pkl") and not os.path.exists("chats.pkl"):
        with open("friendsList.pkl", "wb") as f:
            pickle.dump([], f)  # 2D list (adjacency matrix) for friends
        with open("convos.pkl", "wb") as f:
            pickle.dump({}, f)  # Dict for user ID to chat ID list
        with open("chats.pkl", "wb") as f:
            pickle.dump({}, f)  # Dict for chat ID to list of users
        #dummy user for index 0 
        new_user(0)
    



'''friendsList - who is friends with who 
convos - a list of all the chat ids that a person belongs to
a list of all the chat ids and who is in which one'''
# Data structure for storing friends list
def new_user(id):
    # Open the file in binary mode 
    with open('friendsList.pkl', 'rb') as file: 
    # Call load method to deserialze 
        friends_list = pickle.load(file)
        print(friends_list) 
        # Store another array so the new users friends can be added
        friends_list.append([])
        #  add another value to each of the existing indexes to represent a new user
        for user in friends_list:
            user.append(0)
            # Now add indexes for all the users on the database so their status can be determined
            friends_list[-1].append(0)
        # The newly added list will have one extra index therefore remove it.    
        friends_list[-1].pop()
    with open('friendsList.pkl', 'wb') as file:
        # Writng the data back to the file 
        pickle.dump(friends_list, file=file)
        # open the convos file to add the users key to the dictionary 
    with open('convos.pkl','rb') as file:
        convos = pickle.load(file)
        # add the users key to the dictionary 
        convos[id] = []
        print(convos)
    with open('convos.pkl', 'wb') as file:
        pickle.dump(convos,file)
  
# Data structure to manage friends
def friend_status(sender,reciever,status):
    # Open the file in binary mode 
    with open('friendsList.pkl', 'rb') as file: 
    # Call load method to deserialze 
        friends_list = pickle.load(file)
        friends_list[sender][reciever] = status
        print(friends_list)
        # Writng the data back to the file 
    with open('friendsList.pkl', 'wb') as file:
        pickle.dump(friends_list,file)

# Data structure to find the users friends
def get_friend_status(user):
    # Open the file in binary mode 
    with open('friendsList.pkl', 'rb') as file: 
    # Call load method to deserialze 
        friends_list = pickle.load(file)
        details = friends_list[user] 
    return details
    
# Create new chats  
def create_chat(chat_id,friends):
      # Open the file in binary mode 
    with open('chats.pkl', 'rb') as file: 
    # Call load method to deserialze 
        chats = pickle.load(file)
        chats[chat_id] = friends
        print(chats)
        # Writng the data back to the file 
    with open('chats.pkl', 'wb') as file:
        pickle.dump(chats,file)
        # add to convos so friends list can be tracked 
    with open('convos.pkl','rb') as file:
        # open convos dictionary 
        convos = pickle.load(file)
        # for each person in the friends list
        for i in friends:
            # Add the chat id to the users id 
            if i in list(convos.keys()):
                convos[i].append(chat_id)
            else:
                # if for some reason the user is not in the convos dictionary already
                convos[i] = [chat_id]
    with open('convos.pkl', 'wb') as file:
        pickle.dump(convos,file)

  # create a chat id
def create_chatid():
      # Open the file in binary mode 
    with open('chats.pkl', 'rb') as file: 
    # Call load method to deserialze 
        chats = pickle.load(file)
        print(chats)
        # find the length of the chats dictionary ( how many chats are there )
        length = len(chats) 
        length += 1
        print(f'the positon in the file is {length}')

        return length


#Find users chats 
def find_chats(user):
    chat_list = []
    # find the ids of the chat the user belongs to
    with open('convos.pkl', 'rb') as file: 
    # Call load method to deserialze 
        convos = pickle.load(file)
        # store all the chat id that the user belongs to 
        chat_id_list = convos[user]
    # find who are in those chats 
    with open('chats.pkl', 'rb') as file:
        chats = pickle.load(file)
        # add the participants of each chat in a 2D array
        for i in range(len(chat_id_list)):
            chat_list.append(chats[(chat_id_list[i])]) 
            # return it
    return chat_list, chat_id_list
       

# find the users friend request 
def findFriendReq(id):
    ids = []
    # Open the file in binary mode 
    with open('friendsList.pkl', 'rb') as file: 
    # Call load method to deserialze 
        friends_list = pickle.load(file)
        # iterate through the adjaceny matrix to find where the status is 1
        for i in range(len(friends_list)):
            if friends_list[i][id] == 1:
                # append the id the dictionary if status is 1
                ids.append(i)
    return ids


def find_id_for_chat(chat_id):
    # Open the file in binary mode 
    with open('chats.pkl', 'rb') as file: 
    # Call load method to deserialze 
        chats = pickle.load(file)
        ids = chats[chat_id]

    return ids


'''with open('convos.pkl', 'rb+') as file: 
        # Call load method to deserialze 
            chats = pickle.load(file)
            print(chats)

with open('chats.pkl', 'rb+') as file: 
        # Call load method to deserialze 
            chats = pickle.load(file)
            print(chats)
            
with open('friendsList.pkl', 'rb+') as file: 
        # Call load method to deserialze 
            chats = pickle.load(file)
            print(chats)


'''

if False:
    with open('convos.pkl', 'rb+') as fh:
        c = {0:[],1:[],2:[],3:[]}
        pickle.dump(c, fh)

    with open('friendsList.pkl', 'rb+') as fh:
        c = [[0,0,0,0],[0,0,2,2],[0,2,0,2],[0,2,2,0]]
        pickle.dump(c, fh)

    with open('chats.pkl', 'rb+') as fh:
        c = {}
        pickle.dump(c,fh)