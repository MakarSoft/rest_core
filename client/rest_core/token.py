# ====================================================================
# token.py
# ====================================================================

from __future__ import annotations

import json
import datetime

from datetime import date, datetime, timedelta
from pathlib import Path
from pydantic import BaseModel
from typing import Optional


from project.san.brocade_api_const import BROCADE_EXPIRATION
from project.logger.logger_config import get_logger_config
from project.logger.logger_dict_config import LOG_CONFIG

logger = get_logger_config(__name__, LOG_CONFIG)


# ====================================================================
# TokenData
# ====================================================================
class TokenData(BaseModel):
    """ """

    token: str
    initialization_time: datetime
    before_expiration: Optional[int]


# ====================================================================
# TokenEncoder
# ====================================================================
class TokenEncoder(json.JSONEncoder):
    """ """

    def default(self, obj):

        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        else:
            return obj.__dict__


# --------------------------------------------------------------------
# token_json_dict_decoder
# --------------------------------------------------------------------
def token_json_dict_decoder(data: dict) -> Optional[Token]:
    """ """

    token = None
    try:
        token = Token(
            token=data["token"],
            initialization_time=datetime.fromisoformat(
                data["initialization_time"]
            ),
            before_expiration=data["before_expiration"],
        )
    except KeyError as e:
        logger.debug(f"Token decoder error: {e}")

    return token


# ====================================================================
# Token
# ====================================================================
class Token:
    """ """

    # ----------------------------------------------------------------
    # __init__
    # ----------------------------------------------------------------
    def __init__(
        self,
        token: str,
        *,
        initialization_time: Optional[datetime] = None,
        before_expiration: Optional[
            int
        ] = None,  # кол-во секунда, до истечения срока действия (от получения)
    ) -> None:

        self.token = token
        now = datetime.now()
        if (
            not isinstance(initialization_time, datetime)
            or initialization_time > now
        ):
            initialization_time = now
        self.initialization_time: datetime = initialization_time

        self.before_expiration = None
        if before_expiration and isinstance(before_expiration, int):
            self.before_expiration = before_expiration

    # ----------------------------------------------------------------
    # fake_token
    # ----------------------------------------------------------------
    @staticmethod
    def fake_token() -> Token:
        """
        for DEBUG only...
        """

        auth = "Custom_Basic bWYtYWNpLWRhdGE6eHh4OmEzYmJlNWMzOTUyMDI3YTNhZTUyMjNkNDQ3NzA1YzZhMzg0YjU1M2EyMzEyNjM0YmQxMDU4Y2U1YTkzNDI5NDY="
        token = Token(auth, before_expiration=BROCADE_EXPIRATION)
        return token

    # ----------------------------------------------------------------
    # is_valid
    # ----------------------------------------------------------------
    def is_valid(self) -> bool:
        """
        Проверка токена на валидность (должен быть не просрочен)
        """

        valid = True
        if self.before_expiration:
            valid = (
                self.initialization_time
                + timedelta(seconds=self.before_expiration)
                > datetime.now()
            )
        return valid

    # ----------------------------------------------------------------
    # to_json
    # ----------------------------------------------------------------
    def to_json(self) -> str:
        """
        Преобразование объекта токена в json-строку
        """

        return json.dumps(
            self,
            # default=lambda o: o.isoformat() if isinstance(o, (date, datetime)) else o.__dict__,
            # sort_keys=True,
            indent=4,
            cls=TokenEncoder,
        )

    # ----------------------------------------------------------------
    # get_saved_token
    # ----------------------------------------------------------------
    @staticmethod
    def get_saved_token(filename: str) -> Optional[Token]:
        """
        получает токен из указанного файла
        """

        token = None
        token_file_path = Path(filename)
        if token_file_path.exists():
            with open(token_file_path) as token_file:
                token = json.load(
                    token_file, object_hook=token_json_dict_decoder
                )

        return token

    # ----------------------------------------------------------------
    # save_token
    # ----------------------------------------------------------------
    @staticmethod
    def save_token(*, token: Optional[Token] = None, filename: str) -> None:
        """
        Сохраняет указанный токен в указанном файле
        """

        if isinstance(token, Token) and isinstance(filename, str):
            json_token = token.to_json()
            with open(filename, mode="w") as token_file:
                token_file.write(json_token)

    # ----------------------------------------------------------------
    # save
    # ----------------------------------------------------------------
    def save(self, filename: str) -> None:
        """
        Сохраняет текущий токен в указанном файле
        """
        type(self).save_token(token=self, filename=filename)


# ====================================================================
# HostToken
# ====================================================================
class HostToken(Token):

    def __init__(self, *args, host: str, **kwargs) -> None:
        self.host = host
        super().__init__(*args, **kwargs)
