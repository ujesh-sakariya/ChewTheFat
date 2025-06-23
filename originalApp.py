# importing flask
from flask import Flask, render_template, request, redirect, session, url_for, session


# importing needed libraries for 2FA
#from flask_bootstrap import Bootstrap

from flask_socketio import SocketIO, emit, join_room, leave_room

# get the generate prime number function
#from encryption.findPrime import findPrime
#connecting to my mySQL

import mysql.connector

# importing libraries for 2fa

import pyotp
import qrcode

# generating TOTP codes with provided secret
totp = pyotp.TOTP("base32secret3232")
print(totp.now())
# importing libraries to upload images

from PIL import Image
import base64
import io

# connecting to my database
db = mysql.connector.connect(user='root', password='root@301124',
                              host='localhost',
                              database='messaging')

# creating a cursor
cursor = db.cursor()


#configure application

app = Flask(__name__)

# make the session for the user automatically end when the browser is closed.
# Store the details on the hard drive

SESSION_PERMANENT = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['USER'] = 'name'
app.config['2FA'] = '2FA'

# create the socket
from flask_socketio import SocketIO, emit, join_room, leave_room
app.config["SECRET KEY"] = "secret!"
socketio = SocketIO(app)

# test that it can connect to it properly
@socketio.on("connect")
def handle_connect():
    print("Client connected!")


if __name__ =="__main__":
    # run the app
    socketio.run(app)

# Create a session which has key value pairs for session variables associated values
session(app)

# Create a secure secret key
import os
app.secret_key = os.urandom(24)  # Generate a random 24-byte secret key

# get the datastrucutre functions 
from dataStructures import *

@app.route("/")
def index():

    return render_template('messaging.html')

# handle routes for login
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method =="POST":

        # Obtains the username and password from the data that is posted
        username = request.form.get('username')      
        password = request.form.get('password')
        

        #check if a account exists with the given username and pasoword
        query = ("SELECT username, password, email FROM accounts WHERE username = %s AND password = %s")
        cursor.execute(query,(username,password))
        x = cursor.fetchone()
        if x == None:
            # Output error message 
            return render_template('login.html',fail = 'Incorrect username or password')

        else:

            # set the session to the current user 
            session["name"] = username
            return render_template("login_2fa.html")
    else:
        # direct user to the login page 
        return render_template('login.html')
    
@app.route("/logout")
def logout():
    session.clear()
    return render_template('login.html')



 # handle routes for registraton
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method =="POST":

        #get the data from register
        username = request.form.get('name')      
        password = request.form.get('psswd')
        email = request.form.get('email')
        data = [username]

        #check if am account exists with the given username and pasoword
        query = ("SELECT username FROM accounts WHERE username = %s")
        cursor.execute(query,tuple(data))
        x = cursor.fetchone()
        if x != None:
            # Output error message 
            return render_template('register.html', success = 'username is already taken')
        

        # creating query to add into db
        add_accounts = ("INSERT INTO accounts "
               "(username, password, email) "
               "VALUES (%s, %s, %s)")
    
        data_accounts = (username,password,email)

        #inserting data 
        cursor.execute(add_accounts, data_accounts)

        #commit to db
        db.commit()

        # set the session to the current user 
        session["name"] = username

        # generating random secret key for authentication
        # generate random key
        key = pyotp.random_base32()
        
        # add their unique code to their account
        add_2FA = ("UPDATE accounts SET TWOFA = %s WHERE username = %s")
    
        #inserting data 
        cursor.execute(add_2FA,(key,username))

        #commit to db
        db.commit()

        # create the uri for that account
        uri = pyotp.totp.TOTP(key).provisioning_uri(name = email, issuer_name='CTF')

        # create file name
        name = f'{username}totp.jpg'
        # convert it intoa qr code
        QR = qrcode.make(uri).save(f"static/{name}")

        # read the image
        im = Image.open(f'static/{name}')

        #get in-memory info
        data = io.BytesIO()

        # save image as in-memory
        im.save(data, "JPEG")

        #encode saved image in the file
        encoded_img_data = base64.b64encode(data.getvalue())


        # inserting the QR code into the database
        try:
            with open(f'static\\{name}', 'rb') as file:
                image_data = file.read()
        except FileNotFoundError as e:
            print(f"Error reading the file: {e}")

        # store the QR code in the database
        query = ('UPDATE accounts SET QR = %s WHERE username = %s')
        cursor.execute(query,(image_data,username))
        db.commit()

        # add a user to the friends list adjacency matrix
        data = [username]
        query = ('SELECT id from accounts WHERE username = %s')
        cursor.execute(query,(data))
        id = (cursor.fetchone()[0])
        new_user(id)

        return render_template('register_2fa.html',img_data=encoded_img_data.decode('utf-8'))

    else:

        return render_template('register.html')

