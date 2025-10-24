from ncclient import manager
import xmltodict


def create(studentID, routerIP):
    interface_name = f"Loopback{studentID}"

    current_status = status(interface_name, routerIP)
    if "enable" in current_status or "disable" in current_status:
        print(f"Cannot create: Interface loopback {studentID}  (already exists)")
        return f"Cannot create: Interface loopback {studentID}"
    
    last_three_digits = studentID[-3:]
    x = int(last_three_digits[0])
    y = int(last_three_digits[1:])
    ip_address = f"172.{x}.{y}.1"
    
    netconf_config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <Loopback xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xc:operation="create">
            <name>{studentID}</name>
            <description>Managed by IPA2024 Bot - 66070001</description>
            <ip>
              <address>
                <primary>
                  <address>{ip_address}</address>
                  <mask>255.255.255.0</mask>
                </primary>
              </address>
            </ip>
          </Loopback>
        </interface>
      </native>
    </config>
    """

    try:
        netconf_reply = netconf_edit_config(netconf_config, routerIP)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            print(f"Interface loopback {studentID}  is created successfully using Netconf")
            return f"Interface loopback {studentID}  is created successfully using Netconf"
    except Exception as e:
        print(e)


def delete(studentID, routerIP):
    interface_name = f"Loopback{studentID}"

    current_status = status(interface_name, routerIP)
    if "No" in current_status:
        print(f"Cannot delete: Interface loopback {studentID} (does not exist)")
        return f"Cannot delete: Interface loopback {studentID}"
    
    netconf_config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <Loopback xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xc:operation="delete">
            <name>{studentID}</name>
          </Loopback>
        </interface>
      </native>
    </config>
    """

    try:
        netconf_reply = netconf_edit_config(netconf_config, routerIP)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            print(f"Interface loopback {studentID}  is deleted successfully using Netconf")
            return f"Interface loopback {studentID}  is deleted successfully using Netconf"
    except:
        print("Error!")


def enable(studentID, routerIP):
    interface_name = f"Loopback{studentID}"

    current_status = status(interface_name, routerIP)
    if "No" in current_status:
        print(f"Cannot enable: Interface loopback {studentID} (does not exist)")
        return f"Cannot enable: Interface loopback {studentID}"
    
    if "enable" in current_status:
        print(f"Interface loopback {studentID} is enabled successfully")
        return f"Interface loopback {studentID} is enabled successfully"
    
    netconf_config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <Loopback>
            <name>{studentID}</name>
            <shutdown xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:operation="delete"/>
          </Loopback>
        </interface>
      </native>
    </config>
    """

    try:
        netconf_reply = netconf_edit_config(netconf_config, routerIP)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            print(f"Interface loopback {studentID} is enabled successfully using Netconf")
            return f"Interface loopback {studentID} is enabled successfully using Netconf"
    except Exception as e:
        print(e)


def disable(studentID, routerIP):
    interface_name = f"Loopback{studentID}"

    current_status = status(interface_name, routerIP)
    if current_status == "no-return":
        print(f"Cannot shutdown: Interface loopback {studentID} (does not exist)")
        return f"Cannot shutdown: Interface loopback {studentID}"
    
    netconf_config = f"""
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <Loopback>
            <name>{studentID}</name>
            <shutdown/>
          </Loopback>
        </interface>
      </native>
    </config>
    """

    try:
        netconf_reply = netconf_edit_config(netconf_config, routerIP)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            print(f"Interface loopback {studentID} is shutdowned successfully using Netconf")
            return f"Interface loopback {studentID} is shutdowned successfully using Netconf"
    except:
        print("Error!")


def netconf_edit_config(netconf_config, routerIP):
    m = manager.connect(
    host=routerIP,
    port=830,
    username="admin",
    password="cisco",
    hostkey_verify=False
    )
    return m.edit_config(target="running", config=netconf_config)


def status(interface_name, routerIP):
    m = manager.connect(
    host=routerIP,
    port=830,
    username="admin",
    password="cisco",
    hostkey_verify=False
    )
    netconf_filter = f"""
    <filter>
      <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface>
          <name>{interface_name}</name>
        </interface>
      </interfaces-state>
    </filter>
    """

    try:
        # Use Netconf operational operation to get interfaces-state information
        netconf_reply = m.get(filter=netconf_filter)
        # print(netconf_reply)
        netconf_reply_dict = xmltodict.parse(netconf_reply.xml)

        # if there data return from netconf_reply_dict is not null, the operation-state of interface loopback is returned
        data = netconf_reply_dict.get('rpc-reply', {}).get('data')
        if data and data.get('interfaces-state') and data['interfaces-state'].get('interface'):
            interface_state = data['interfaces-state']['interface']
            # extract admin_status and oper_status from netconf_reply_dict
            admin_status = interface_state.get('admin-status')
            oper_status = interface_state.get('oper-status')
            if admin_status == 'up' and oper_status == 'up':
                return f"Interface loopback {interface_name} is enabled (checked by Netconf)"
            elif admin_status == 'down' and oper_status == 'down':
                return f"Interface loopback {interface_name} is disabled (checked by Netconf)"
        else: # no operation-state data
            return f"No Interface loopback {interface_name} (checked by Netconf)"
    except:
       print("Error!")

# ทดสอบ
# if __name__ == "__main__":
    
#     print("\n--- [STEP 1: Attempt to create (should work or fail if exists)] ---")
#     create()
    
#     print("\n--- [STEP 2: Attempt to create again (should fail)] ---")
#     create()
    
#     print("\n--- [STEP 3: Check Status] ---")
#     print(f"Current Status: {status()}")

#     print("\n--- [STEP 4: Disable interface] ---")
#     disable()

#     print("\n--- [STEP 5: Check Status] ---")
#     print(f"Current Status: {status()}")

#     print("\n--- [STEP 6: Enable interface] ---")
#     enable()

#     print("\n--- [STEP 7: Check Status] ---")
#     print(f"Current Status: {status()}")

#     print("\n--- [STEP 8: Delete interface] ---")
#     delete()

#     print("\n--- [STEP 9: Delete interface again (should fail)] ---")
#     delete()

#     print("\n--- [STEP 10: Check Status] ---")
#     print(f"Current Status: {status()}")

#     # Close the connection
#     m.close_session()
#     print("\n--- Connection Closed ---")