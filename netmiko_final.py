from netmiko import ConnectHandler
from pprint import pprint

# device_ip = "<!!!REPLACEME with router IP address!!!>"
# username = "admin"
# password = "cisco"



def gigabit_status(routerIP):
    device_params = {
    "device_type": "cisco_ios",
    "ip": routerIP,
    "username": "admin",
    "password": "cisco",
    }
    ans_list = []
    with ConnectHandler(**device_params) as ssh:
        up = 0
        down = 0
        admin_down = 0
        result = ssh.send_command("show ip interface brief", use_textfsm=True)

        # ตรวจสอบว่า TextFSM ทำงานสำเร็จ (ได้ผลลัพธ์เป็น list)
        if not isinstance(result, list):
            error_msg = "Error: TextFSM parsing failed. Check command or template."
            print(error_msg)
            return error_msg
        
        for status in result:
            # print(status)
            if status['interface'].startswith("GigabitEthernet"):
                current_status_str = ""
                # 1. 'administratively down' สำคัญสุด
                if status['status'] == "administratively down":
                    admin_down += 1
                    current_status_str = "administratively down"
                
                # 2. 'up' ต้อง up ทั้ง status และ protocol
                elif status['status'] == "up" and status['proto'] == "up":
                    up += 1
                    current_status_str = "up"
                
                # 3. นอกนั้นถือว่า 'down' ทั้งหมด (เช่น up/down, down/down)
                else:
                    down += 1
                    current_status_str = "down"

                # <--- Write code here: เพิ่มข้อมูล interface และสถานะเข้าไปใน 'ans'
                ans_list.append(f"{status['interface']} {current_status_str}")
        ans = ",".join(ans_list)
        ans += f" -> {up} up, {down} down, {admin_down} administratively down"
        pprint(ans)
        return ans

def get_motd(router_ip):
    device_params = {
    "device_type": "cisco_ios",
    "ip": router_ip,
    "username": "admin",
    "password": "cisco",
    }
    
    # คำสั่ง 'show banner motd' จะแสดงเฉพาะเนื้อหาของ MOTD
    # ซึ่งเหมาะสำหรับ TextFSM มากกว่า 'show run'
    cmd = 'show banner motd'
    template_path = 'motd_template.fsm' # ไฟล์ template ที่เราสร้างไว้
    
    print(f"\n--- [START] Connecting to {router_ip} ---")

    try:
        # 1. เชื่อมต่อและดึงข้อมูลด้วย Netmiko
        with ConnectHandler(**device_params) as ssh:
            print(f"✅ Connected. Sending command: '{cmd}'")
            # .strip() เพื่อลบบรรทัดว่างที่ไม่จำเป็นหน้า-หลัง
            result = ssh.send_command(cmd, use_textfsm=True)

        # 2.2 (ส่วนที่เพิ่มตามคำขอ) ตรวจสอบว่า list ว่างเปล่าหรือไม่
        # ถ้า list ว่าง = command ทำงาน แต่ TextFSM ไม่เจอ MOTD ที่ตั้งค่าไว้
        if not result: # 'if not result:' จะเป็น True ถ้า result คือ []
            error_msg = "Error: No MOTD Configured"
            print(f"✅ Command successful, but {error_msg}")
            return error_msg

        # 2.3 ถ้าทุกอย่างปกติ (ได้ list ที่มีข้อมูล)
        print(f"✅ MOTD Found. Parsed data:")
        print(result)
        return result # คืนค่า list ที่มี dictionary ของ MOTD

        # 2. ตรวจสอบว่ามี output หรือไม่
        # ตรวจสอบว่า TextFSM ทำงานสำเร็จ (ได้ผลลัพธ์เป็น list)
        # if not isinstance(result, list):
        #     error_msg = "Error: TextFSM parsing failed. Check command or template."
        #     print(error_msg)
        #     return error_msg
        
        # for status in result:
        #     print(status)
    except Exception as e:
        print(e)
        return None
    
if __name__ == "__main__":
    
    get_motd("10.0.15.61")