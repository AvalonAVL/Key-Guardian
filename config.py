from decouple import config
from outline_vpn.outline_vpn import OutlineVPN

def gb_to_bytes(gb: float):
    if gb is not None:
        bytes_in_gb = 1024 ** 3  
        return int(gb * bytes_in_gb)
    else:
        return None

def get_keys():
    return client.get_keys()

def get_key_info(key_id: str):
    return client.get_key(key_id)

def create_new_key(key_id: str = None, name: str = None, data_limit_gb: float = None): # type: ignore
    return client.create_key(key_id=key_id, name=name, data_limit=gb_to_bytes(data_limit_gb))

def rename_key(key_id: str, new_key_name: str):
    return client.rename_key(key_id, new_key_name)

def upd_limit(key_id: str, data_limit_gb: float):
    return client.add_data_limit(key_id, gb_to_bytes(data_limit_gb))

def delete_limit(key_id: str):
    return client.delete_data_limit(key_id)

def delete_key(key_id: str):
    return client.delete_key(key_id)

def get_service_info():
    return client.get_server_information()

def create_dynamic_link(user_id: str, conn_name: str ='connect'):
    id = int(user_id)
    return f"{gateway}/conf/{salt}{hex(id)}#{conn_name}"


api_url = config('API_URL')
cert_sha256 = config('CERT_SHA')
token = config('BOT_TOKEN')
gateway = str(config('OUTLINE_USERS_GATEWAY'))
salt = str(config('OUTLINE_SALT'))
admin_id = str(config('ADMIN_ID'))
key_limit = str(config('KEY_LIMIT'))

client = OutlineVPN(api_url=str(api_url), cert_sha256=str(cert_sha256))
