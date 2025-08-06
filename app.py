# importing flask
from flask import Flask, render_template, request, redirect, session, url_for, jsonify

# Connect to the local databse 
import mysql.connector
import os
from dotenv import load_dotenv
db = mysql.connector.connect(
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME')
)

# creating a cursor
cursor = db.cursor()

# import libraries needed for the 2FA
import pyotp
import qrcode
from PIL import Image
import io
import base64

# Import all the datastructure functions 
from dataStructures import *

# Create instance of the flask class
app = Flask(__name__)

# generate a secret key for the session 
import secrets
app.secret_key = secrets.token_hex(16)

# allow users to remain logged in for 7 days 
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# for sockets 
from flask_socketio import SocketIO, emit, join_room, leave_room
socketio = SocketIO(app) 

import json

from werkzeug.security import generate_password_hash, check_password_hash

#ensure that the files exist
ensure_files_exist()

# default route - takes the user to the homepage to choose too log in or register an account 
@app.route("/")
def index():
    return render_template('homepage.html')

# handle routes for login
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method =="POST":

        # Obtains the username and password from the data that is posted
        username = request.form.get('username')      
        password = request.form.get('password')
       

        

        #check if a account exists with the given username and pasoword
        query = ("SELECT username, password, email FROM accounts WHERE username = %s ")
        cursor.execute(query,(username,))
        acc = cursor.fetchone()
        print(acc)
        if acc == None:
            # Output error message 
            return render_template('login.html',fail = 'Incorrect username or password')
        else:
            if not (check_password_hash(acc[1],password)):
                return render_template('login.html',fail = 'Incorrect username or password')

            # set the session to the current user 
            session["name"] = username
            return render_template("login_2fa.html")
    else:
        # direct user to the login page 
        return render_template('login.html')

# clear the session and takeuser back the homepage
@app.route("/logout")
def logout():
    session.clear()
    return render_template('homepage.html')

# handle routes for registraton
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method =="POST":

        #get the data from register
        username = request.form.get('name')      
        password = request.form.get('psswd')
        password = generate_password_hash(password)

        email = request.form.get('email')
        data = [username]

        #check if an account exists with the given username 
        query = ("SELECT username FROM accounts WHERE username = %s")
        cursor.execute(query,tuple(data))
        status = cursor.fetchone()
        if status != None:
            # Output error message 
            return render_template('register.html', success = 'username is already taken')

        # set the session to the current user 
        session["name"] = username
        
        # generate random key
        key = pyotp.random_base32()
        # create the uri for that account
        uri = pyotp.totp.TOTP(key).provisioning_uri(name = username, issuer_name='CTF')
        # convert it into a qr code
        QR = qrcode.make(uri)
        #get in-memory info
        data = io.BytesIO()
        # save image as in-memory
        QR.save(data, "JPEG")
        #encode saved image in the file
        encoded_img_data = base64.b64encode(data.getvalue())

        # creating query to add account to the db
        add_accounts = ("INSERT INTO accounts "
               "(username, password, email,TWOFA,QR) "
               "VALUES (%s, %s, %s,%s,%s)")
        data_accounts = (username,password,email,key,encoded_img_data)
        #inserting data 
        cursor.execute(add_accounts, data_accounts)
        #commit to db
        db.commit()
        
         # add a user to the friends list adjacency matrix
        data = [username]
        query = ('SELECT id from accounts WHERE username = %s')
        cursor.execute(query,(data))
        id = (cursor.fetchone()[0])
        session['ID'] = id
        new_user(id)

        return render_template('register_2fa.html',img_data=encoded_img_data.decode('utf-8'))
    else:
        # GET METHOD
        return render_template('register.html')


# route to handle the 2FA when registering 
@app.route("/register_2fa",  methods=["GET","POST"])
def register_2fa():

    if request.method == 'POST':
            # get the OTP entered 
        OTP = request.form.get('OTP')  

        # get username from session
        username = session["name"]
        data = [username]
        # find the correct OTP by getting the key 
        query = ("SELECT TWOFA FROM accounts WHERE username = %s")
        cursor.execute(query,(data))
        key = (cursor.fetchone()[0])
        # find the corresponding TOTP
        totp = pyotp.TOTP(key)
        # Checks if the correct TOTP was entered 
        if totp.verify(OTP) == True:
            # set the 2FA to the name so it is no longer the defualt text so can identiy the user has completed the 2FA
            session["TWOFA"] = username
            query = ("SELECT id FROM accounts WHERE username = %s")
            cursor.execute(query,(data))
            id = ((cursor.fetchone()[0]))
            session['ID'] = id
            return jsonify({"status":"2fa_success"})
        else:
            return jsonify({"status":"2fa_failed"})
    else:
        return render_template('homepage.html')
    

