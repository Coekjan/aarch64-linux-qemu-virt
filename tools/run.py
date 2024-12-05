import argparse
import pathlib

from tools.utils.common import check_program, goto_workspace


def args(parser: argparse.ArgumentParser):
    """
    Adds the arguments for the run subcommand to the parser.

    NOTE: This is called from main.py.
    """
    from pathvalidate.argparse import validate_filename_arg

    parser.add_argument('name', type=validate_filename_arg,
                        help='The name of the workspace')
    parser.add_argument('--disk-name', type=validate_filename_arg, default='disk.img',
                        help='The name of the disk image')
    parser.add_argument('--smp', type=int, default=2,
                        help='The number of virtual CPUs to use')
    parser.add_argument('--ram', type=int, default=4,
                        help='The amount of RAM to allocate in GB')
    parser.add_argument('--port', type=int, default=8022,
                        help='The port to forward SSH to')
    parser.add_argument('--kernel', type=validate_filename_arg,
                        help='The name of the kernel image')


def do(arch: str, **kwargs):
    """
    The entry point for the run subcommand. Just dispatches to the appropriate function
    based on the architecture.

    NOTE: This is called from main.py.
    """
    eval(f'do_{arch}')(**kwargs)


def do_aarch64(name: str,
               disk_name: str,
               smp: int,
               ram: int,
               port: int,
               kernel: str | None):
    from .utils.qemu import run_aarch64_linux as run

    goto_workspace('aarch64', name)
    qemu = check_program('qemu-system-aarch64')
    if not pathlib.Path(disk_name).exists():
        raise FileNotFoundError(
            'Disk image not found, please run `init` first')

    if kernel is not None:
        if not pathlib.Path(kernel).exists():
            if pathlib.Path(f'Image-{kernel}').exists():
                kernel = f'Image-{kernel}'
            else:
                raise FileNotFoundError(f'Kernel image `{kernel}` not found')

    run(
        qemu,
        init=False,
        smp=smp,
        ram=ram,
        disk=pathlib.Path(disk_name),
        port=port,
        kernel=kernel,
    )
