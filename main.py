from deployment.thingsboard_deployment import execute_thingsboard_deployment
from deployment.openremote_deployment import execute_openremote_deployment

print("Select platform to deploy:")
print("1. Thingsboard")
print("2. OpenRemote")
platform = input("Enter your choice (1 or 2): ")

if platform not in ["1", "2"]:
    print("Invalid choice. No deployment executed.")
else:
    if platform == "1":
        execute_thingsboard_deployment()
    if platform == "2":
        execute_openremote_deployment()