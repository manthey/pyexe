import os
import requests
import subprocess
import sys

if __name__ == '__main__':  # noqa
    dest = '.'
    instdest = None
    force = False
    help = False
    is64 = False
    keep = False
    minpoint = 0
    remove = False
    version = None
    for arg in sys.argv[1:]:
        if arg.startswith('-'):
            if arg in ('-f', '--force'):
                force = True
            elif arg in ('-k', '--keep'):
                keep = True
            elif arg.startswith('--inst='):
                instdest = arg.split('=', 1)[1]
            elif arg.startswith('--min='):
                minpoint = int(arg.split('=', 1)[1])
            elif arg.startswith('--out='):
                dest = arg.split('=', 1)[1]
            elif arg in ('-r', '--remove'):
                remove = True
            elif arg == '--32':
                is64 = False
            elif arg == '--64':
                is64 = True
            else:
                help = True
        elif not version:
            version = arg
        else:
            help = True
    if help or not version:
        print("""Install the latest revision of a version of python.

Syntax: install_python.py (version) [--32|--64] [--out=(destination directory)]
        [--inst=(installation directory)] [--force]
        [--min=(minimum point release)] [--keep] [--remove]

Specify just the major and minor version, such as 2.7 or 3.6.
--force will overwrite an existing installation file.
--keep keeps the install file.
--remove first uninstalls the specified version of python.""")
        sys.exit(0)
    baseurl = 'https://www.python.org/ftp/python/'
    versionList = requests.get(baseurl).text
    versionList = [part.split('"')[0] for part in versionList.split('<a href="')[1:]]
    versionList = sorted([(int(ver[len(version) + 1:].strip('/')), ver)
                          for ver in versionList if ver.startswith(version + '.')],
                         reverse=True)
    for subver, ver in versionList:
        if subver < minpoint:
            continue
        url = baseurl + ver + 'python-' + version + '.' + str(subver) + (
            '' if not is64 else ('.amd64' if version.startswith('2') else '-amd64')) + (
            '.msi' if version.startswith('2') else '.exe')
        try:
            response = requests.get(url).content
            if len(response) < 1000000:
                continue
            break
        except Exception:
            continue
    if len(response) < 1000000:
        raise Exception('Failed to find install file')
    print('Size: %d, url: %s' % (len(response), url))
    if instdest is None:
        instdest = os.path.split(dest)[0]
    if not os.path.exists(instdest):
        os.makedirs(instdest)
    installer = os.path.join(instdest, url.rsplit('/', 1)[-1])
    if os.path.exists(installer) and not force:
        raise Exception('Path already exists: %s' % installer)
    open(installer, 'wb').write(response)
    if installer.endswith('.msi'):
        uncmd = ['msiexec', '/uninstall', installer, '/quiet', '/norestart']
        cmd = ['msiexec', '/i', installer, '/quiet', '/norestart']
        altcmd = ['msiexec', '/fa', installer, '/quiet', '/norestart']
    else:
        uncmd = [installer, '/quiet', '/uninstall']
        cmd = [installer, '/quiet']
        altcmd = [installer, '/quiet', '/repair']
    cmdopts = [
        'TargetDir=' + dest, 'AssociateFiles=0', 'CompileAll=0',
        'PrependPath=0', 'Shortcuts=0', 'Include_doc=0', 'Include_dev=1',
        'Include_debug=0', 'Include_exe=1', 'Include_launcher=0',
        'InstallLauncherAllUsers=0', 'Include_lib=1', 'Include_pip=1',
        'Include_symbols=0', 'Include_tcltk=0', 'Include_test=0',
        'Include_tools=0', 'SimpleInstall=1']
    if remove:
        print('Remove: ' + ' '.join(uncmd))
        try:
            subprocess.check_call(uncmd)
        except Exception:
            pass
    print('Install: ' + ' '.join(cmd + cmdopts))
    try:
        subprocess.check_call(cmd + cmdopts)
    except Exception:
        pass
    if not os.path.exists(os.path.join(dest, 'python.exe')):
        print('Update ' + ' '.join(altcmd + cmdopts))
        subprocess.check_call(altcmd + cmdopts)
    print('Done')
    if not keep:
        os.unlink(installer)
