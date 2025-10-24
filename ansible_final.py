import subprocess
import ansible_runner
import re
import os

def showrun(student_id, router_ip):
    # read https://www.datacamp.com/tutorial/python-subprocess to learn more about subprocess
    extra_vars_str = f'student_id={student_id} router_ip={router_ip}'
    
    command = ['ansible-playbook', 'playbook.yaml', '--extra-vars',
        extra_vars_str]

    result = subprocess.run(command, capture_output=True, text=True)

    result = result.stdout
    print("--- Ansible Output ---")
    print(result)
    print("----------------------")

    # 1. ตรวจสอบว่ามี task 'failed=1' หรือ 'unreachable=1' หรือไม่
    if "failed=1" in result or "unreachable=1" in result:
        print("Error: Ansible run reported a failure.")
        return 'Error: Ansible'

    # 2. ถ้าไม่ล้มเหลว, ให้ค้นหา "MAGIC_STRING" ที่เราพิมพ์ไว้
    #    Pattern นี้จะค้นหา 'FINAL_FILENAME_IS:' ตามด้วยชื่อไฟล์
    pattern = r"FINAL_FILENAME_IS:(\./show_run_.*?\.txt)"
    match = re.search(pattern, result)

    if match:
        # 3. ถ้าเจอ, ให้ดึงชื่อไฟล์ (กลุ่มที่ 1) ออกมา
        #    .lstrip('./') เพื่อลบ './' ด้านหน้าออก
        filename = match.group(1).lstrip('./') 
        
        print(f"Ansible successfully created file: {filename}")
        return filename
    else:
        # 4. ถ้ารันสำเร็จ แต่หา MAGIC_STRING ไม่เจอ (แปลว่าโค้ดผิดพลาด)
        print("Error: Could not parse filename from Ansible output.")
        return 'Error: Ansible'
    
def motd(routerIP, message):
    """
    ตั้งค่า MOTD บน router ที่ระบุ โดยเรียกใช้ Ansible Playbook
    """
    print(f"\n--- [START] กำลังตั้งค่า MOTD บน {routerIP} ---")

    inventory = {
        'all': {
            'hosts': {
                routerIP: {}  # <-- BUG FIXED: value ต้องเป็น dict (สำหรับ host_vars)
            },
            'vars': {
                'ansible_network_os': 'cisco.ios.ios',
                'ansible_connection': 'network_cli',
                'ansible_user': "admin",
                'ansible_password': "cisco",
                # ข้ามการตรวจสอบ SSH Host Key (สะดวกสำหรับการทดสอบ)
                'ansible_ssh_common_args': '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
            }
        }
    }

    # -----------------------------------------------------------------
    # 3. กำหนดตัวแปร (Extravars) ที่จะส่งให้ Playbook
    # -----------------------------------------------------------------
    extravars = {
        'motd_message_text': message # ชื่อตัวแปรต้องตรงกับใน motd.yaml
    }

    # 4. ค้นหาไฟล์ Playbook
    playbook_path = os.path.join(os.path.dirname(__file__), 'motd.yaml')
    if not os.path.exists(playbook_path):
        print(f"❌ Error: ไม่พบไฟล์ '{playbook_path}'")
        return f"Error: File not found {playbook_path}"

    # -----------------------------------------------------------------
    # 5. สั่งรัน Ansible Playbook!
    # -----------------------------------------------------------------
    try:
        r = ansible_runner.run(
            playbook=playbook_path,
            inventory=inventory,    # ส่ง dict inventory ที่เราสร้าง
            extravars=extravars,    # ส่ง dict ตัวแปร
            quiet=True              # ซ่อน output ของ ansible-runner (เราจะแสดงผลเอง)
        )

        # -----------------------------------------------------------------
        # 6. ตรวจสอบผลลัพธ์ (แบบรัดกุม)
        # -----------------------------------------------------------------
        
        # ตรวจสอบว่าคำสั่งรันจบ (rc == 0) และ ไม่มี task ที่ 'failed' หรือ 'unreachable'
        is_success = (
            r.rc == 0 and 
            not r.stats.get('failures') and 
            not r.stats.get('unreachable')
        )

        if is_success:
            print(f"✅ Success: ตั้งค่า MOTD บน {routerIP} สำเร็จ")
            return "Ok: success"
        else:
            print(f"❌ Error: Ansible ล้มเหลว (Return Code: {r.rc})")
            print(f"--- Stats: {r.stats} ---")
            print("--- Ansible Log (stdout) ---")
            print(r.stdout.read()) # พิมพ์ Log ทั้งหมดจาก ansible-playbook
            print("----------------------------")
            return f"Error: Ansible failed. Stats={r.stats}"
        
    except Exception as e:
        # Error ที่เกิดจาก Python เอง (เช่น inventory ผิดพลาด)
        print(e)

# ส่วนนี้สำหรับการทดสอบสคริปต์
# -----------------------------------------------------------------
if __name__ == "__main__":
    
    TARGET_ROUTER_IP = "10.0.15.61" 

    # --- ข้อความ MOTD ที่ต้องการตั้งค่า ---
    NEW_MOTD_MESSAGE = ("muhihihi muhahaha")

    # --- เรียกใช้งานฟังก์ชัน ---
    motd(TARGET_ROUTER_IP, NEW_MOTD_MESSAGE)