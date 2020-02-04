import sys
from typing import List, Tuple

import boto3
from botocore.client import BaseClient
from prompt_toolkit.shortcuts import confirm

SAM_DEPLOY_USER = "sam-deploy-user"
SSM_DEPLOY_USER = "ssm-deploy-user"


def main():
    iam = boto3.client("iam")

    username = get_username()
    print(f"\nusername: {username}")
    key_names = get_access_key_names(username, iam)
    if len(key_names) > 0:
        if not confirm_delete():
            print("\nfinish\n")
            return
        delete_access_keys(username, key_names, iam)
    access_key, secret_key = create_access_key(username, iam)
    print(f"\nAccessKeyId: {access_key}")
    print(f"SecretAccessKey: {secret_key}")


def get_username() -> str:
    args = sys.argv
    if len(args) < 2:
        return SAM_DEPLOY_USER
    return SSM_DEPLOY_USER if args[1] == "SSM" else SAM_DEPLOY_USER


def get_access_key_names(username: str, iam: BaseClient) -> List[str]:
    option = {"UserName": username}
    resp = iam.list_access_keys(**option)
    return [x["AccessKeyId"] for x in resp.get("AccessKeyMetadata", [])]


def confirm_delete() -> bool:
    print("\nThe user has access keys.")
    return confirm("Do you want to delete the access keys?")


def delete_access_keys(username: str, access_key_names: List[str], iam: BaseClient):
    for key_id in access_key_names:
        option = {"UserName": username, "AccessKeyId": key_id}
        iam.delete_access_key(**option)


def create_access_key(username: str, iam: BaseClient) -> Tuple[str, str]:
    option = {"UserName": username}
    resp = iam.create_access_key(**option)
    return resp["AccessKey"]["AccessKeyId"], resp["AccessKey"]["SecretAccessKey"]


if __name__ == "__main__":
    main()
