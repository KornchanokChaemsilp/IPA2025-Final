#######################################################################################
# Yourname: Kornchanok Chaemsilp
# Your student ID: 66070001
# Your GitHub Repo: https://github.com/KornchanokChaemsilp/IPA2024-Final.git

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
import json
import time
import re
import os
import xml.dom.minidom
from dotenv import load_dotenv
from requests_toolbelt.multipart.encoder import MultipartEncoder
import netconf_final
import netmiko_final
import ansible_final

#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.

load_dotenv()

ACCESS_TOKEN = os.environ["WEBEX_ACCESS_TOKEN"]
# print(ACCESS_TOKEN)
if ACCESS_TOKEN is None:
    print("Error: WEBEX_ACCESS_TOKEN environment variable not set.")
    exit(1)

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = (
    "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vYmQwODczMTAtNmMyNi0xMWYwLWE1MWMtNzkzZDM2ZjZjM2Zm"
)

# roomIdToGetMessages = (
#     "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vZjBmMzdkZTAtYjAxMC0xMWYwLTgxNmEtYmZkNWZkODQzYjgw"
# )

last_message_id = None

method = "" # ตั้งค่าเริ่มต้น


while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    
    # store the text of the first message in the array
    ### FIXED ### - ตรวจสอบว่าข้อความนี้เป็นข้อความใหม่หรือไม่
    message_id = messages[0].get("id")
    if message_id == last_message_id:
        continue # ถ้าเป็นข้อความเดิมที่อ่านแล้ว ให้ข้ามไป

    # ถ้าเป็นข้อความใหม่, ให้อัปเดต ID ก่อนเลย
    last_message_id = message_id

    message = messages[0].get("text", "") # ใช้ .get() เพื่อความปลอดภัย
    print("Received message: " + message)

    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"
    # match = re.match(r"/(\d+) (\S+)", message)
    match = re.match(r"/(66070001) (.+)", message)
        
    responseMessage = None # ตั้งค่าเริ่มต้น
    studentID = ""
    routerIP = ""
    command = "" # ตั้งค่าเริ่มต้น


    if match:
        # extract studentID and command
        studentID = match.group(1)

        # command = match.group(2)

        args_string = match.group(2)
        args_list = args_string.split()
        arg_1 = args_list[0]
        arg_2 = ""
        if len(args_list) > 1:
            arg_2 = args_list[1]

        if arg_1 == "restconf":
            print("Ok: Restconf")
            method = "restconf"
            responseMessage = "Ok: Restconf"
        elif arg_1 == "netconf":
            print("Ok: Netconf")
            method = "netconf"
            responseMessage = "Ok: Netconf"
        else:
            if not method:
                print("Error: No method specified")
                responseMessage = "Error: No method specified"
            elif arg_1[0].isdigit():
                if arg_2 in ["create", "delete", "enable", "disable", "status"]:
                    print("Router IP:", arg_1, "Command:", arg_2)
                    routerIP = arg_1
                    command = arg_2
                else:
                    print("Error: No command found.")
                    responseMessage = "Error: No command found."
            else:
                print("Error: No IP specified")
                responseMessage = "Error: No IP specified"


        print(studentID)
        print(routerIP)
        print(method)
        print(command)
        # print(f"Processing command '{command}' for studentID '{studentID}'")
        
        # สร้างชื่อ Loopback
        loopback_name = f"Loopback{studentID}"

# 5. Complete the logic for each command

        if method == "netconf":
            if routerIP and command == "create":
                responseMessage = netconf_final.create(studentID, routerIP)    
            elif routerIP and command == "delete":
                responseMessage = netconf_final.delete(studentID, routerIP)
            elif routerIP and command == "enable":
                responseMessage = netconf_final.enable(studentID, routerIP)
            elif routerIP and command == "disable":
                responseMessage = netconf_final.disable(studentID, routerIP)
            elif routerIP and command == "status":
                responseMessage = netconf_final.status(loopback_name, routerIP)
        elif method == "restconf":
            pass
        
        # elif command == "gigabit_status":
        #     responseMessage = netmiko_final.gigabit_status()
        # elif command == "showrun":
        #     responseMessage = ansible_final.showrun(studentID)
        else:
            pass
            # responseMessage = "Error: No command or unknown command"
        
# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail

        # ถ้าไม่มี responseMessage (เช่น ไม่ใช่ command) ก็ไม่ต้องทำอะไร
        if responseMessage is None:
            continue

        fileobject = None # ประกาศตัวแปรไว้นอก try

        # ตรวจสอบว่า command คือ 'showrun' 
        # และ responseMessage (ผลลัพธ์จาก ansible_final.showrun()) ไม่ใช่ 'Error: Ansible'
        if command == "showrun" and responseMessage != 'Error: Ansible':
            
            # ถ้าสำเร็จ, responseMessage จะเป็น "ชื่อไฟล์" เช่น "show_run_...txt"
            filename = responseMessage 

            try:
                # เปิดไฟล์ที่ ansible สร้างขึ้น
                fileobject = open(filename, "rb") # "rb"
                filetype = "text/plain"
                
                # เตรียมข้อมูลสำหรับส่งแบบ Multipart (ส่งไฟล์)
                postData = {
                    "roomId": roomIdToGetMessages,
                    "text": f"Here is the requested config: {filename}",
                    "files": (filename, fileobject, filetype),
                }
                postData = MultipartEncoder(fields=postData)
                HTTPHeaders = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": postData.content_type,
                }
            except FileNotFoundError:
                # กรณีฉุกเฉิน: ถ้า ansible บอกว่าสำเร็จ แต่ Python หาไฟล์ไม่เจอ
                print(f"Error: File {filename} not found!")
                responseMessage = f"Error: Ansible OK, but file {filename} not found."
                # ส่งเป็นข้อความธรรมดาแทน (โค้ดจะตกลงไปใน else ข้างล่าง)
                command = "force_text_error" # บังคับให้ไปที่ else

        # ถ้าเป็น command อื่น 
        # หรือถ้า 'showrun' ล้มเหลว (responseMessage == 'Error: Ansible')
        # หรือถ้าหาไฟล์ไม่เจอ (command == "force_text_error")
        if command != "showrun" or responseMessage == 'Error: Ansible' or command == "force_text_error":
            postData = {"roomId": roomIdToGetMessages, "text": responseMessage}
            postData = json.dumps(postData)

            # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
            HTTPHeaders = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}  

        # Post the call to the Webex Teams message API.
        r = requests.post(
            "https://webexapis.com/v1/messages",
            data=postData,
            headers=HTTPHeaders,
        )
        if fileobject: 
            fileobject.close()
        if not r.status_code == 200:
            raise Exception(
                "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
            )
