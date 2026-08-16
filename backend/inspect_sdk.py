import sarvamai
import inspect

try:
    from sarvamai.types import SpeechToTextResponse
    print("SpeechToTextResponse fields:", SpeechToTextResponse.__fields__)
except Exception as e:
    print(e)
    # Let's search for the type
    import pkgutil
    import importlib
    for m in pkgutil.walk_packages(sarvamai.__path__, sarvamai.__name__ + "."):
        if "types" in m.name:
            try:
                mod = importlib.import_module(m.name)
                for name, obj in inspect.getmembers(mod, inspect.isclass):
                    if "SpeechToTextResponse" in name:
                        print("Found:", name, "in", m.name)
                        if hasattr(obj, "__fields__"):
                            print("Fields:", obj.__fields__)
                        elif hasattr(obj, "model_fields"):
                            print("Fields:", obj.model_fields)
            except:
                pass
