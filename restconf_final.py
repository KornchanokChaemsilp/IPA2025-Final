import json
import requests
import re
requests.packages.urllib3.disable_warnings()

# Router IP Address is 10.0.15.181-184
# api_url = ""
ROUTER_IP = "10.0.15.62"

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF 
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
basicauth = ("admin", "cisco")


def create(studentID, routerIP):
    """ สร้าง Loopback (จากโค้ดเดิม) """
    if_name = f"Loopback{studentID}"
    current_status = status(if_name, routerIP)
    
    if "enable" in current_status or "disable" in current_status:
        print(f"Interface {if_name} already exists.")
        return f"Cannot create: Interface loopback {studentID}"
    
    print(f"Interface {if_name} does not exist. Creating...")

    last_three_digits = studentID[-3:]
    x = int(last_three_digits[0])
    y = int(last_three_digits[1:])
    ip_address = f"172.{x}.{y}.1"

    yangConfig = {
      "ietf-interfaces:interface": {
        "name": if_name, "description": f"Loopback for student {studentID}",
        "type": "iana-if-type:softwareLoopback", "enabled": True,
        "ietf-ip:ipv4": {"address": [{"ip": ip_address, "netmask": "255.255.255.0"}]}
      }
    }
    
    # สร้าง API URL แบบไดนามิกตามชื่อ interface
    api_url = f"https://{routerIP}/restconf/data/ietf-interfaces:interfaces/interface={if_name}"
    
    print(f"Attempting to CREATE {if_name} on {ROUTER_IP}...")

    resp = requests.put(
        api_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface loopback {studentID}  is created successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


# def delete():
#     resp = requests.<!!!REPLACEME with the proper HTTP Method!!!>(
#         <!!!REPLACEME with URL!!!>, 
#         auth=basicauth, 
#         headers=<!!!REPLACEME with HTTP Header!!!>, 
#         verify=False
#         )

#     if(resp.status_code >= 200 and resp.status_code <= 299):
#         print("STATUS OK: {}".format(resp.status_code))
#         return "<!!!REPLACEME with proper message!!!>"
#     else:
#         print('Error. Status Code: {}'.format(resp.status_code))


# def enable():
#     yangConfig = <!!!REPLACEME with YANG data!!!>

#     resp = requests.<!!!REPLACEME with the proper HTTP Method!!!>(
#         <!!!REPLACEME with URL!!!>, 
#         data=json.dumps(<!!!REPLACEME with yangConfig!!!>), 
#         auth=basicauth, 
#         headers=<!!!REPLACEME with HTTP Header!!!>, 
#         verify=False
#         )

#     if(resp.status_code >= 200 and resp.status_code <= 299):
#         print("STATUS OK: {}".format(resp.status_code))
#         return "<!!!REPLACEME with proper message!!!>"
#     else:
#         print('Error. Status Code: {}'.format(resp.status_code))


# def disable():
#     yangConfig = <!!!REPLACEME with YANG data!!!>

#     resp = requests.<!!!REPLACEME with the proper HTTP Method!!!>(
#         <!!!REPLACEME with URL!!!>, 
#         data=json.dumps(<!!!REPLACEME with yangConfig!!!>), 
#         auth=basicauth, 
#         headers=<!!!REPLACEME with HTTP Header!!!>, 
#         verify=False
#         )

#     if(resp.status_code >= 200 and resp.status_code <= 299):
#         print("STATUS OK: {}".format(resp.status_code))
#         return "<!!!REPLACEME with proper message!!!>"
#     else:
#         print('Error. Status Code: {}'.format(resp.status_code))


def status(interface_name, routerIP):

    student_id = re.sub(r'[a-zA-Z]+', '', interface_name)

    """
    ตรวจสอบสถานะของ interface
    คืนค่า: "EXISTS", "DOES_NOT_EXIST", หรือ "ERROR"
    """
    api_url_status = f"https://{routerIP}/restconf/data/ietf-interfaces:interfaces-state/interface={interface_name}"
    
    print(f"Checking status: {api_url_status}")

    resp = requests.get(
        api_url_status, 
        auth=basicauth, 
        headers=headers, 
        verify=False,
        timeout=10
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()

        # 1. ใช้ .get() เพื่อเข้าถึง dict ชั้นในอย่างปลอดภัย
        interface_state = response_json.get("ietf-interfaces:interface", {})
        
        # 2. ดึงค่าสถานะ (จะได้เป็น string "up" หรือ "down")
        admin_status = interface_state.get("admin-status")
        oper_status = interface_state.get("oper-status")
        if admin_status == 'up' and oper_status == 'up':
            print("enable")
            return f"Interface loopback {student_id} is enabled (checked by Restconf)"
        elif admin_status == 'down' and oper_status == 'down':
            print("disable")
            return f"Interface loopback {student_id} is disabled (checked by Restconf)"
    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return f"No Interface loopback {student_id} (checked by Restconf)"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))

