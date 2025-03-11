# ====================================================================
# utils_socket.py
# ====================================================================

import enum
import socket

from collections import namedtuple
from urllib.parse import urlparse

from typing import Optional, List, Mapping, Any, Hashable


IPv4 = namedtuple(
    'IPv4',
    ('host', 'port')
)

IPv6 = namedtuple(
    'IPv6',
    ('host', 'port', 'flowonfo', 'scopeid')
)

AddrInfo = namedtuple(
    'AddrInfo',
    ('family', 'sock_type', 'proto', 'canon_name', 'sock_addr')
)

class AddrInfo_Ind(enum.IntEnum):
    family = 0
    sock_type = 1
    proto = 2
    canon_name = 3
    sock_addr = 4
    

FAMILY =  AddrInfo_Ind.family
SOCK_TYPE =  AddrInfo_Ind.sock_type
PROTO =  AddrInfo_Ind.proto
CANON_NAME = AddrInfo_Ind.canon_name
SOCK_ADDR = AddrInfo_Ind.sock_addr


# --------------------------------------------------------------------
# get_url_port
# --------------------------------------------------------------------
def get_url_port(url: str) -> int:
    parsed_url = urlparse(url)
    port = socket.getservbyname(parsed_url.scheme)
    
    return port


# --------------------------------------------------------------------
# get_schema_port
# --------------------------------------------------------------------
def get_schema_port(port: int) -> Optional[str]:
    schema = None
    try:
        schema = socket.getservbyport(port)
    finally:
        return schema


# --------------------------------------------------------------------
# get_socket_constants
# --------------------------------------------------------------------
def get_socket_constants(prefix: str) -> Mapping[Hashable, str]:
    '''
    Получение значения констант модуля socket по префиксу имени...
        например:
            families = get_socket_constants('AF_')
            types = get_socket_constants('SOCK_')
            protocols = get_socket_constants('IPPROTO_')
    '''
    socket_attrs = {
        getattr(socket, name): name for name in socket.__dict__ if name.startswith(prefix)
    }
        
    return socket_attrs

    
# --------------------------------------------------------------------
# resolve_addr
# --------------------------------------------------------------------
def resolve_addr(
    host: str,
    port: Optional[int] = None
) -> Optional[List[IPv4]]:
    '''
    '''

    addr_list: Optional[List[IPv4]] = None
    try:
        addr_list = [
            IPv4(*addr_info[SOCK_ADDR])
            for addr_info in socket.getaddrinfo(host, port)  
            if addr_info[FAMILY] == socket.AF_INET and addr_info[SOCK_TYPE] == socket.SOCK_STREAM
        ]
    except socket.gaierror:
        raise socket.gaierror(f'Hostname {host} could not be resolved')
    
    return addr_list

# ####################################################################

if __name__ == '__main__':
    
    from pprint import pprint
    
    families = get_socket_constants('AF_')
    types = get_socket_constants('SOCK_')
    protocols = get_socket_constants('IPPROTO_')
    pprint(families)
    pprint(types)
    pprint(protocols)
    
    hosts = (
        '10.23.182.44',
        '10.106.107.98'
    )
    
    for host in hosts:
        h = resolve_addr(host)
        pprint(h[0])
        pprint(h[0].host)
        
    port = get_url_port('https://www.python.org')
    print(port)
    
    pass