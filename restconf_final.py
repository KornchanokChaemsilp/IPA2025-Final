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


def delete(studentID, routerIP):
    """ ลบ Loopback """
    if_name = f"Loopback{studentID}"
    current_status = status(if_name, routerIP)
    
    if "No" in current_status:
        print(f"Cannot delete: Interface loopback {studentID} (does not exist)")
        return f"Cannot delete: Interface loopback {studentID}"
    
    api_url = f"https://{routerIP}/restconf/data/ietf-interfaces:interfaces/interface={if_name}"
    print(f"Attempting to DELETE {if_name}...")
    
    resp = requests.delete(
        api_url, 
        auth=basicauth, 
        headers=headers, 
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print(f"Interface loopback {studentID}  is deleted successfully using Restconf")
        return f"Interface loopback {studentID}  is deleted successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


def enable(studentID, routerIP):
    """ ลบ Loopback """
    if_name = f"Loopback{studentID}"
    current_status = status(if_name, routerIP)
    
    if "No" in current_status:
        print(f"Cannot enable: Interface loopback {studentID} (does not exist)")
        return f"Cannot enable: Interface loopback {studentID}"
    elif "enable" in current_status:
        print(f"Interface loopback {studentID} is enabled successfully")
        return f"Interface loopback {studentID} is enabled successfully"
    
    api_url = f"https://{routerIP}/restconf/data/ietf-interfaces:interfaces/interface={if_name}"
    print(f"Attempting to ENABLE {if_name}...")

    yangConfig = {
      "ietf-interfaces:interface": {
        "name": if_name,
        "enabled": True 
      }
    }

    resp = requests.patch(
        api_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print(f"Interface loopback {studentID} is enabled successfully using Restconf")
        return f"Interface loopback {studentID} is enabled successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


def disable(studentID, routerIP):
    """ ลบ Loopback """
    if_name = f"Loopback{studentID}"
    current_status = status(if_name, routerIP)
    if "No" in current_status:
        print(f"Cannot shutdown: Interface loopback {studentID} (does not exist)")
        return f"Cannot shutdown: Interface loopback {studentID}"
    
    api_url = f"https://{routerIP}/restconf/data/ietf-interfaces:interfaces/interface={if_name}"
    print(f"Attempting to DISABLE {if_name}...")
    
    yangConfig = {
      "ietf-interfaces:interface": {
        "name": if_name,
        "enabled": False 
      }
    }

    resp = requests.patch(
        api_url, 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
        )


    if(resp.status_code >= 200 and resp.status_code <= 299):
        print(f"Interface loopback {studentID} is shutdowned successfully using Restconf")
        return f"Interface loopback {studentID} is shutdowned successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))


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
        print(admin_status, oper_status)

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
    test1_status = create(studentID, routerIP)
    print(f"==> Test 1 Result: '{test1_status}'")
    test2_status = status(IF_NAME, routerIP)
    print(f"==> Test 2 Result: '{test2_status}'")
    test3_status = disable(studentID, routerIP)
    print(f"==> Test 3 Result: '{test3_status}'")
    test4_status = status(IF_NAME, routerIP)
    print(f"==> Test 3 Result: '{test4_status}'")
    print("--- 🏁 สิ้นสุดการทดสอบ ---")