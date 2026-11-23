"""Validate the unpersonalized release; this does not boot or install macOS."""
import argparse
import hashlib
import json
from pathlib import Path
import plistlib
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OC = ROOT / 'EFI/OC'
CONFIGS = [OC / 'config.plist', *sorted((ROOT / 'configs').glob('*.plist'))]
PLACEHOLDERS = {
    'SystemSerialNumber': 'XXXXXXXXXXXX',
    'MLB': 'XXXXXXXXXXXXXXXXX',
    'SystemUUID': '00000000-0000-0000-0000-000000000000',
    'ROM': bytes(6),
}
checks = []


def check(name, passed):
    checks.append({'check': name, 'pass': bool(passed)})


def macho_x64(data):
    if data[:4] == b'\xcf\xfa\xed\xfe':
        return struct.unpack_from('<I', data, 4)[0] == 0x01000007
    if data[:4] in (b'\xca\xfe\xba\xbe', b'\xbe\xba\xfe\xca'):
        endian = '>' if data[:4] == b'\xca\xfe\xba\xbe' else '<'
        count = struct.unpack_from(endian + 'I', data, 4)[0]
        return any(struct.unpack_from(endian + 'I', data, 8 + i * 20)[0] == 0x01000007
                   for i in range(count))
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ocvalidate', type=Path, help='OpenCore 1.0.8 ocvalidate executable')
    parser.add_argument('--report', type=Path, help='Optional JSON result output path')
    args = parser.parse_args()
    for path in CONFIGS:
        label = path.relative_to(ROOT).as_posix()
        c = plistlib.loads(path.read_bytes())
        generic = c['PlatformInfo']['Generic']
        check(label + ': public identity placeholders',
              all(generic.get(k) == v for k, v in PLACEHOLDERS.items()))
        check(label + ': model retained', generic['SystemProductName'] == 'MacBookPro16,1')
        enabled = [x for x in c['Kernel']['Add'] if x['Enabled']]
        ids = []
        infos = []
        for entry in enabled:
            bundle = OC / 'Kexts' / entry['BundlePath']
            info_path = bundle / entry['PlistPath']
            check(label + ': kext plist ' + entry['BundlePath'], info_path.is_file())
            if not info_path.is_file():
                continue
            info = plistlib.loads(info_path.read_bytes())
            ids.append(info['CFBundleIdentifier'])
            infos.append((entry['BundlePath'], info))
            if entry['ExecutablePath']:
                exe = bundle / entry['ExecutablePath']
                check(label + ': x86_64 kext ' + entry['BundlePath'],
                      exe.is_file() and macho_x64(exe.read_bytes()))
        check(label + ': unique enabled bundle IDs', len(ids) == len(set(ids)))
        for i, (bundle, info) in enumerate(infos):
            for dep in info.get('OSBundleLibraries', {}):
                if dep in ids:
                    check(label + ': dependency ' + bundle + ' -> ' + dep, ids.index(dep) < i)
        check(label + ': USBToolBox before map',
              ids.index('com.dhinakg.USBToolBox.kext') < ids.index('com.dhinakg.USBToolBox.map'))
        check(label + ': obsolete USB injection disabled',
              all('USBInjectAll' not in x['BundlePath'] for x in enabled)
              and all(not x['Enabled'] or x['Path'] != 'SSDT-UIAC.aml' for x in c['ACPI']['Add']))
        for entry in c['ACPI']['Add']:
            if not entry['Enabled']:
                continue
            aml = OC / 'ACPI' / entry['Path']
            check(label + ': ACPI file ' + entry['Path'], aml.is_file())
            if aml.is_file():
                data = aml.read_bytes()
                check(label + ': AML checksum ' + entry['Path'],
                      len(data) >= 36 and data[:4] == b'SSDT'
                      and struct.unpack_from('<I', data, 4)[0] == len(data) and sum(data) % 256 == 0)
        for section, base in [(c['UEFI']['Drivers'], OC / 'Drivers'),
                              (c['Misc']['Tools'], OC / 'Tools')]:
            for entry in section:
                if entry['Enabled']:
                    check(label + ': EFI reference ' + entry['Path'], (base / entry['Path']).is_file())
        nv = c['NVRAM']['Add']['7C436110-AB2A-4BBB-A880-FE41995C9F82']
        dgpu_off = any(x['Path'] == 'SSDT-DDGPU.aml' and x['Enabled'] for x in c['ACPI']['Add'])
        if path.name == 'config-UHD630.plist':
            check(label + ': installation stage', dgpu_off and nv['csr-active-config'] == bytes(4)
                  and 'nvaccel=1' not in nv['boot-args'])
        else:
            check(label + ': dGPU exposed with backlight patch',
                  not dgpu_off and 'applbkl=1' in nv['boot-args']
                  and all('disable-external-gpu' not in x for x in c['DeviceProperties']['Add'].values()))
        if path == OC / 'config.plist':
            check(label + ': installed NVIDIA settings', nv['csr-active-config'] == bytes.fromhex('430a0000')
                  and 'nvaccel=1' in nv['boot-args']
                  and any(x['Enabled'] and x['Identifier'] == 'com.apple.iokit.IONDRVSupport'
                          for x in c['Kernel']['Block']))
        if args.ocvalidate:
            result = subprocess.run([str(args.ocvalidate.resolve()), str(path)], capture_output=True)
            check(label + ': OpenCore 1.0.8 ocvalidate', result.returncode == 0)
            if result.returncode:
                print((result.stdout + result.stderr).decode('utf-8', errors='replace'))
    for path in (ROOT / 'EFI').rglob('*.efi'):
        data = path.read_bytes()
        offset = struct.unpack_from('<I', data, 0x3c)[0]
        check('x64 PE/COFF ' + path.relative_to(ROOT).as_posix(),
              data[offset:offset+4] == b'PE\0\0' and struct.unpack_from('<H', data, offset+4)[0] == 0x8664)
    for line in (ROOT / 'docs/SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        expected, rel = line.split('  ', 1)
        path = ROOT / rel
        check('SHA256 ' + rel, path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected)
    check('No identity backups or Finder metadata in EFI',
          not any('.before-' in p.name or p.name.startswith('._') or p.name == '.DS_Store'
                  for p in (ROOT / 'EFI').rglob('*')))
    report = {'kind':'static-release-validation', 'ocvalidate_requested':bool(args.ocvalidate),
              'checks':len(checks), 'passed':sum(x['pass'] for x in checks),
              'hardware_boot_test_performed':False, 'results':checks}
    if args.report:
        args.report.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(f"Static checks: {report['passed']}/{report['checks']} passed")
    for failure in (x for x in checks if not x['pass']):
        print('FAIL:', failure['check'])
    return int(report['passed'] != report['checks'])


if __name__ == '__main__':
    sys.exit(main())
