#!/bin/bash
# SPDX-FileCopyrightText: 2026 Open Mobile Platform LLC <community@omp.ru>
# SPDX-License-Identifier: BSD-3-Clause
# Adapted from the Aurora OS wakeword example and official Conan bootstrap.

set -eu

# RPM command substitutions can ignore a shell exit status. Emit an RPM error
# macro on failure so that an incomplete bootstrap cannot pass SPEC expansion.
rpm_error() {
    printf '%%{error:%s}\n' "$*"
    exit 1
}

if [[ -n "${SAILFISH_SDK_SRC1_MOUNT_POINT:-}" ]]; then
    workspace_dir=${SAILFISH_SDK_SRC1_MOUNT_POINT}
elif [[ "$(basename -- "${AURORA_SDK:-}")" == "aurora_psdk" ]]; then
    workspace_dir=${HOME}
elif [[ "${PWD}" == "/workspace" || "${PWD}" == "/workspace/"* ]]; then
    workspace_dir=/workspace
else
    rpm_error "Unknown Aurora SDK workspace environment"
fi

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
config_file="${script_dir}/version.config"
[[ -f "$config_file" ]] || rpm_error "Missing rpm/version.config"
source "$config_file"
[[ "${conan_version:-}" =~ ^2\.[0-9]+\.[0-9]+$ ]] || rpm_error "Invalid conan_version in rpm/version.config"

host_arch=$(uname -m)
target_arch=$host_arch
if [[ "$target_arch" == "armv7l" ]]; then
    target_arch=armv7hl
fi
aurora_sdk_version=$(awk -F= '$1 == "VERSION_ID" { gsub(/"/, "", $2); print $2 }' /etc/os-release)
aurora_sdk_major_version=${aurora_sdk_version%%.*}
[[ "$aurora_sdk_major_version" =~ ^[0-9]+$ ]] || rpm_error "Cannot determine Aurora SDK major version"

distribution_dir="${workspace_dir}/.cache/AuroraTools/${aurora_sdk_major_version}/conan/${conan_version}/${host_arch}"
rpm_macros="${distribution_dir}/rpm-macros"
complete_marker="${distribution_dir}/.bootstrap-complete"
download_url="https://conan.omp.ru/distrib/conan/${conan_version}/${aurora_sdk_major_version}/conan-${conan_version}-${target_arch}.tar.gz"

if [[ ! -f "$rpm_macros" || ! -f "$complete_marker" ]]; then
    cache_parent=$(dirname -- "$distribution_dir")
    mkdir -p -- "$cache_parent" || rpm_error "Cannot create Conan cache parent"
    lock_dir="${distribution_dir}.bootstrap-lock"
    mkdir -- "$lock_dir" 2>/dev/null || rpm_error "Conan cache is locked; retry after the other bootstrap exits. Remove a stale lock only after confirming no bootstrap is running: $lock_dir"
    stage_dir=""
    cleanup_bootstrap() {
        if [[ -n "$stage_dir" ]]; then
            if [[ ! -e "$distribution_dir" && ! -L "$distribution_dir" ]] &&
               [[ -e "${stage_dir}/previous" || -L "${stage_dir}/previous" ]]; then
                if ! mv -- "${stage_dir}/previous" "$distribution_dir"; then
                    printf 'Previous Conan cache retained for recovery at %s\n' "$stage_dir" >&2
                    rmdir -- "$lock_dir" 2>/dev/null || true
                    return
                fi
            fi
            rm -rf -- "$stage_dir"
        fi
        rmdir -- "$lock_dir" 2>/dev/null || true
    }
    trap cleanup_bootstrap EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM

    # Another bootstrap may have completed before we acquired the lock.
    if [[ ! -f "$rpm_macros" || ! -f "$complete_marker" ]]; then
        stage_dir=$(mktemp -d "${distribution_dir}.stage.XXXXXX") || rpm_error "Cannot create Conan staging directory"
        archive_path="${stage_dir}/conan.tar.gz"
        payload_dir="${stage_dir}/payload"
        mkdir -- "$payload_dir" || rpm_error "Cannot create Conan staging payload"
        curl --fail --silent --show-error --location --output "$archive_path" "$download_url" || rpm_error "Failed to download Conan distribution"
        tar -xf "$archive_path" -C "$payload_dir" || rpm_error "Failed to extract Conan distribution"
        [[ -f "${payload_dir}/rpm-macros" ]] || rpm_error "Conan distribution does not contain rpm-macros"
        touch "${payload_dir}/.bootstrap-complete" || rpm_error "Cannot mark Conan distribution complete"

        # Keep an old incomplete cache until the replacement is fully extracted.
        # Staging is on the same filesystem, so publishing uses a directory rename.
        if [[ -e "$distribution_dir" || -L "$distribution_dir" ]]; then
            mv -- "$distribution_dir" "${stage_dir}/previous" || rpm_error "Cannot move incomplete Conan cache"
        fi
        if ! mv -- "$payload_dir" "$distribution_dir"; then
            rpm_error "Cannot publish Conan distribution"
        fi
    fi
fi

printf '%%define __workspace_dir %s\n' "$workspace_dir"
printf '%%define __conan_version %s\n' "$conan_version"
printf '%%{load:%s}\n' "$rpm_macros"
