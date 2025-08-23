from decouple import config
from outline_vpn.outline_vpn import OutlineVPN


def gb_to_bytes(gb: int | None):
    if gb is not None:
        bytes_in_gb = 1000 ** 3  
        return int(gb * bytes_in_gb)
    else:
        return None


def get_keys(timeout: int | None = None):
    if timeout is None:
        return client.get_keys()
    else:
        return client.get_keys(timeout=timeout)


def get_key(key_id: str, timeout: int | None = None):
    if timeout is None:
        return client.get_key(key_id=key_id)
    else:
        return client.get_key(key_id=key_id, timeout=timeout)


def create_key(key_id: str | None = None, name: str | None = None,
               method: str | None = None, password: str | None = None,
               data_limit_gb: int | None = None, port: int | None = None,
               timeout: int | None = None):
    return client.create_key(key_id=key_id, name=name, method=method, # type: ignore
                             password=password, data_limit=gb_to_bytes(data_limit_gb), # type: ignore
                             port=port, timeout=timeout) # type: ignore


def rename_key(key_id: str, new_name: str, timeout: int | None = None):
    if timeout is None:
        return client.rename_key(key_id=key_id, name=new_name)
    else:
        return client.rename_key(key_id=key_id, name=new_name, timeout=timeout)


def set_limit(key_id: str, new_limit_gb: int, timeout: int | None = None):
        return client.add_data_limit(key_id=key_id, limit_bytes=gb_to_bytes(new_limit_gb), # type: ignore
                                     timeout=timeout)  # type: ignore


def delete_limit(key_id: str, timeout: int | None = None):
    if timeout is None:
        return client.delete_data_limit(key_id=key_id)
    else:
        return client.delete_data_limit(key_id=key_id, timeout=timeout)


def delete_key(key_id: str, timeout: int | None = None):
    if timeout is None:
        return client.delete_key(key_id=key_id)
    else:
        return client.delete_key(key_id=key_id, timeout=timeout)


def delete_limit_all_keys(timeout: int | None = None):
    if timeout is None:
        return client.delete_data_limit_for_all_keys()
    else:
        return client.delete_data_limit_for_all_keys(timeout=timeout)


def set_limit_all_keys(limit_gb: int, timeout: int | None = None):
    return client.set_data_limit_for_all_keys(limit_bytes=gb_to_bytes(limit_gb), # type: ignore
                                              timeout=timeout) # type: ignore


def get_all_transferred_data(timeout: int | None = None):
    if timeout is None:
        return client.get_transferred_data()
    else:
        return client.get_transferred_data(timeout=timeout)


def get_metrics_status(timeout: int | None = None):
    if timeout is None:
        return client.get_metrics_status()
    else:
        return client.get_metrics_status(timeout=timeout)


def get_server_info(timeout: int | None = None):
    if timeout is None:
        return client.get_server_information()
    else:
        return client.get_server_information(timeout=timeout)


def set_hostname(hostname: str, timeout: int | None = None):
    if timeout is None:
        return client.set_hostname(hostname=hostname)
    else:
        return client.set_hostname(hostname=hostname, timeout=timeout)


def set_metrics_status(status: bool, timeout: int | None = None):
    if timeout is None:
        return client.set_metrics_status(status=status)
    else:
        return client.set_metrics_status(status=status, timeout=timeout)


def set_port(port: int, timeout: int | None = None):
    if timeout is None:
        return client.set_port_new_for_access_keys(port=port)
    else:
        return client.set_port_new_for_access_keys(port=port, timeout=timeout)
    

def set_server_name(name: str, timeout: int | None = None):
    if timeout is None:
        return client.set_server_name(name=name)
    else:
        return client.set_server_name(name=name, timeout=timeout)
    

def create_dynamic_link(user_id: str, conn_name: str ='connect'):
    id = int(user_id)
    return f"{gateway}/conf/{salt}{hex(id)}#{conn_name}"


gateway = str(config('OUTLINE_USERS_GATEWAY'))
salt = str(config('OUTLINE_SALT'))
admin_id = str(config('ADMIN_ID'))

client = OutlineVPN(api_url=str(config('API_URL')), cert_sha256=str(config('CERT_SHA')))