@app.route('/store_encrypted_key', methods=['POST'])
def store_encrypted_key():
    try:
        data = request.get_json()

        encrypted_private_key = data.get('encryptedPrivateKey')
        public_key = data.get('publicKey')
        n_value = data.get('nValue')

        # Basic validation
        if not encrypted_private_key or not public_key or not n_value:
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

        encrypted_private_key_json = json.dumps(encrypted_private_key)
        public_key_str = str(public_key)
        n_value_str = str(n_value)

        print("Store Encrypted Key route hit!")

        id = session['ID']
        query = ("UPDATE accounts SET privateKey = %s, publicKey = %s,nVal = %s WHERE id = %s")
        data = (encrypted_private_key_json,public_key_str,n_value_str,id)
        cursor.execute(query,data)
        db.commit()

        return jsonify({"status":"success"})


    except Exception as e:

        print('error')
        return jsonify({'status': 'error', 'message': str(e)}), 500

        
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
    
        # find the corresponding TOTP
        totp = pyotp.TOTP(key)

        # Checks if the TOTP entered is correct
        if totp.verify(OTP) == True:
            
            # set the 2FA to the name so it is no longer the defualt text so can identiy the user has completed the 2FA
            session['TWOFA'] = username
            
            return redirect (url_for('mainMessage'))
        
        else:

            return render_template('login_2fa.html', status = 'Wrong OTP entered, Please try again')
    else:
        return render_template('login.html')

# route to load messaging screen 
@app.route("/mainMessage",  methods=["GET","POST"])
def mainMessage():
        # Check if the user has logged in and passed the 2FA stage
        if 'name' in session.values() or 'TWOFA' in session.values():
            return render_template('homepage.html')
        
        # Make the browser permanet 
        session.permanent = True

        # Get their ID number so the friends list can be found 
        username = session['name']
        data = [username]
        query = ("SELECT id FROM accounts WHERE username = %s")
        cursor.execute(query,(data))
        id = (cursor.fetchone()[0])
        # store in session if not already there
        session['ID'] = id

        chat_list = []
        # call the find_chats function to find the users chats
        chats,chat_id_list = find_chats(id)
        # Iterate through each list within the 2D array
        for i in range(len(chats)):
            # Convert the list of ids to a string for the SQL query
            id_string = ', '.join(map(str, chats[i]))
            query = f"SELECT username FROM accounts WHERE id IN ({id_string})"
            # execute query
            cursor.execute(query)
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
    
        # store these lists in the session to be used by other routes
        session['chat_list'] = chat_list
        session['chat_id_list'] = chat_id_list
        session['prev_openchat'] = 'NULL'
        # testing purposes leave this here 
        x = session['prev_openchat']
        print(f'joined room {x}')
        
        return render_template('messaging.html',chat_list=chat_list,open = 'no',private_key='',
        reciever_n='',public_key='',sender_n= '',is_private_chat = False)

# route to load messaging screen 
@app.route("/manageFriends",  methods=["GET"])
def manageFriends():

    if request.method == 'GET':

        # Check if the user has logged in and passed the 2FA stage
        if 'name' in session.values() or 'TWOFA' in session.values():
            return render_template('homepage.html')
        # Get their ID number so the friends list can be found 
        id = session['ID'] 
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

