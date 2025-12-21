
from sms_service import NetgsmSMSService
import logging

# Configure logging to see output
logging.basicConfig(level=logging.INFO)

print("--- Starting SMS Test ---")
sms = NetgsmSMSService()
print(f"Username: {sms.username}")
print(f"Sender: {sms.sender}")

# Test sending to your number
test_phone = "5307111864"
print(f"Sending test SMS to {test_phone}...")

result = sms.send_sms(test_phone, "Tevkil Platformu Test Mesaji - Lutfen dikkate almayiniz.")
print(f"Result: {result}")
print("--- End SMS Test ---")
