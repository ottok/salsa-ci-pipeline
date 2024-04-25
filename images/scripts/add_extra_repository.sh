#!/bin/bash
# Copyright salsa-ci-team and others
# SPDX-License-Identifier: FSFAP
# Copying and distribution of this file, with or without modification, are
# permitted in any medium without royalty provided the copyright notice and
# this notice are preserved. This file is offered as-is, without any warranty.

# Add an extra apt repository sources.list if the extra-repository argument is
# set and an extra deb822 sources file if extra-repository-sources is set.
# The extra-repository, extra-repository-key and extra-repository-sources
# arguments are filenames.
# The optional target-etc argument allows setting a different destination path
# to be able to update chroots.

SALSA_CI_EXTRA_REPOSITORY=""
SALSA_CI_EXTRA_REPOSITORY_KEY=""
SALSA_CI_EXTRA_REPOSITORY_SOURCES=""
TARGET_ETC="/etc"
VERBOSE=0

while [[ "$#" -ge 1 ]]; do
    case "$1" in
        --extra-repository|-e)
            shift
            SALSA_CI_EXTRA_REPOSITORY="$1"
            shift
            ;;
        --extra-repository-key|-k)
            shift
            SALSA_CI_EXTRA_REPOSITORY_KEY="$1"
            shift
            ;;
        --extra-repository-sources|-s)
            shift
            SALSA_CI_EXTRA_REPOSITORY_SOURCES="$1"
            shift
            ;;
        --target-etc|-t)
            shift
            TARGET_ETC="$1"
            shift
            ;;
        --verbose|-v)
            VERBOSE=1
            shift
            ;;
        *)
            echo "Unkown argument $1"
            exit 1
            ;;
    esac
done

if [[ "$VERBOSE" -ne 0 ]]; then
    set -x
fi

if [[ -n "${SALSA_CI_EXTRA_REPOSITORY}" ]] ||
        [[ -n "${SALSA_CI_EXTRA_REPOSITORY_SOURCES}" ]]; then
    mkdir -p "${TARGET_ETC}"/apt/sources.list.d/
    if [[ -n "${SALSA_CI_EXTRA_REPOSITORY_SOURCES}" ]]; then
        cp "${SALSA_CI_EXTRA_REPOSITORY_SOURCES}" \
            "${TARGET_ETC}"/apt/sources.list.d/extra_repository.sources
    fi
    if [[ -n "${SALSA_CI_EXTRA_REPOSITORY}" ]]; then
        cp "${SALSA_CI_EXTRA_REPOSITORY}" \
            "${TARGET_ETC}"/apt/sources.list.d/extra_repository.list
        if [[ -n "${SALSA_CI_EXTRA_REPOSITORY_KEY}" ]]; then
            mkdir -p "${TARGET_ETC}"/apt/trusted.gpg.d/
            cp "${SALSA_CI_EXTRA_REPOSITORY_KEY}" \
                "${TARGET_ETC}"/apt/trusted.gpg.d/extra_repository.asc
        fi
    fi
    apt-get update
    apt-get upgrade --assume-yes
    apt-get --assume-yes install ca-certificates
fi

