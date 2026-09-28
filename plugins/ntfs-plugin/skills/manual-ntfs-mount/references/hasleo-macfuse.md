# Hasleo and macFUSE NTFS Flow

Use this reference when the user asks why Hasleo NTFS for Mac can mount manually but does not automatically remount an external NTFS disk.

## Expected Chain

1. macOS detects an external `Windows_NTFS` partition.
2. macOS may mount it with the built-in `ntfs` implementation as read-only, often showing `fskit` in `mount`.
3. Hasleo's LaunchDaemon (`com.hasleo.NTFS4MacMounterService`) should notice the disk.
4. Hasleo's `NtfsMounter` should use macFUSE to remount the disk writable.

On macOS 15.6.1 in the observed setup, steps 1 and 2 happened, the Hasleo service detected the disk, but automatic remount did not happen. Manual remount worked.

## Known Permission Gates

- Full Disk Access must allow:
  - `/Applications/Hasleo NTFS For Mac.app/Contents/MacOS/NtfsMounter`
  - `/Applications/Hasleo NTFS For Mac.app/Contents/MacOS/HasleoNTFS4MacService`
- macFUSE must be allowed in Privacy & Security as system software from developer `Benjamin Fleischer`.
- Apple Silicon may require Reduced Security with user management of kernel extensions enabled.

## Useful Checks

```bash
diskutil list
diskutil info /dev/disk4s1
mount | grep -i 'ntfs\|fuse'
launchctl print system/com.hasleo.NTFS4MacMounterService
kmutil showloaded | grep -i macfuse
kextstat | grep -i macfuse
systemextensionsctl list | grep -i fuse
```

Interpretation:

- `ntfs, ... read-only, ... fskit`: macOS built-in NTFS has mounted read-only.
- `macfuse, synchronous` plus `Volume Read-Only: No`: Hasleo/macFUSE writable mount is active.
- `The system extension required for mounting macFUSE volumes could not be loaded`: approve Benjamin Fleischer in Privacy & Security.
- TCC denial for `NtfsMounter` `SystemPolicyAllFiles`: add `NtfsMounter` to Full Disk Access.

## Safe Manual Sequence

1. Ensure no active file copy or write is using the NTFS volume.
2. Unmount the system read-only mount:
   ```bash
   diskutil unmount /dev/disk4s1
   ```
3. Remount with Hasleo:
   ```bash
   "/Applications/Hasleo NTFS For Mac.app/Contents/MacOS/NtfsMounter" -o allow_other /dev/disk4s1 /Volumes/Untitled
   ```
4. Verify:
   ```bash
   mount | grep disk4s1
   diskutil info /dev/disk4s1 | grep 'Volume Read-Only'
   ```

Prefer `scripts/remount_ntfs.sh` over hand-running these commands because it checks permissions, macFUSE loading, and write-test behavior.