# route to find friends screen 
@app.route("/findFriends",  methods=["POST"])
def findFriends():

    if request.method == 'POST':
        # Check if the user has logged in and passed the 2FA stage
        if 'name' in session.values() or 'TWOFA' in session.values():
            return render_template('homepage.html')
        
        # Get their ID number 
        id = session['ID']
        # get users search request
        search_pattern = request.form.get('search')
        # query database to obtain the users username and ids
        query = ("SELECT username,id FROM accounts WHERE username LIKE %s ")
        cursor.execute(query, ('%' + search_pattern + '%',))
        accounts = (cursor.fetchall())

        # remove the users account from the search 
        remove = []
        for i in range(len(accounts)):
            # if id matches the users id
            if accounts[i][1] == id:
                remove.append(i)
        # if there is an id to remove 
        if len(remove) > 0:
            accounts.pop(remove[0])

        # initialise the users names and ids array
        names1 = []
        ids = []
        # add the names and ids of the searched up users
        for i in range(len(accounts)):
            names1.append(accounts[i][0])
            ids.append(accounts[i][1])

        # get the users friend status with the people in the search
        friends_list = get_friend_status(id)
        status = []
        for j in range(len(ids)):
            status.append(friends_list[(ids[j])])

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
        # get the users data

        ids = session['ids']
        status = session['status']
        FQ = session['ids4Freq']

        # Get their ID number so the friends list can be found 
        id = session['ID']

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
    
        return redirect (url_for('manageFriends'))
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
        # store it in the session 
        session['currentchat'] = openchat

    # if a GET request is made ( e.g when the user deletes messages), get the current chat
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

    # create a dictionary where the key is the id and the item is the users name 
    accounts_dict = {}
    for i in range(len(participants)):
        accounts_dict[participants[i]] = names[i][0]

    # find the current users id
    id = session['ID']

    # GET ENCRYPTION KEY ONLY FOR 1-1 MESSAGING
    
    if len(accounts_dict) == 2:

        #Get the recipient's ID (the one that's NOT the current user)
        recipient_id = [key for key in accounts_dict.keys() if key != id][0]
        query = ('SELECT publicKey,nVal FROM accounts WHERE id = %s')
        cursor.execute(query,(recipient_id,))
        data = cursor.fetchone()
        public_key,sender_n = data[0],data[1]

        # get the encrypted private key of the sender and the n_val
        query = ('SELECT PrivateKey, nVal FROM accounts WHERE id = %s')
        cursor.execute(query,(id,))
        data = cursor.fetchone()
        private_key ,reciever_n= data[0],data[1]
        is_private_chat = True
    # for gc's
    else:
        private_key = 'null'
        public_key = 'null'
        sender_n = 'null'
        reciever_n = 'null'
        is_private_chat = False
    
    print("private: " ,is_private_chat)
        
    

    # add the messages to an array with the users name and depending if it is the current user, store the value 0 or 1
    # This is so we can different style depending on if the user sent a message or not
    # check if there are any messages  
    if len(chats) > 0:
      
        for i in range(len(chats)):
          
            if chats[i][0] == id:
                message.append([accounts_dict[chats[i][0]],chats[i][1],1])
            else:
                message.append([accounts_dict[chats[i][0]],chats[i][1],0])
        print(message)

    return jsonify({
    'chat_list': chat_list,'openchat': current,'message': message,'open': 'yes','private_key': private_key,'public_key': public_key,'sender_n': sender_n,
    'reciever_n': reciever_n,'is_private_chat': is_private_chat
    })
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
    mode = message.get('selectedMode')
    chat_id_list = session['chat_id_list']
    chat_id = chat_id_list[index]
    print(f"New message: {message}")
    username = session['name']
    id = session['ID']
    print(f'the current id is{id}')   
    # add the message to the database if mode is standard
    if mode == 'standard':
        print(f'messages are being added to {chat_id}')
        query = ("INSERT INTO messages (chatID,id,message) VALUES (%s,%s,%s)")
        data = (chat_id,id,text)
        cursor.execute(query,data)
        db.commit()
    room = chat_id
    # This will take in the message and broadcast to all the chat members
    emit("chat",{"message":text, "ID":id,"username":username,'mode':mode}, room=room,include_self=False)
    print('successful')

@app.route('/get_session_id', methods=['GET'])
def get_session_id():
    username = session['name']
    data = [username]
    query = ("SELECT id FROM accounts WHERE username = %s")
    cursor.execute(query,(data))
    id = (cursor.fetchone()[0])
    return jsonify({'session_id': id})    

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
        id = session['ID']
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
        new = generate_password_hash(new)
        # find the current users password
        username = session['name']
        data = [username]
        query = ("SELECT password FROM accounts WHERE username = %s")
        cursor.execute(query,(data))
        password = (cursor.fetchone()[0])
        print(password)
        # check if the entered paossword is the same or not
        if check_password_hash(password,current): 
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

    return '', 204  

