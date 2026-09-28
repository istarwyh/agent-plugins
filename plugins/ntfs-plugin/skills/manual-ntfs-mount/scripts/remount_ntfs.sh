#!/bin/bash
set -u

MOUNTER="/Applications/Hasleo NTFS For Mac.app/Contents/MacOS/NtfsMounter"
DEFAULT_MOUNT_POINT="/Volumes/Untitled"

usage() {
  cat <<'EOF'
Usage:
  remount_ntfs.sh status [--device diskXsY]
  remount_ntfs.sh remount [--device diskXsY] [--mount-point /Volumes/Name] [--write-test] [--force]

This script is intentionally manual. It never installs launchd jobs or watches disks.
`remount` unmounts the current NTFS volume and starts Hasleo NtfsMounter via macFUSE.
EOF
}

die() {
  echo "error: $*" >&2
  exit 1
}

normalize_device() {
  local dev="$1"
  dev="${dev#/dev/}"
  dev="${dev#r}"
  printf '%s\n' "$dev"
}

detect_ntfs_device() {
  diskutil list | awk '/Windows_NTFS/ {print $NF}'
}

require_device() {
  local dev="${1:-}"
  if [ -n "$dev" ]; then
    normalize_device "$dev"
    return
  fi

  local devices count
  devices="$(detect_ntfs_device)"
  count="$(printf '%s\n' "$devices" | sed '/^$/d' | wc -l | tr -d ' ')"
  if [ "$count" = "0" ]; then
    die "no Windows_NTFS partition detected"
  fi
  if [ "$count" != "1" ]; then
    echo "Detected multiple NTFS partitions:" >&2
    printf '%s\n' "$devices" >&2
    die "pass --device diskXsY explicitly"
  fi
  printf '%s\n' "$devices"
}

diskutil_value() {
  local dev="$1"
  local key="$2"
  diskutil info "/dev/$dev" 2>/dev/null | awk -F: -v key="$key" '
    index($1, key) {
      sub(/^[ \t]+/, "", $2)
      print $2
      exit
    }
  '
}

mount_line_for() {
  local dev="$1"
  mount | grep -E "^/dev/${dev} on " || true
}

is_mounted_macy_writable() {
  local dev="$1"
  local line readonly
  line="$(mount_line_for "$dev")"
  readonly="$(diskutil_value "$dev" "Volume Read-Only")"
  [ -n "$line" ] && printf '%s\n' "$line" | grep -qi 'macfuse' && [ "$readonly" = "No" ]
}

console_user() {
  stat -f %Su /dev/console 2>/dev/null || printf '%s\n' "${SUDO_USER:-$(id -un)}"
}

print_status() {
  local dev="$1"
  echo "== Disk =="
  diskutil info "/dev/$dev" 2>/dev/null | sed -n '1,95p' || true
  echo
  echo "== Mount =="
  mount_line_for "$dev"
  echo
  echo "== Hasleo =="
  if launchctl print system/com.hasleo.NTFS4MacMounterService >/dev/null 2>&1; then
    launchctl print system/com.hasleo.NTFS4MacMounterService 2>/dev/null | sed -n '1,45p'
  else
    echo "Hasleo LaunchDaemon not registered"
  fi
  pgrep -fl 'Hasleo|NtfsMounter' || true
  echo
  echo "== macFUSE =="
  if kmutil showloaded 2>/dev/null | grep -qi 'macfuse'; then
    kmutil showloaded 2>/dev/null | grep -i 'macfuse'
  elif kextstat 2>/dev/null | grep -qi 'macfuse'; then
    kextstat 2>/dev/null | grep -i 'macfuse'
  else
    echo "macFUSE kext is not loaded"
  fi
}

try_load_macfuse() {
  if kmutil showloaded 2>/dev/null | grep -qi 'macfuse' || kextstat 2>/dev/null | grep -qi 'macfuse'; then
    return 0
  fi

  local loader="/Library/Filesystems/macfuse.fs/Contents/Resources/load_macfuse"
  if [ -x "$loader" ]; then
    "$loader" >/tmp/manual-ntfs-load-macfuse.log 2>&1 || true
  fi

  if kmutil showloaded 2>/dev/null | grep -qi 'macfuse' || kextstat 2>/dev/null | grep -qi 'macfuse'; then
    return 0
  fi

  echo "macFUSE is not loaded. Approve system software from developer Benjamin Fleischer in Privacy & Security, then restart if prompted." >&2
  [ -s /tmp/manual-ntfs-load-macfuse.log ] && cat /tmp/manual-ntfs-load-macfuse.log >&2
  return 1
}

