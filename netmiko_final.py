from netmiko import ConnectHandler
from pprint import pprint

device_ip = "<!!!REPLACEME with router IP address!!!>"
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_ios",
    "ip": "10.0.15.61",
    "username": "admin",
    "password": "cisco",
}


def gigabit_status():
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
