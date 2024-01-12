
import typing
from bitwarden_utils.core.proc import BwProc
import inspect

def BwProcCallback(_type : typing.Literal["pre", "post"] = "post"):
    def decorator(func):
        func._bwproc_callback_marker = _type
        return func
    return decorator

class BwProcAdapter:
    def __init__(self):
        for method in dir(self):
            if method.startswith("__"):
                continue
            
            methodObj = getattr(self, method)
            
            if not callable(methodObj):
                continue
            
            if (w := getattr(methodObj, "_bwproc_callback_marker", None)) is None:
                continue
            
            if w == "pre" and methodObj not in BwProc.preExecCallbacks:
                BwProc.preExecCallbacks.append(methodObj)
            elif w == "post" and methodObj not in BwProc.postExecCallbacks:
                BwProc.postExecCallbacks.append(methodObj)
                
    
    @classmethod
    def loadCls(cls):
        for name, methodObj in inspect.getmembers(cls):
            
            if not(inspect.ismethod(methodObj) and hasattr(methodObj, "__self__") and methodObj.__self__ is cls):
                continue
        
            if (w := getattr(methodObj, "_bwproc_callback_marker", None)) is None:
                continue
            
            if w == "pre" and methodObj not in BwProc.preExecCallbacks:
                BwProc.preExecCallbacks.append(methodObj)
            elif w == "post" and methodObj not in BwProc.postExecCallbacks:
                BwProc.postExecCallbacks.append(methodObj)
                