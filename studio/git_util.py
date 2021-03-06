import re
import subprocess


def get_git_info(path='.', abort_dirty=True):
    info = {}
    if not is_git(path):
        return None

    if abort_dirty and not is_clean(path):
        return None

    info['url'] = get_repo_url(path)
    info['commit'] = get_commit(path)
    return info


def is_git(path='.'):
    p = subprocess.Popen(
        ['git', 'status'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=path)

    p.wait()
    return (p.returncode == 0)


def is_clean(path='.'):
    p = subprocess.Popen(
        ['git', 'status', '-s'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=path)

    stdout, _ = p.communicate()
    if not p.returncode == 0:
        return False

    return (stdout.strip() == '')


def get_repo_url(path='.', remove_user=True):
    p = subprocess.Popen(
        ['git', 'config', '--get', 'remote.origin.url'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=path)

    stdout, _ = p.communicate()
    assert p.returncode == 0, "git returned non-zero return code"

    url = stdout.strip()
    if remove_user:
        url = re.sub('(?<=://).*@', '', url.decode('utf-8'))
    return url


def get_commit(path='.'):
    p = subprocess.Popen(
        ['git', 'rev-parse', 'HEAD'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=path)

    stdout, _ = p.communicate()
    assert p.returncode == 0, "git returned non-zero return code"

    return stdout.strip()


def get_branch(path='.'):
    p = subprocess.Popen(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=path)

    stdout, _ = p.communicate()
    assert p.returncode == 0, "git returned non-zero return code"

    return stdout.strip().decode('utf8')
