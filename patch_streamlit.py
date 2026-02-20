import streamlit.watcher.local_sources_watcher as lsw

def safe_get_module_paths(module):
    try:
        if hasattr(module, '__path__'):
            return list(module.__path__._path) if hasattr(module.__path__, '_path') else []
        return []
    except Exception:
        return []

lsw.get_module_paths = safe_get_module_paths