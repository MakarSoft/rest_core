import sys
import builtins
from typing import Optional, Any
import inspect



# --------------------------------------------------------------------
# get_type
# --------------------------------------------------------------------
def get_type(
    type_name: str,
    mod_name: str = None
) -> Optional[type]:
    '''
    Получение типа по имени.
    '''

    try:
        t = getattr(builtins, type_name)
    except AttributeError:
        # нет среди builtins
        # смотрим пользовательские типы ...
        
        if mod_name is None:
            # если модуль не указан, смотрим атрибуты текущего модуля
            mod_name = __name__
        try:
            mod = sys.modules[mod_name]
        except KeyError:
            # нет модуля с таким именем ...
            return None

        try:
            # получаем атрибут с именем type_name
            # в пространстве имен модуля с именем mod
            t = getattr(mod, type_name)
        except AttributeError:
            return None
        
    return t if isinstance(t, type) else None

# --------------------------------------------------------------------
# get_kwargs
# --------------------------------------------------------------------
def get_kwargs() -> dict[str, Any]:
    '''
    '''
    
    frame = inspect.currentframe().f_back
    keys,_,_,values = inspect.getargvalues(frame)
    
    # kwargs = {key: values[key] for key in keys if keys != 'self'}
    
    # для отладки...
    kwargs = {}
    for key in keys:
       if key != 'self':
           kwargs[key] = values[key]
    
    return kwargs