# route to handle the 2FA when registering 

@app.route("/register_2fa",  methods=["GET","POST"])
def register_2fa():

    if request.method == 'POST':
            # get the OTP entered 
        OTP = request.form.get('OTP')  

        # get username from session
        username = session["name"]
        print(username)
        data = [username]
        # find the correct OTP
        query = ("SELECT TWOFA FROM accounts WHERE username = %s")
        cursor.execute(query,(data))
        key = (cursor.fetchone()[0])
        print(key)
        # find the corresponding TOTP
        totp = pyotp.TOTP(key)
        # Checks if the correct TOTP was entered 
        if totp.verify(OTP) == True:
            
            # set the 2FA to the name so it is no longer the defualt text so can identiy the user has completed the 2FA
            session["TWOFA"] = username
            
            return render_template('messaging.html')
            

        else:

            # set the session to the current user 
            session["name"] = username

            # create file name
            name = f'{username}totp.jpg'

            # read the image
            im = Image.open(f'static/{name}')

            #get in-memory info
            data = io.BytesIO()

            # save image as in-memory
            im.save(data, "JPEG")

            #encode saved image in the file
            encoded_img_data = base64.b64encode(data.getvalue()).decode('utf-8')


            return render_template('register_2fa.html', img_data=encoded_img_data, status='Wrong OTP entered, Please try again')

    else:
        return render_template('login.html')


# route to handle 2FA when logging in
@app.route("/login_2fa",  methods=["GET","POST"])
def login_2fa():

    if request.method == 'POST':
            # get the OTP entered 
        OTP = request.form.get('login_TOTP')  

        # get username from session
        username = session["name"]
        data = [username]

        # find the correct OTP
        query = ("SELECT TWOFA FROM accounts WHERE username = %s")
        cursor.execute(query,(data))
        key = (cursor.fetchone()[0])
        print(key)
    
        # find the corresponding TOTP
        totp = pyotp.TOTP(key)
        print(totp)

        # Checks if the TOTP entered is correct
        if totp.verify(OTP) == True:
            
            # set the 2FA to the name so it is no longer the defualt text so can identiy the user has completed the 2FA
            session['TWOFA'] = username
            
            return redirect (url_for('mainMessage'))
        
        else:

            return render_template('login_2fa.html', status = 'Wrong OTP entered, Please try again')

# route to load messaging screen 
@app.route("/mainMessage",  methods=["GET","POST"])
def mainMessage():

        # Check if the user has logged in, if not, return them to the correct page depending on their status.
        if 'name' in session:
            if 'TWOFA' in session:
                # Get their ID number so the friends list can be found 
                username = session['name']
                data = [username]
                query = ("SELECT id FROM accounts WHERE username = %s")
                cursor.execute(query,(data))
                id = (cursor.fetchone()[0])
                print(id)
                chat_list = []
                # call th find_chats function to find the users chats
                chats,chat_id_list = find_chats(id)
                # Iterate through each list within the 2D array
                for i in range(len(chats)):
                    # Convert the list of ids to a string for the SQL query
                    id_string = ', '.join(map(str, chats[i]))
                    query = f"SELECT username FROM accounts WHERE id IN ({id_string})"
                    # execute query
                    cursor.execute(query)
                    # Fetch all the results
                     # Fetch all the results
                    names = cursor.fetchall()
                    # get rid of the the brackets and concatinate it into 1 string
                    name_string =""
                    for j in range(len(names)):
                        temp = str(names[j][0].strip())
                        name_string += temp
                        name_string +=','
                    name_string = name_string[:-1]
                    chat_list.append(name_string)
                print(chat_list)

                session['chat_list'] = chat_list
                session['chat_id_list'] = chat_id_list
                print(chat_id_list)
                session['prev_openchat'] = 'NULL'
                x = session['prev_openchat']
                print(f'joined room {x}')
            
                                    
                return render_template('messaging.html',chat_list=chat_list,open = 'no')
            else:
                return render_template('login_2fa.html')



