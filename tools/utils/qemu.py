import pathlib
import subprocess


def run_aarch64_linux(qemu: pathlib.Path,
                      extra: tuple[str] | None = None,
                      /, *,
                      init: bool,
                      smp: int,
                      ram: int,
                      disk: pathlib.Path,
                      port: int,
                      kernel: pathlib.Path | None = None,
                      extra_bootargs: str | None = None):
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
        '-netdev', f'user,id=net0,hostfwd=tcp::{port}-:22',
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
        else:
            bootargs = 'earlycon root=/dev/vda2'
            if extra_bootargs:
                bootargs += ' ' + extra_bootargs
            args = args + (
                '-kernel', kernel,
                '-append', bootargs,
            )
    subprocess.check_call(args)
