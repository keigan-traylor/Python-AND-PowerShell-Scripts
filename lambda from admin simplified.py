import boto3
from datetime import datetime, timedelta

# Set the organization ID and the number of days of inactivity before deletion
ORGANIZATION_ID = 'o-XXXXXXXXXX'
INACTIVITY_DAYS = 21

# Create clients for IAM, Organizations, and QuickSight
iam = boto3.client('iam')
org = boto3.client('organizations')
qs = boto3.client('quicksight')

def main(command, username=None, email=None):
    # Main function that takes a command and optional username and email arguments
    if command == 'check_user':
        # If the command is 'check_user', check if the user exists
        user_exists = check_user_exists(username)
        if user_exists:
            print(f"{username} exists in the AWS organization or QuickSight")
        else:
            print(f"{username} does not exist in the AWS organization or QuickSight")
    elif command == 'create_user':
        # If the command is 'create_user', create a new user with the given username and email
        create_user(username, email)
    elif command == 'delete_user':
        # If the command is 'delete_user', delete the user with the given username
        delete_user(username)
    elif command == 'monitor_users':
        # If the command is 'monitor_users', monitor all users for inactivity and delete inactive users
        monitor_users()

def check_user_exists(username):
    # Function to check if a user with the given username exists in IAM or QuickSight
    
    # Check if the user exists in IAM
    try:
        iam.get_user(UserName=username)
        return True
    except iam.exceptions.NoSuchEntityException:
        pass
    
    # Check if the user exists in QuickSight
    try:
        qs.describe_user(
            UserName=username,
            AwsAccountId=boto3.client('sts').get_caller_identity()['Account'],
            Namespace='default'
        )
        return True
    except qs.exceptions.ResourceNotFoundException:
        pass
    
    return False

def create_user(username, email):
    # Function to create a new user with the given username and email
    
    # Create the IAM user
    iam.create_user(UserName=username)
    
    # Add the user to the organization
    org.create_account(
        Email=email,
        AccountName=username,
        RoleName='OrganizationAccountAccessRole',
        IamUserAccessToBilling='ALLOW'
    )
    
    # Create the QuickSight user
    qs.register_user(
        IdentityType='IAM',
        Email=email,
        UserRole='READER',
        IamArn=f'arn:aws:iam::XXXXXXXXXX:user/{username}',
        SessionName=username,
        AwsAccountId=boto3.client('sts').get_caller_identity()['Account'],
        Namespace='default'
    )

def delete_user(username):
    # Function to delete a user with the given username
    
    # Delete the IAM user
    try:
        iam.delete_user(UserName=username)
    except iam.exceptions.NoSuchEntityException:
        pass
    
    # Remove the account from the organization
    accounts = org.list_accounts_for_parent(ParentId=ORGANIZATION_ID)['Accounts']
    for account in accounts:
        if account['Name'] == username:
            org.remove_account_from_organization(AccountId=account['Id'])
    
    # Delete the QuickSight user
    try:
        qs.delete_user(
            UserName=username,
            AwsAccountId=boto3.client('sts').get_caller_identity()['Account'],
            Namespace='default'
        )
    except qs.exceptions.ResourceNotFoundException:
        pass

def monitor_users():
    # Function to monitor all users for inactivity and delete inactive users
    
    # Get all IAM users
    users = iam.list_users()['Users']
    
    for user in users:
        username = user['UserName']
        
        # Get the last time the user accessed AWS services
        last_used = iam.get_user_last_used(UserName=username).get('UserLastUsed')
        
        # If the user has never accessed AWS services, use their creation date as their last access date
        if not last_used:
            last_used = user['CreateDate']
        
        # Calculate the number of days since their last access
        days_since_last_used = (datetime.now(last_used.tzinfo) - last_used).days
        
        # If it has been more than INACTIVITY_DAYS since their last access, delete the user
        if days_since_last_used > INACTIVITY_DAYS:
            delete_user(username)
