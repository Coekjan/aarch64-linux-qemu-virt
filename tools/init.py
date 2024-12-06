import argparse
import pathlib
import subprocess

from tools.utils.common import check_program, goto_workspace


def args(parser: argparse.ArgumentParser):
    """
    Adds the arguments for the init subcommand to the parser.

    NOTE: This is called from main.py.
    """
    from pathvalidate.argparse import validate_filename_arg

    def validate_positive_int_arg(arg: str) -> int:
        try:
            arg = int(arg)
        except ValueError:
            raise argparse.ArgumentTypeError(f'{arg} is not a valid integer')
        if arg <= 0:
            raise argparse.ArgumentTypeError(
                f'{arg} is not a positive integer')
        return arg

    parser.add_argument('name', type=validate_filename_arg,
                        help='The name of the workspace')
    parser.add_argument('--disk-name', type=validate_filename_arg, default='disk.img',
                        help='The name of the disk image')
    parser.add_argument('--disk-size', type=validate_positive_int_arg, default=16,
                        help='The size of the disk in GB')
    parser.add_argument('--smp', type=validate_positive_int_arg, default=2,
                        help='The number of virtual CPUs to use during installation')
    parser.add_argument('--ram', type=validate_positive_int_arg, default=4,
                        help='The amount of RAM to allocate in GB during installation')
    parser.add_argument('--port', type=int, default=8022,
                        help='The port to forward SSH to during installation')


def do(arch: str, **kwargs):
    """
    The entry point for the init subcommand. Just dispatches to the appropriate function
    based on the architecture.

    NOTE: This is called from main.py.
    """
    eval(f'do_{arch}')(**kwargs)


def do_aarch64(name: str,
               disk_name: str,
               disk_size: int,
               smp: int,
               ram: int,
               port: int):
    from .utils.qemu import run_aarch64_linux as run

    workspace = goto_workspace('aarch64', name)
    qemu = check_program('qemu-system-aarch64')
    qemu_img = check_program('qemu-img')
    if not (firmware := (workspace / 'firmware.bin')).exists() or not firmware.is_file():
        raise FileNotFoundError(f'''Firmware file not found, please provide it before proceeding

Debian helpfully provides some pre-packaged UEFI firmware so that we can use:
```console
$ sudo apt-get install qemu-efi-aarch64
```
This should place a `QEMU_EFI.fd` file in `/usr/share/qemu-efi-aarch64/`.

If you're not using Debian, then you can probably just download this file directly from \
the repository:
https://packages.debian.org/search?keywords=qemu-efi-aarch64&searchon=names

Once you have the file, you can copy or link it to the workspace directory  and rename \
it to `firmware.bin`. For example:
```console
$ WORKSPACE={workspace}
$ # Assuming the file is in /usr/share/qemu-efi-aarch64/
$ # Copy the file
$ cp /usr/share/qemu-efi-aarch64/QEMU_EFI.fd $WORKSPACE/firmware.bin
$ # Or link the file
$ ln -s /usr/share/qemu-efi-aarch64/QEMU_EFI.fd $WORKSPACE/firmware.bin
```
''')
    if not (install_media := (workspace / 'install-media.iso')).exists() or not install_media.is_file():
        raise FileNotFoundError(f'''Install media not found, please provide it before proceeding

You can download the Debian installer from the official website:
https://cdimage.debian.org/debian-cd/current/arm64/iso-cd/

Or download it from a mirror.

Once you have the file, you can copy or link it to the workspace directory and rename \
it to `install-media.iso`. For example:
```console
$ WORKSPACE={workspace}
$ # Assuming the file is at ~/Downloads/debian-version-arm64-netinst.iso
$ # Copy the file
$ cp ~/Downloads/debian-version-arm64-netinst.iso $WORKSPACE/install-media.iso
$ # Or link the file
$ ln -s ~/Downloads/debian-version-arm64-netinst.iso $WORKSPACE/install-media.iso
```
''')

    if pathlib.Path(disk_name).exists():
        raise FileExistsError(f'Disk image `{disk_name}` already exists. Seems like you have \
already initialized this workspace')

    subprocess.check_call((
        qemu_img, 'create', '-f', 'qcow2', disk_name, f'{disk_size}G',
    ))
    subprocess.check_call(('truncate', '-s', '64m', 'varstore.img'))
    subprocess.check_call(('truncate', '-s', '64m', 'efi.img'))
    subprocess.check_call((
        'dd', f'if={firmware}', 'of=efi.img', 'conv=notrunc',
    ))

    run(
        qemu,
        init=True,
        smp=smp,
        ram=ram,
        disk=pathlib.Path(disk_name),
        ssh_port=port,
    )