# route to load messaging screen 
@app.route("/manageFriends",  methods=["GET","POST"])
def manageFriends():

    if request.method == 'GET':

        # Check if the user has logged in, if not, return them to the correct page depending on their status.
        if 'name' in session:
            if 'TWOFA' in session:
                # Get their ID number so the friends list can be found 
                username = session['name']
                data = [username]
                query = ("SELECT id FROM accounts WHERE username = %s")
                cursor.execute(query,(data))
                id = (cursor.fetchone()[0])   
                # find the users friend requests
                FQ = findFriendReq(id)
                if len(FQ) > 0:
                    # Convert the list of ids to a string for the SQL query
                    id_string = ', '.join(map(str,FQ))
                    query = f"SELECT username FROM accounts WHERE id IN ({id_string})"
                    # execute query
                    cursor.execute(query)
                    # Fetch all the results and store the username in an array
                    Freq = [] 
                    names = cursor.fetchall()
                    for j in range(len(names)):
                        temp = str(names[j][0].strip())
                        Freq.append(temp)
                else:
                    Freq = [] 
                # store in session
                session['ids4Freq'] = FQ 
                ids = []
                session['ids'] = ids
                status = []
                session['status'] = status

                # return the page back to user
                return render_template('managefriends.html', freq = Freq)
          #  else:
            return render_template('login_2fa.html')
        #else:
        return render_template('login.html')

# route to find friends screen 
@app.route("/findFriends",  methods=["POST"])
def findFriends():

    if request.method == 'POST':

        # Get their ID number 
        username = session['name']
        data = [username]
        query = ("SELECT id FROM accounts WHERE username = %s")
        cursor.execute(query,(data))
        id = ((cursor.fetchone()[0]))
        print(id)

        # get users search request
        search_pattern = request.form.get('search')
        # query databse to obtain the users username and ids
        query = ("SELECT username,id FROM accounts WHERE username LIKE %s ")
        cursor.execute(query, ('%' + search_pattern + '%',))
        accounts = (cursor.fetchall())
        # id to remove
        remove = []
        print(accounts)
        for i in range(len(accounts)):
            print(i)
            print(accounts[i])
            if accounts[i][1] == id:
                remove.append(i)
        # if there is an id to remove 
        if len(remove) > 0:
            accounts.pop(remove[0])


        # initialise the users names and ids array
        print(accounts)
        names1 = []
        ids = []
        # Convert the tuples into 1 array
        for i in range(len(accounts)):
            names1.append(accounts[i][0])
            print(names1)
            print(ids)
            ids.append(accounts[i][1])
        # Get their ID number so the friends list can be found 
        username = session['name']
        data = [username]
        query = ("SELECT id FROM accounts WHERE username = %s")
        cursor.execute(query,(data))
        id = ((cursor.fetchone()[0]))
        print(id)
        # get the users friend status with the people in the search
        friends_list = get_friend_status(id)
        status = []
        for j in range(len(ids)):
            status.append(friends_list[(ids[j])])
        print(status)

        # store these variables in the session so we can access them again

        session['ids'] = ids
        session['status'] = status

        # find the users friend requests
        FQ = findFriendReq(id)
        if len(FQ) > 0:
            # Convert the list of ids to a string for the SQL query
            id_string = ', '.join(map(str,FQ))
            query = f"SELECT username FROM accounts WHERE id IN ({id_string})"
            # execute query
            cursor.execute(query)
            # Fetch all the results and store the username in an array
            Freq = [] 
            names = cursor.fetchall()
            for j in range(len(names)):
                temp = str(names[j][0].strip())
                Freq.append(temp)
        else:
            Freq = []
        
        # return page back to user
        return render_template('manageFriends.html', accounts = names1, status = status, freq = Freq)


