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
archive_path="${distribution_dir}/conan.tar.gz"
download_url="https://conan.omp.ru/distrib/conan/${conan_version}/${aurora_sdk_major_version}/conan-${conan_version}-${target_arch}.tar.gz"

if [[ ! -f "$rpm_macros" ]]; then
    mkdir -p -- "$distribution_dir" || rpm_error "Cannot create Conan cache directory"
    curl --fail --silent --show-error --location --output "$archive_path" "$download_url" || rpm_error "Failed to download Conan distribution"
    tar -xf "$archive_path" -C "$distribution_dir" || rpm_error "Failed to extract Conan distribution"
    rm -f -- "$archive_path"
    [[ -f "$rpm_macros" ]] || rpm_error "Conan distribution does not contain rpm-macros"
fi

printf '%%define __workspace_dir %s\n' "$workspace_dir"
printf '%%define __conan_version %s\n' "$conan_version"
printf '%%{load:%s}\n' "$rpm_macros"
