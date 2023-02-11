import logging
import pathlib
import subprocess
import typing

import jinja2


def prettify_paths(*paths: typing.List[pathlib.Path]):
    cmd = [
        "shfmt",
        "-i",
        "4",
        "-w",
    ]
    paths_as_strings = [str(x.resolve()) for x in paths]
    cmd.extend(paths_as_strings)

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        outs, errs = proc.communicate(timeout=15)
        logging.debug(outs.decode())
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        logging.warning(errs.decode())

    if errs:
        logging.warning(f"failed to run {' '.join(cmd)}, error: {errs.decode()}")
    else:
        logging.debug(f"ran ok: {' '.join(cmd)}")


templates_dir = "."
loader = jinja2.FileSystemLoader(searchpath=templates_dir)
env = jinja2.Environment(loader=loader, keep_trailing_newline=True)
cache_paths = []
install_paths = []
other_script_paths = []

##############################
# containerd
##############################
template = env.get_template("containerd.sh.j2")
path = pathlib.Path("cache_containerd.sh")
cache_paths.append(path)
rendered = template.render(cache_only=True)
path.write_text(rendered)
path.chmod(0o775)

path = pathlib.Path("install_containerd.sh")
install_paths.append(path)
rendered = template.render(cache_only=False)
path.write_text(rendered)
path.chmod(0o775)

##############################
# runc
##############################

template = env.get_template("runc.sh.j2")
path = pathlib.Path("cache_runc.sh")
cache_paths.append(path)
rendered = template.render(cache_only=True)
path.write_text(rendered)
path.chmod(0o775)

path = pathlib.Path("install_runc.sh")
install_paths.append(path)
rendered = template.render(cache_only=False)
path.write_text(rendered)
path.chmod(0o775)

##############################
# kubectl
##############################

template = env.get_template("kubectl.sh.j2")
path = pathlib.Path("cache_kubectl.sh")
cache_paths.append(path)
rendered = template.render(cache_only=True)
path.write_text(rendered)
path.chmod(0o775)

path = pathlib.Path("install_kubectl.sh")
install_paths.append(path)
rendered = template.render(cache_only=False)
path.write_text(rendered)
path.chmod(0o775)

##############################
# nerdctl
##############################

template = env.get_template("nerdctl.sh.j2")
path = pathlib.Path("cache_nerdctl.sh")
cache_paths.append(path)
rendered = template.render(cache_only=True)
path.write_text(rendered)
path.chmod(0o775)

path = pathlib.Path("install_nerdctl.sh")
install_paths.append(path)
rendered = template.render(cache_only=False)
path.write_text(rendered)
path.chmod(0o775)

##############################
# kubeadmin init
##############################

template = env.get_template("kubeadm-init.sh.j2")
path = pathlib.Path("kubeadm-init.sh")
other_script_paths.append(path)
rendered = template.render(cache_only=True)
path.write_text(rendered)
path.chmod(0o775)

# end scripts

all_paths = cache_paths + install_paths + other_script_paths
prettify_paths(*all_paths)

cache_dir = pathlib.Path("stage")
pathlib.Path.mkdir(cache_dir, parents=True, exist_ok=True)

cache_path = pathlib.Path("cache.sh")
cache_path.unlink(missing_ok=True)
with cache_path.open("a") as f:
    for path in cache_paths:
        f.write(f"cd {cache_dir.resolve()}")
        f.write("\n")

        text = path.read_text()
        f.write(text)
        f.write("\n")

cache_path.chmod(0o775)

install_path = pathlib.Path("install.sh")
install_path.unlink(missing_ok=True)
with install_path.open("a") as f:
    for path in install_paths:
        text = path.read_text()
        f.write(text)
        f.write("\n")

install_path.chmod(0o775)