# route to handle the changes made to the users friends list
@app.route("/friendslist_changes",  methods=["POST","GET"])
def friendslist_changes():

    if request.method == 'POST':

        # get the data of what buttons were clicked.
        data = request.get_json()
        # get the users changes#
        # for both friend requests and changes in status
        button_indexes = data.get('button_indexes',[])
        button_indexes2 = data.get('button_indexes2',[])

        print(button_indexes)  
        print(button_indexes2)  

        # get the users data

        ids = session['ids']
        status = session['status']
        FQ = session['ids4Freq']


        # Get their ID number so the friends list can be found 
        username = session['name']
        data = [username]
        query = ("SELECT id FROM accounts WHERE username = %s")
        cursor.execute(query,(data))
        id = ((cursor.fetchone()[0]))

        # store the ids that a new conversation wil be added to 
        newChat =[]
        if len(button_indexes) > 0:
            for i in range(len(button_indexes)):
                if status[button_indexes[i]] == 0:
                    # change the friend status to pending
                    friend_status(id,ids[button_indexes[i]],1)
                    find_chats(id)
                    # add the user to a new conversation 
                elif status[button_indexes[i]] == 2:
                    newChat.append(ids[button_indexes[i]])
                print(newChat)
                    
            # check if the user wants a new chat to be created
            if len(newChat) > 0:
                # add the user to the chat
                newChat.append(id)
                # find the next chat id and store th chat
                chatid = create_chatid()
                print(f'the id of the chat will be {chatid}')
                create_chat(chatid,newChat)
        
        # checks if the user has made any changes to their friends list
        if len(button_indexes2) > 0:
            # calcualtes if the user has accepted a friend request
            for i in range (len(button_indexes2)):
                if button_indexes2[i] % 2 == 0:
                    index = int(button_indexes2[i] / 2)
                    freq = FQ[index]
                    # finds the users and makes the changes to the friends list
                    friend_status(id,freq,2)
                    friend_status(freq,id,2)
                # calcualtes if the user has rejected a friend request
                elif button_indexes2[i] % 2 == 1:
                    index = button_indexes2[i] // 2
                    freq = FQ[index]
                    # finds the users and makes the changes to the friends list
                    friend_status(id,freq,0)
                    friend_status(freq,id,0)
                

        return render_template('messaging.html')
    else:
        return redirect (url_for('mainMessage'))
    
# back button 
@app.route("/backtomessaging",  methods=["GET"])
def backtomessaging():
    return redirect (url_for('mainMessage'))