write_test() {
  local mount_point="$1"
  local user test_path
  user="$(console_user)"
  test_path="$mount_point/.manual_ntfs_write_test_$(date +%s).txt"
  if [ "$(id -u)" = "0" ] && [ "$user" != "root" ]; then
    sudo -u "$user" sh -c "printf '%s\n' 'manual ntfs write test' > \"\$1\" && rm \"\$1\"" sh "$test_path"
  else
    printf '%s\n' 'manual ntfs write test' > "$test_path" && rm "$test_path"
  fi
}

remount_device() {
  local dev="$1"
  local mount_point="$2"
  local force="$3"
  local do_write_test="$4"

  [ "$(id -u)" = "0" ] || die "remount requires root; rerun with sudo or administrator privileges"
  [ -x "$MOUNTER" ] || die "Hasleo NtfsMounter not found or not executable at $MOUNTER"
  try_load_macfuse || exit 2

  if [ "$force" != "1" ] && is_mounted_macy_writable "$dev"; then
    echo "/dev/$dev is already mounted through macFUSE and writable"
    print_status "$dev"
    if [ "$do_write_test" = "1" ]; then
      local existing_mount_point
      existing_mount_point="$(diskutil_value "$dev" "Mount Point")"
      [ -n "$existing_mount_point" ] || existing_mount_point="$mount_point"
      echo "Running write test as console user..."
      write_test "$existing_mount_point" && echo "WRITE_TEST_OK"
    fi
    return 0
  fi

  echo "Unmounting /dev/$dev if mounted..."
  diskutil unmount "/dev/$dev" >/tmp/manual-ntfs-unmount.log 2>&1 || true
  sleep 1

  mkdir -p "$mount_point"
  echo "Mounting /dev/$dev at $mount_point with Hasleo NtfsMounter..."
  "$MOUNTER" -o allow_other "/dev/$dev" "$mount_point" >/tmp/manual-ntfs-mount.log 2>&1 &

  local i
  for i in 1 2 3 4 5 6 7 8 9 10; do
    sleep 1
    if mount_line_for "$dev" | grep -qi 'macfuse'; then
      break
    fi
  done

  local line readonly
  line="$(mount_line_for "$dev")"
  readonly="$(diskutil_value "$dev" "Volume Read-Only")"
  if ! printf '%s\n' "$line" | grep -qi 'macfuse' || [ "$readonly" != "No" ]; then
    echo "Mount did not become writable through macFUSE." >&2
    [ -s /tmp/manual-ntfs-mount.log ] && cat /tmp/manual-ntfs-mount.log >&2
    print_status "$dev"
    exit 3
  fi

  echo "Mounted writable:"
  printf '%s\n' "$line"
  diskutil info "/dev/$dev" | grep -E 'Mounted|Mount Point|Volume Read-Only|Media Read-Only|File System Personality|Type'

  if [ "$do_write_test" = "1" ]; then
    echo "Running write test as console user..."
    write_test "$mount_point" && echo "WRITE_TEST_OK"
  fi
}

main() {
  local command="status"
  if [ "$#" -gt 0 ]; then
    command="$1"
    shift
  fi
  if [ "$command" = "-h" ] || [ "$command" = "--help" ]; then
    usage
    exit 0
  fi

  local device="" mount_point="$DEFAULT_MOUNT_POINT" write_test_flag="0" force="0"
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --device)
        [ "$#" -ge 2 ] || die "--device needs a value"
        device="$2"
        shift 2
        ;;
      --mount-point)
        [ "$#" -ge 2 ] || die "--mount-point needs a value"
        mount_point="$2"
        shift 2
        ;;
      --write-test)
        write_test_flag="1"
        shift
        ;;
      --force)
        force="1"
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        die "unknown argument: $1"
        ;;
    esac
  done

  local dev
  dev="$(require_device "$device")"

  case "$command" in
    status)
      print_status "$dev"
      ;;
    remount)
      remount_device "$dev" "$mount_point" "$force" "$write_test_flag"
      ;;
    *)
      usage
      die "unknown command: $command"
      ;;
  esac
}

main "$@"
