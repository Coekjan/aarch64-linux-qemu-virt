import pathlib
import subprocess


def run_aarch64_linux(qemu: pathlib.Path,
                      extra: tuple[str] | None = None,
                      /, *,
                      init: bool,
                      smp: int,
                      ram: int,
                      disk: pathlib.Path,
                      ssh_port: int,
                      qemu_debug: bool = False,
                      kernel: pathlib.Path | None = None,
                      kernel_extra_bootargs: str | None = None,
                      dry_run: bool):
    args = (
        qemu, '-M', 'virt',
        '-machine', 'virtualization=true',
        '-machine', 'virt,gic-version=3',
        '-cpu', 'max,pauth-impdef=on',
        '-smp', f'{smp}',
        '-m', f'{ram}G',
        '-drive', 'if=pflash,format=raw,file=efi.img,readonly=on',
        '-drive', 'if=pflash,format=raw,file=varstore.img',
        '-drive', f'if=virtio,format=qcow2,file={disk}',
        '-device', 'virtio-scsi-pci,id=scsi0',
        '-object', 'rng-random,filename=/dev/urandom,id=rng0',
        '-device', 'virtio-rng-pci,rng=rng0',
        '-device', 'virtio-net-pci,netdev=net0',
        '-netdev', f'user,id=net0,hostfwd=tcp::{ssh_port}-:22',
        '-nographic',
    )
    if extra:
        args = args + extra
    if init:
        args = args + (
            '-drive', 'if=none,id=cd,file=install-media.iso',
            '-device', 'scsi-cd,drive=cd',
        )
    if kernel is not None:
        if init:
            raise ValueError('Cannot specify kernel when initializing')
        bootargs = 'earlycon root=/dev/vda2'
        if kernel_extra_bootargs:
            bootargs += ' ' + kernel_extra_bootargs
        args = args + (
            '-kernel', kernel,
            '-append', bootargs,
        )
    if qemu_debug:
        if init:
            raise ValueError('Cannot debug when initializing')
        args = ('gdb', '--args') + args
    if dry_run:
        def stringify(arg):
            arg = str(arg)
            return f'"{arg}"' if ' ' in arg else arg
        print(' '.join(map(stringify, args)))
    else:
        subprocess.check_call(args)