# handle opening chats 
@app.route("/openchats", methods=["GET","POST"])
def openchats():

    if request.method == 'POST':
        
        # if the user has clicked on a chat
        # get the index value of the chat
        data = request.get_json()
        openchat = data.get('chat')
        # store it in the sesion 
        session['currentchat'] = openchat

    # if a GET request is made, get the current chat
    openchat = session['currentchat']
    print(f'the open chat is {openchat}')
    # get the chat list which is stored in sessions
    chat_list = session['chat_list']
    # get the ids of the chat_list
    chat_id_list = session['chat_id_list']
    
    # convert the names in the chat list into arrays from strings
    # This is so the chat name can be presented
    names_in_chats = [item.split(',')[:-1] for item in chat_list]
    chosen_chat = names_in_chats[openchat]
    print(f'chat name is {chosen_chat}')

    # find the chat that was clicked on 
    current = chat_list[openchat]
    # Get rid of the last comma in the name
    current = current[:-1]
    # find the current chat_id using the index value and the Chat_id_list
    chat_id = chat_id_list[openchat]
    # store the previous openchat so we can close the socket for it later on
    # Store the current chat id
    session['openchat'] = chat_id
    session['prev_openchat'] = session['openchat']
    x = session['prev_openchat']
    print(f'The id of the chat is and the value of openchat is now {x}')

    # get the messages for that chat
    data = [chat_id]
    query = ("SELECT id,message FROM messages WHERE chatID = %s")
    cursor.execute(query,(data))
    chats = ((cursor.fetchall()))
    
    # create an array to store the message 
    message = []
    # find the particpants of the chat
    participants = find_id_for_chat(chat_id)
    participants.sort()
    #find the usernames of the ids
    # Iterate through each list within the 2D array
    for i in range(len(participants)):
        # Convert the list of ids to a string for the SQL query
        id_string = ', '.join(map(str, participants))
        query = f"SELECT username FROM accounts WHERE id IN ({id_string})"
        # execute query
        cursor.execute(query)
        # Fetch all the results
        names = cursor.fetchall()

    # create a dictionary where the key is the id and the definition is the users name 
    accounts_dict = {}
    for i in range(len(participants)):
        accounts_dict[participants[i]] = names[i][0]
    
    # find the current users id
    username = session['name']
    data = [username]
    query = ("SELECT id FROM accounts WHERE username = %s")
    cursor.execute(query,(data))
    id = (cursor.fetchone()[0])

    # add the messages to an array with the users name and depending if it is the current user, store the value 0 or 1
    # This is so we can different style depending on if the user sent a message or not
    # cheeck if there are any messages  
    if len(chats) > 0:
      
        for i in range(len(chats)):
          
            if chats[i][0] == id:
                message.append([accounts_dict[chats[i][0]],chats[i][1],1])
            else:
                message.append([accounts_dict[chats[i][0]],chats[i][1],0])
        print(message)

    return render_template('messaging.html', chat_list = chat_list, openchat = current, message = message, open = 'yes' )

# handle user joining a room

@socketio.on('join')
def on_join(data):
    # get the index
    index = data.get('value')
    # get the ids of the chat_list
    chat_id_list = session['chat_id_list']
    chat_id = chat_id_list[index]
    # get the users name
    username = session['name']
    # get the chat that was clicked on
    print('the join function has been called')
    print(f'The id of the chat is {chat_id}')
    room = chat_id
    # join the room 
    join_room(room)
    print(f"{username} joined room: {room}")
    # Set the previous chat session variable to room
    session['prev_openchat'] = room
    x = session['prev_openchat']
    print(f'The previous chat has now been set to {x}')
    # Emit message to the frontend so everyone on the chat is notified 
    emit('joined_room', {'joined': username + ' is on the chat.'}, room=room)
    # Acknowledge the client-side event
    return {'status': 'success'}

@socketio.on('leave')
def on_leave(data):
    # get the user's username
    username = session['name']
    # find the room they were previoously in
    room = session['prev_openchat']
    # leave the room
    leave_room(room)
    print(f"User has left room: {room}")
    # let everyone in that room know that the user has left the room
    emit('joined_room', {'joined': username + ' is no longer on the chat'}, room=room)
    # Acknowledge the client-side event
    return {'status': 'success'}


# handle new messages
@socketio.on("new_message")
def handle_new_message(message):
    # get the contnets of the message 
    text = message.get('message')
    # get the index of the chat that was clicked
    index = message.get('index')
    print(f' the index clicked was {index}')
    # get the id of the chat
    chat_id_list = session['chat_id_list']
    chat_id = chat_id_list[index]
    print(f"New message: {message}")
    # find the current users id
    username = session['name']
    print(username)
    data = [username]
    query = ("SELECT id FROM accounts WHERE username = %s")
    cursor.execute(query,(data))
    id = (cursor.fetchone()[0])
    print(f'the current id is{id}')   
    # add the message to the database 
    print(f'messages are being added to {chat_id}')
    query = ("INSERT INTO messages (chatID,id,message) VALUES (%s,%s,%s)")
    data = (chat_id,id,text)
    cursor.execute(query,data)
    db.commit()
    room = chat_id
    # This will take in the message and broadcast to all the clients 
    emit("chat",{"message":text, "ID":id,"username":username}, room=room)
    print('successful')
