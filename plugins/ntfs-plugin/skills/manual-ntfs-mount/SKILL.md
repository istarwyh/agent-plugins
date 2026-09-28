---
name: manual-ntfs-mount
description: Diagnoses and manually remounts external NTFS drives on macOS through Hasleo NTFS for Mac and macFUSE. Use when the user mentions NTFS read-only mounts, Hasleo NTFS, macFUSE, Benjamin Fleischer system extension approval, "Volume Read-Only", `/Volumes/Untitled`, or wants a manual trigger instead of an automatic launchd remount.
---

# Manual NTFS Mount

Use this skill to investigate and manually repair the specific macOS flow where the system mounts an external NTFS disk read-only before Hasleo can remount it through macFUSE.

## Safety Model

- Do not create an automatic launchd watcher unless the user explicitly asks for one.
- Always inspect status first.
- Before running a remount, confirm the user is not copying files to or from the NTFS volume unless the user already asked for the remount in the same turn.
- Treat remount as a disruptive operation: it unmounts the current volume and starts Hasleo's `NtfsMounter`.

## Quick Commands

Run from this skill directory:

```bash
scripts/remount_ntfs.sh status
```

Manual remount of the single detected external NTFS partition:

```bash
sudo scripts/remount_ntfs.sh remount --mount-point /Volumes/Untitled
```

Manual remount of a specific partition:

```bash
sudo scripts/remount_ntfs.sh remount --device disk4s1 --mount-point /Volumes/Untitled
```

Include a user-level write test after remount:

```bash
sudo scripts/remount_ntfs.sh remount --device disk4s1 --mount-point /Volumes/Untitled --write-test
```

If `sudo` cannot prompt in the current environment, run the script through macOS administrator authorization:

```bash
osascript -e 'do shell script "/absolute/path/to/scripts/remount_ntfs.sh remount --device disk4s1 --mount-point /Volumes/Untitled" with administrator privileges'
```

## Workflow

1. Run `scripts/remount_ntfs.sh status`.
2. If the disk is already mounted as `macfuse` and `Volume Read-Only: No`, stop.
3. If the disk is mounted as system `ntfs` with `read-only` or `fskit`, prepare a manual remount.
4. If macFUSE is not loaded, direct the user to approve system software from developer `Benjamin Fleischer` in Privacy & Security, then restart if macOS requests it.
5. If `NtfsMounter` is denied Full Disk Access, direct the user to add `/Applications/Hasleo NTFS For Mac.app/Contents/MacOS/NtfsMounter` to Full Disk Access.
6. Run `scripts/remount_ntfs.sh remount ...` only after the user is ready.
7. Verify with `diskutil info /dev/<device>` and, when appropriate, `--write-test`.

## References

Read `references/hasleo-macfuse.md` when diagnosing permission prompts, macFUSE errors, or why Hasleo can mount manually but not automatically.
