"""Atomic local configuration writes without predictable temporary filenames."""
import os
from pathlib import Path
import stat
import tempfile


def restrict_permissions(path):
    """Owner-only POSIX access; protected owner/SYSTEM/Administrators DACL on Windows."""
    path = reject_link_path(path)
    if os.name != 'nt':
        path.chmod(0o700 if path.is_dir() else 0o600)
        return
    import ctypes
    from ctypes import wintypes
    advapi = ctypes.WinDLL('advapi32', use_last_error=True)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    advapi.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    advapi.GetTokenInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    advapi.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.LPWSTR)]
    advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(wintypes.DWORD)]
    advapi.SetFileSecurityW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_void_p]
    token = wintypes.HANDLE()
    if not advapi.OpenProcessToken(kernel.GetCurrentProcess(), 8, ctypes.byref(token)):
        raise ctypes.WinError(ctypes.get_last_error())
    sid_text = wintypes.LPWSTR()
    descriptor = ctypes.c_void_p()
    try:
        needed = wintypes.DWORD()
        advapi.GetTokenInformation(token, 1, None, 0, ctypes.byref(needed))
        buffer = ctypes.create_string_buffer(needed.value)
        if not advapi.GetTokenInformation(token, 1, buffer, needed, ctypes.byref(needed)):
            raise ctypes.WinError(ctypes.get_last_error())
        sid_pointer = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_void_p))[0]
        if not advapi.ConvertSidToStringSidW(sid_pointer, ctypes.byref(sid_text)):
            raise ctypes.WinError(ctypes.get_last_error())
        inheritance = 'OICI' if path.is_dir() else ''
        sddl = 'D:P' + ''.join(f'(A;{inheritance};FA;;;{sid})' for sid in (sid_text.value, 'SY', 'BA'))
        if not advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, ctypes.byref(descriptor), None):
            raise ctypes.WinError(ctypes.get_last_error())
        if not advapi.SetFileSecurityW(str(path), 0x80000004, descriptor):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        if descriptor:
            kernel.LocalFree(descriptor)
        if sid_text:
            kernel.LocalFree(ctypes.cast(sid_text, ctypes.c_void_p))
        kernel.CloseHandle(token)


def reject_link_path(path):
    path = Path(path).absolute()
    for component in (path, *path.parents):
        try:
            details = component.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(details.st_mode) or getattr(details, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0):
            raise ValueError('Arquivos de segurança não podem usar links ou redirecionamentos de diretório.')
    return path


def private_directory(path):
    path = reject_link_path(path)
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    restrict_permissions(path)
    return path


def atomic_write_private(path, content):
    path = reject_link_path(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f'.{path.name}-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as stream:
            restrict_permissions(temporary)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        # Only the uniquely created temporary file is removed on failure.
        if os.path.exists(temporary):
            os.unlink(temporary)