# handle sending messages 






@app.route("/send", methods=["POST"])
def send():
   
        # get the messgae the user wants to send 
        message = request.form.get('send')
        # find the current users id
        username = session['name']
        data = [username]
        query = ("SELECT id FROM accounts WHERE username = %s")
        cursor.execute(query,(data))
        id = (cursor.fetchone()[0])
        print(f'the current id is{id}')   
        # add the message to the database 
        chat_id = session['openchat']
        query = ("INSERT INTO messages (chatID,id,message) VALUES (%s,%s,%s)")
        data = (chat_id,id,message)
        cursor.execute(query,data)
        db.commit()

        return redirect (url_for('openchats'))

# handle deleting messages 
@app.route("/deleteMessage", methods=["POST"])
def deleteMessage():
    if request.method == 'POST':
        #get the index of the message the user wantes to delete
        data = request.get_json()
        index = data.get('mesg')
        chat_index = data.get('index')
        print(f'The message at index position {index} will be deleted')
        #get the chat id
        # get the ids of the chat_list
        chat_id_list = session['chat_id_list']
        chat_id = chat_id_list[chat_index]
        # find the current users id
        username = session['name']
        data = [username]
        query = ("SELECT id FROM accounts WHERE username = %s")
        cursor.execute(query,(data))
        id = (cursor.fetchone()[0])
        # find all the messages of the chat that the user has sent 
        query = ("SELECT * FROM messages WHERE chatID = %s AND id = %s")
        data = (chat_id,id)
        cursor.execute(query,data)
        messages = (cursor.fetchall())
        print(messages)
        # using the index value of the messae to delete, we can find the message the user wants to delete 
        msg_to_delete = messages[index][0]
        # delete the message from the database 
        query = ("DELETE FROM messages WHERE messageID = %s")
        data = [msg_to_delete]
        cursor.execute(query,(data))
        db.commit()
        return redirect (url_for('openchats'))

# Change Password 
@app.route("/changePassword", methods=["POST","GET"])
def changePassword():
    if request.method == 'POST':
        # get the details of the passwords eneterd 
        current = request.form.get('originalpassword')
        print(current)
        new = request.form.get('newpassword')
        # find the current users password
        username = session['name']
        data = [username]
        query = ("SELECT password FROM accounts WHERE username = %s")
        cursor.execute(query,(data))
        password = (cursor.fetchone()[0])
        print(password)
        # check if the entered paossword is the same or not
        if password == current:
            # if the same, update the new password in the databse
            query = ("UPDATE accounts SET password = %s WHERE username = %s")
            data = [new,username]
            cursor.execute(query,(data))
            db.commit()
            return render_template('settings.html', status = 'Your password has successfully been changed')
        else:
            # let the user know that the entered password was incorrect
            return render_template('settings.html', status = 'Incorrect password entered')
    else:
        return render_template('settings.html')

# Clear Conversation  
@app.route("/clearconversation", methods=["POST"])
def clearconversation():
    # get the index of the chat
    data = request.get_json()
    index = data.get('index')
     # get the chat id
    chat_id_list = session['chat_id_list']
    chat_id = chat_id_list[index]
    query = ("DELETE FROM messages WHERE chatID = %s")
    data = [chat_id]
    cursor.execute(query,(data))
    db.commit()

    return redirect (url_for('openchats'))


@app.route('/get_session_id', methods=['GET'])
def get_session_id():
    username = session['name']
    data = [username]
    query = ("SELECT id FROM accounts WHERE username = %s")
    cursor.execute(query,(data))
    id = (cursor.fetchone()[0])
    return jsonify({'session_id': id})