# --- ทดสอบงับ ---
if __name__ == "__main__":
    
    studentID = "66070001" # ใช้นักศึกษาทดสอบ
    IF_NAME = f"Loopback{studentID}"
    routerIP = "10.0.15.62"

    print(f"--- 🧪 เริ่มต้นทดสอบฟังก์ชัน status กับ {IF_NAME} 🧪 ---")

    # --- Scenario 1: ทดสอบ "DOES_NOT_EXIST" ---
    # ลบ interface (ถ้ามี) เพื่อให้แน่ใจว่ามันไม่มีอยู่จริง
    # print("\n--- [Test 1: 'DOES_NOT_EXIST'] ---")
    # print("(Step 1.1: Cleanup - Deleting interface just in case...)")
    # delete(IF_NAME) 
    # time.sleep(1) # รอเราเตอร์ประมวลผลแป๊บนึง
    
    # print("\n(Step 1.2: Calling status function...)")
    test1_status = create(studentID, routerIP)
    print(f"==> Test 1 Result: '{test1_status}'")
    # if test1_status == "DOES_NOT_EXIST":
    #     print("✅ PASS: ฟังก์ชันคืนค่า 'DOES_NOT_EXIST' ถูกต้อง")
    # else:
    #     print("❌ FAIL: คาดหวัง 'DOES_NOT_EXIST'")

    # --- Scenario 2: ทดสอบ "up" ---
    # print("\n--- [Test 2: 'up'] ---")
    # print(f"(Step 2.1: Creating interface {IF_NAME}...)")
    # create_student_loopback(STUDENT_ID)
    # time.sleep(1) # รอ interface 'up'

    # print("\n(Step 2.2: Calling status function...)")
    test2_status = status(IF_NAME, routerIP)
    print(f"==> Test 2 Result: '{test2_status}'")
    # if test2_status == "up":
    #     print("✅ PASS: ฟังก์ชันคืนค่า 'up' ถูกต้อง")
    # else:
    #     print("❌ FAIL: คาดหวัง 'up'")

    # --- Scenario 3: ทดสอบ "down" ---
    # print("\n--- [Test 3: 'down'] ---")
    # print(f"(Step 3.1: Disabling interface {IF_NAME}...)")
    # disable(IF_NAME)
    # time.sleep(1) # รอ interface 'down'

    # print("\n(Step 3.2: Calling status function...)")
    # test3_status = status(IF_NAME)
    # print(f"==> Test 3 Result: '{test3_status}'")
    # if test3_status == "down":
    #     print("✅ PASS: ฟังก์ชันคืนค่า 'down' ถูกต้อง")
    # else:
    #     print("❌ FAIL: คาดหวัง 'down'")

    # --- Cleanup (ลบทิ้งหลังทดสอบเสร็จ) ---
    # print("\n--- [Cleanup] ---")
    # print(f"(Step 4.1: Deleting {IF_NAME}...)")
    # delete(IF_NAME)
    print("--- 🏁 สิ้นสุดการทดสอบ ---")