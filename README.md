# ChewTheFat

# Secure E2E Messaging Application

A secure, full-stack messaging application that was developed as part of my A-Level Computer Science project. The platform supports both standard and end-to-end encrypted communication using RSA and AES encryption, allowing users to safely chat with security and privacy at its core.

## 🚀 Features

- **User Authentication**
  - Account creation and login
  - Google 2FA (Two-Factor Authentication)
  - Reset password support

- **Messaging**
  - One-to-one and group chats
  - Real-time messaging with WebSockets
  - Notifications for when a user is on the chat
  - Message deletion (individual or entire conversation)

# 2 Modes

- **End-to-End Encrypted Mode (E2E)**
  - Messages are encrypted client-side
  - Encrypted Messages are sent securely
  - Decrypted on client side for one time viewing and **never stored** on the database

- **Standard Messaging Mode**
  - Messages are stored in the database in plain text
  - Suitable for persistent, accessible conversation history

- **Friends and Discovery**
  - Add/remove friends
  - Search and discover new users
  - Maintain a friend list
  - Make new chats / groupchats

## 🔐 Security Details
 
  - **E2E Encryption Flow**:
  - RSA key pair fully implemented and coded from scratch, generated per user upon registration
  - AES encryption algorithm also fully coded manually, used to encrypt the RSA private key in 16-byte blocks
  - AES key derived from the user's password using SHA-256
  - The encrypted private key is securely stored in the database
  - Upon selecting E2E mode, the encrypted key is sent to the frontend and decrypted locally
  - This approach guarantees that message content remains private and inaccessible to the server


- **2FA Integration**:
  - Time-based one-time passwords (TOTP) using Google Authenticator
  - Prevents unauthorised access even if passwords are compromised

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** Python with Flask framework and Jinja templating  
- **Real-time Communication:** Flask-SocketIO for WebSocket handling  
- **Database:** MySQL (using MySQL Connector for Python)  
- **Data Persistence:** Pickle (`.pkl`) files to manage and maintain the friends system  
- **Encryption:** Custom-implemented RSA and AES algorithms for end-to-end encryption  

