import subprocess
import re

def showrun(student_id):
    # read https://www.datacamp.com/tutorial/python-subprocess to learn more about subprocess
    command = ['ansible-playbook', 'playbook.yaml', '--extra-vars',
        f'student_id={student_id}']

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