from dataclasses import dataclass
from typing import final
import pybis
from datastore.utils import settings
import contextlib
from fastapi import HTTPException, status
from typing import Tuple
from datastore.models import auth as auth_models

from instance_creator import views as openbis_views

from functools import cache


@dataclass
class OpenbisUser(auth_models.User):
    space: str | None
    permid: str | None 


#TODO use a better method to initialise only once
@cache
def get_openbis() -> pybis.Openbis:
    config = settings.get_settings()
    return pybis.Openbis(config.openbis_server, verify_certificates=False, token=False, allow_http_but_do_not_use_this_in_production_and_only_within_safe_networks=True)



@contextlib.contextmanager
def openbis_login(username: str, password: str) -> str:
    """
    Get an :obj:`pybis.Openbis` object given
    password and username.
    """
    config = settings.get_settings()
    try:
        pb = get_openbis()
        token = pb.login(username, password)
        yield token
    except Exception as e:
        credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could login to openbis",
        headers={"WWW-Authenticate": "Bearer"})
        raise credentials_exception
    finally:
        pb.logout()



def delete_all(ob: pybis.Openbis, type:str):
    t = ob.new_transaction()
    for s in ob.get_object(type==type):
        t.add(s)