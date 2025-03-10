# ====================================================================
# rest_core/session.py
# ====================================================================

from __future__ import annotations

import aiohttp
import asyncio

from socket import AF_INET
from typing import Optional, Type
# from typing import Self   # 3.11
# from TracebackType    # 3.10

from .auth import Auth


CONNECTION_TIMEOUT = 15
TOTAL_TIMEOUT = 30
SIZE_POOL_AIOHTTP = 100
DEFAULT_REQUEST_TIMEOUT = 150


SEMAPHORE_LIMIT = 100

# ====================================================================
# Session
# ====================================================================
class Session(aiohttp.ClientSession):
    """
    """

    def __init__(
        self,
        *,
        timeout: Optional[aiohttp.ClientTimeout]=None,
        connector: Optional[aiohttp.TCPConnector]=None,
        auth = None
    ) -> None:
        
           
        if not timeout:
            timeout = aiohttp.ClientTimeout(total=DEFAULT_REQUEST_TIMEOUT)
            
        if not connector:
            connector = aiohttp.TCPConnector(
                family=AF_INET,
                limit_per_host=SIZE_POOL_AIOHTTP,
                ssl=False
            )
           
        super().__init__(
            timeout=timeout,
            connector=connector,
            auth=auth,
            raise_for_status=True
        )

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    async def __aenter__(self) -> Session:
        return self

    # ----------------------------------------------------------------
    # ----------------------------------------------------------------
    async def __aexit__(
        self,
        *exc
        # exc_type: Optional[Type[BaseException]],
        # exc_val: Optional[BaseException],
        # exc_tb  : Optional[TracebackType]
    ) -> Optional[bool]:

        await self.close()
        return None

