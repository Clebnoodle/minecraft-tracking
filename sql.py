import mysql.connector
from mojang import MojangAPI
import json

file = open("token.json")
tokens = json.load(file)
file.close()


mydb = mysql.connector.connect(
    host = tokens["host"],         # the host machine, 'localhost' if on the same machine
    user = tokens["user"],         # the MySQL user to run this application through
    password = tokens["password"], # the user's password
    database = tokens["database"]  # the database you wish to connect to
)
mycursor = mydb.cursor()


def process(type_string):
  discord_id = input("Enter the user's discord id: ")
  ign = input("Enter the user's minecraft username: ")

  uuid = MojangAPI.get_uuid(ign)
  if uuid == None:
    print("ERROR: minecraft username does not exist")
    return

  mycursor.execute(
    "INSERT INTO user (user_discord_id, user_minecraft_uuid) "
    f"VALUES ({discord_id}, '{str(uuid)}');"
  )
  mydb.commit()
  mycursor.execute(
    "INSERT INTO app_action (app_action_type, app_action_date, user_id_mod, user_id_user) "
    f"SELECT '{type_string}', CURDATE(), 4, user_id "
    "FROM user "
    f"WHERE user_minecraft_uuid = '{str(uuid)}';"
  )
  mydb.commit()


def action(action_type):
  ign = input("Enter the user's minecraft username: ")
  uuid = MojangAPI.get_uuid(ign)
  if uuid == None:
    print("ERROR: minecraft username does not exist")
    return
  
  mycursor.execute(
    "SELECT user_id "
    "FROM user "
    f"WHERE user_minecraft_uuid = '{uuid}';"
  )
  result = mycursor.fetchall()
  if result[0] == None:
    print("ERROR: user is not in database")
    return
  else:
    user_id = result[0]
    print(f'userid: {user_id[0]}')
    description = input("OPTIONAL: input a short description of the action taken: ")
    mycursor.execute(
      "INSERT INTO action (action_type, action_date, action_description, user_id) "
      f"VALUES ('{action_type}', CURDATE(), '{description}', {user_id[0]});"
    )
    mydb.commit()


def show_users():
  mycursor.execute(
    "SELECT user_discord_id, user_minecraft_uuid FROM user;"
  )
  result = mycursor.fetchall()
  print("\nDisplaying users")
  for x in result:
    disId = x[0]
    uuid = x[1]
    username = MojangAPI.get_username(uuid)
    print(f"Discord ID: {disId}, Minecraft username: {username}")


def show_apps():
  mycursor.execute(
    "SELECT u.user_discord_id, u.user_minecraft_uuid, aa.app_action_type, aa.app_action_date "
    "FROM user u "
    "JOIN app_action aa "
    "ON u.user_id = aa.user_id_user;"
  )
  result = mycursor.fetchall()

  print("\nDisplaying application records")
  for x in result:
    disId = x[0]
    uuid = x[1]
    type = x[2]
    date = x[3]
    username = MojangAPI.get_username(uuid)
    if type == 'a':
      type = 'accepted'
    else:
      type = 'denied'
    print(f"\tDiscord ID: {disId}, Minecraft username: {username}, Status: {type}, Date: {date}")


def show_actions():
  username = input("\nEnter minecraft username: ")
  uuid = MojangAPI.get_uuid(username)
  if uuid == None:
    print(f"ERROR: username {username} does not exist")
    return
  
  mycursor.execute(
    "SELECT action_type, action_date, action_description "
    "FROM action a "
    "WHERE a.user_id = "
      "(SELECT user_id "
      "FROM user u "
      f"WHERE user_minecraft_uuid = '{uuid}') "
    ";"
  )
  result = mycursor.fetchall()

  print(f"\nDisplaying actions for user {username}")
  for x in result:
    type = x[0]
    date = x[1]
    description = x[2]
    print(f"\tAction: {type}, Date: {date}, Description: {description}")


running = True
while running:
  print("\napplications:")
  print("\t'accept' to accept user")
  print("\t'deny' to deny user")
  print("users:")
  print("\t'mute' to mute user")
  print("\t'tempban' to temporarily ban user")
  print("\t'ban' to permanently ban user")
  print("display:")
  print("\t'showusers' to display all users")
  print("\t'showapps' to display application records")
  print("\t'showactions' to display actions against a user")
  print("\n'quit' to stop program")

  choice = input(":")
  if choice == 'quit':
    running = False
  elif choice == 'accept':
    process('a')
  elif choice == 'deny':
    process('d')
  elif choice == 'mute':
    action('mute')
  elif choice == 'tempban':
    action('tempban')
  elif choice == 'ban':
    action('ban')
  elif choice == 'showusers':
    show_users()
    input("Press enter to continue: ")
  elif choice == 'showapps':
    show_apps()
    input("Press enter to continue: ")
  elif choice == 'showactions':
    show_actions()
    input("Press enter to continue: ")