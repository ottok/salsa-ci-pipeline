# Salsa CI pipeline jobs per Debian release

Salsa CI has historically been focused on testing packages prior to upload to
Debian unstable (sid), while testing packages prior to upload to other releases
has been a secondary feature. The purpose of this documentation is to establish
what jobs run, why and where, so we have a shared understanding of how the
pipeline morphs based on the `RELEASE` value and to faciliate planning future
changes in that behavior.

## How the RELEASE variable drives the pipeline

The target distribution is derived from the `debian/changelog` and it populates the value of `RELEASE` (unless explicitly overridden). The value of `RELEASE` makes the pipeline adapt to the target distribution.

Only three images are release-parameterised: `blhc:${RELEASE}`,
`generic_tests:${RELEASE}` and `lintian:${RELEASE}`. The Lintian image is built
per release on purpose, since Lintian evolves in lockstep with the Debian
release it is published in. When preparing updates to an older release, the
Lintian version from that release should be used, so the package is checked
against the policy of the release it is destined for.

### Release overlays

Not all releases are self-sufficient but must be activated on top of a full
release and hence called *release overlays*:

| RELEASE value | Bootstrapped suite | Overlay |
| --- | --- | --- |
| `experimental` | `DEFAULT_RELEASE` (unstable) | experimental |
| `<release>-backports` | `<release>` | backports |
| `<release>-updates` | `<release>` | updates |
| `<release>-security` | `<release>` | security |
| `<release>-proposed-updates` (Ubuntu) | `<release>` | proposed |

For `experimental` builds, sbuild uses the `aspcud` resolver so that build
dependencies are minimized; for `-backports` builds, `aptitude` is used instead.
Reverse-dependency builds follow the same rule and, by default, build the reverse
dependencies from unstable when `RELEASE=experimental` (see
`SALSA_CI_DISABLE_RATT_SBUILD_EXPERIMENTAL_ASPCUD`). The jobs that compare
against the archive (`debdiff`, the reverse-dependency jobs) additionally enable
the `-updates` and `-security` suites for `stable` and `oldstable`.

## Which jobs are mandatory

The `build` and `autopkgtest` jobs are the most important ones. They must always
pass, otherwise the package is visibly broken for users.

The next most important jobs are the variations of the build. Even if the most
basic amd64 binary build would pass, if the other builds are failing the package
will not migrate from Debian *unstable* to *testing* or from
`<release>-proposed` to `<release>`, and for any user needing those alternative
binary versions the package would be unusable. Lintian and Piuparts are also
essential and can reveal serious issues in the package, though they may also
error on minor issues that do not necessarily indicate that the package is
unusable, and thus these two are slightly lower in importance than autopkgtest.

The other jobs are relevant mainly for the new package versions. Debian
maintainers should strive to have these jobs pass in the next version going into
Debian unstable, and do the necessary build rule changes or patch the upstream
source code to improve the code quality.

Two mechanisms make a job unable to fail the pipeline: disabling it
(`SALSA_CI_DISABLE_*`), which removes it from the pipeline, and
`allow_failure: true`, which lets it run but stops it from failing the pipeline.
Either way the result does not depend on the job, so a non-blocking job is no
more mandatory than one that never runs. The tables below therefore use a single
*Mandatory* column: **✔** marks the jobs a maintainer has to keep green, and
**–** marks the jobs that are opt-in or non-blocking, where the pipeline passes
regardless. The only practical difference is reporting, since a non-blocking job
still produces logs and artifacts while a disabled job produces nothing at all.

Opt-in does not mean unimportant. Several jobs marked – are mandatory in
practice, but do not run by default because the shared runners or the required
infrastructure are not always available – notably the non-amd64 builds and the
cross-build. They can be enabled with the `SALSA_CI_ENABLE_*` /
`SALSA_CI_DISABLE_*` variables, as documented in the
[README](README.md#select-which-jobs-run-in-the-ci-pipeline).

## Jobs

These tables cover all Salsa CI jobs.

Unless a row says otherwise, *all releases* means every release the pipeline
builds images for: stretch, buster, bullseye, bookworm, bookworm-backports,
trixie, trixie-backports, forky, sid and experimental.

Build jobs run in a sid-based `build` image, one per architecture, and bootstrap
the build chroot for `$RELEASE` themselves with `sbuild --dist=${RELEASE}`. They
therefore support every release and every [release overlay](#release-overlays),
and need no `base` image.

### Build jobs

| Job | Mandatory | Releases |
| --- | --- | --- |
| build (amd64) | ✔ | all releases |
| build i386 | ✔ | all releases |
| build armel | – | all releases that ship armel |
| build armhf | – | all releases that ship armhf |
| build arm64 | – | all releases |
| build ppc64el | – | all releases that ship ppc64el |
| build riscv64 | – | all releases that ship riscv64 |
| build source | ✔ | all releases |
| build (faketime) | – | all releases |
| build i386 (faketime) | – | all releases |

The non-amd64 builds are mandatory whenever the package declares `Architecture:`
fields for those architectures, but are opt-in because the shared runners are
not always available. Enable them with, for example,
`SALSA_CI_DISABLE_BUILD_PACKAGE_ARM64: 0`.

### Build validation jobs

| Job | Mandatory | Releases |
| --- | --- | --- |
| test-build-any | ✔ | all releases |
| test-build-all | ✔ | all releases |
| test-build-twice | – | all releases |
| test-build-validate-cleanup | – | all releases |
| test-build-profiles | – | all releases |
| test-crossbuild-arm64 | – | the releases covered by crossqa.debian.net |

These jobs rebuild the package from the artifacts of the `build` job.
`test-crossbuild-arm64` is opt-in because cross-builds have a high failure rate
that is not suitable for a CI that is expected to be green and to gatekeep
commits, so it only covers what
[crossqa.debian.net](https://crossqa.debian.net/) supports. The job
`test-build-twice` is kept for backwards compatibility only; prefer
`test-build-validate-cleanup`, which validates the same thing without building
the package twice.

### autopkgtest jobs

| Job | Mandatory | Releases |
| --- | --- | --- |
| autopkgtest | ✔ | all releases except experimental |
| autopkgtest i386 | – | all releases except experimental |
| autopkgtest armel | – | all releases except experimental |
| autopkgtest armhf | – | all releases except experimental |
| autopkgtest arm64 | – | all releases except experimental |
| autopkgtest (faketime) | – | all releases except experimental |
| autopkgtest i386 (faketime) | – | all releases except experimental |

The autopkgtest images are built from the current stable release and are
release-independent. What limits autopkgtest to a given release is the
availability of the corresponding `lxc.tar` in the
[autopkgtest-lxc](https://salsa.debian.org/salsa-ci-team/autopkgtest-lxc)
project, which is built from the ci.debian.org LXC containers; there are none for
experimental. The i386 and ARM variants are opt-in because the shared runners
are not always available.

### Installation and archive quality jobs

| Job | Mandatory | Releases |
| --- | --- | --- |
| piuparts | ✔ | all releases |
| blhc | ✔ | all releases; arm64 only available for sid |
| missing-breaks | – | all releases |
| rc-bugs | – | all releases |
| debdiff | – | only packages with a previous version in Debian |

piuparts bootstraps its chroot for `$RELEASE` and runs the package's test suite
from it, so it supports every release. `missing-breaks` and `debdiff` are
non-blocking: they report their results but cannot fail the pipeline.
`missing-breaks` is additionally disabled by default, and its `allow_failure`
carries a `@TODO` to remove it once maintainers have had time to notice the job.
`debdiff` downloads the source package from the archive, so it only yields a
comparison for packages that already have a version uploaded to Debian, and
`$RELEASE` must be an archive suite.

### Reproducibility jobs

| Job | Mandatory | Releases |
| --- | --- | --- |
| debrebuild | ✔ | all releases |
| reprotest | – | all releases |
| atomic-reprotest | – | all releases |

debrebuild rebuilds the package from the `build` job's `.buildinfo` and compares
the result, writing a diffoscope report when the two differ. It is the only
mandatory job in this group, although it can fail randomly on packages that are
not yet fully reproducible, so a project may want to set `allow_failure: true`
on it. reprotest and atomic-reprotest analyze the build artifacts, the latter
with one job per reprotest variation; enable either with
`SALSA_CI_ENABLE_REPROTEST` or `SALSA_CI_ENABLE_ATOMIC_REPROTEST`.

### Source quality and metadata jobs

| Job | Mandatory | Releases |
| --- | --- | --- |
| lintian | ✔ | all releases |
| test-uscan | ✔ * | all releases |
| wrap-and-sort | – | all releases |
| licenserecon | – | all releases |

test-uscan only runs, and therefore only gates, when the package has a
`debian/watch` file. wrap-and-sort and licenserecon do not build the package, so
they run in a sid-based `generic_tests` image regardless of `$RELEASE`.

### Reverse dependency and publishing jobs

| Job | Mandatory | Releases |
| --- | --- | --- |
| generate-build-rdep-config | – | all releases |
| build-reverse-dependencies | – | all releases |
| aptly | – | all releases |

The reverse-dependency jobs are meant to be run on demand for specific
pipelines, not on every push. See
[Enable build reverse dependencies checking](README.md#enable-build-reverse-dependencies-checking).
aptly publishes the build artifacts to an apt repository.

The `extract-source` job, which used to prepare a debianized source tree in the
`provisioning` stage, is no longer defined by any recipe. Only the unused
`.provisioning-extract-source` template remains in
[salsa-ci.yml](salsa-ci.yml), together with the `SALSA_CI_DISABLE_EXTRACT_SOURCE`
variable and a stale `TODO` in [pipeline-jobs.yml](pipeline-jobs.yml).

## Release coverage of the Debian images

A dash (–) means that no image is built for that release and architecture
combination.

| Release | amd64 | i386 | armel | armhf | arm64 | ppc64el | riscv64 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| stretch | ✔ | ✔ | ✔ | ✔ | ✔ | – | – |
| buster | ✔ | ✔ | – | ✔ | ✔ | – | – |
| bullseye | ✔ | ✔ | – | ✔ | ✔ | – | – |
| bookworm | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | – |
| bookworm-backports | ✔ | ✔ | ✔ | ✔ | ✔ | – | – |
| trixie | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| trixie-backports | ✔ | ✔ | ✔ | ✔ | ✔ | – | – |
| forky | ✔ | ✔ | – | – | – | – | – |
| sid | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| experimental | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |

The remaining images are much narrower:

| Image | Releases | Architectures |
| --- | --- | --- |
| `blhc`, `generic_tests`, `lintian` | all releases | amd64 |
| `blhc`, `lintian`, `piuparts`, `reprotest`, `build` | sid | arm64 |
| `gbp`, `aptly`, `piuparts`, `reprotest` | sid | amd64 |
| `build` | sid | amd64, i386, armel, armhf, arm64, ppc64el, riscv64 |
| `autopkgtest` | current stable | amd64, i386, armel, armhf, arm64 |

These are the images relevant to the jobs above. The `base` images in the first
table are currently referenced by no job at all, so its gaps do not limit what
can be built; they are kept for projects that use them directly. The ARM,
PPC64EL and RISC-V image builds are only triggered on request (`when: manual`),
because the shared runners for those architectures are not always available. On
branches other than the default one, only a subset of these images is built (all
of them for sid, plus autopkgtest for the current stable release).

## Vendor profiles

The `RELEASE` variable is vendor-agnostic, and the pipeline is also used to test
packaging for distributions other than Debian. Each vendor ships a **recipe**
that a project includes instead of `recipes/debian.yml`, which pulls in the
shared `salsa-ci.yml` and `pipeline-jobs.yml` plus a vendor-specific **variable
profile** that narrows the job scope:

| Recipe | Vendor profile | Images |
| --- | --- | --- |
| [recipes/debian.yml](recipes/debian.yml) | – (Debian defaults) | [.images-debian.yml](.images-debian.yml) |
| [recipes/ubuntu.yml](recipes/ubuntu.yml) | [vars/ubuntu.yml](vars/ubuntu.yml) | [.images-ubuntu.yml](.images-ubuntu.yml) |
| [recipes/kali.yml](recipes/kali.yml) | [vars/kali.yml](vars/kali.yml) | [.images-kali.yml](.images-kali.yml) |
| – | – (eLxr) | [.images-elxr.yml](.images-elxr.yml) |

The profiles only pre-set `SALSA_CI_DISABLE_*` and `VENDOR`-related variables, so
a project using one of them starts with a considerably smaller set of jobs
without writing any `variables:` block itself. Because the values arrive through
an `include`, they behave like defaults: GitLab gives precedence to the file
that does the including, so a project can re-enable any of these jobs by setting
the variable in its own `debian/salsa-ci.yml`.

### Ubuntu

Ubuntu support is experimental. [vars/ubuntu.yml](vars/ubuntu.yml) sets
`VENDOR: ubuntu`, `DEFAULT_RELEASE` to an Ubuntu release and the mirror to
`archive.ubuntu.com`, and disables the QA jobs that do not apply to Ubuntu
packages: lintian, blhc, piuparts, debrebuild, debdiff, the `i386`, `any` and
`all` builds, and cross-builds.

[.images-ubuntu.yml](.images-ubuntu.yml) builds `base`, `lintian`, `blhc` and
`generic_tests` for amd64 on `resolute`, `questing`, `plucky`, `noble`, `jammy`
and `focal`, plus `base` and `blhc` for armhf and arm64. There are no `gbp`,
`aptly`, `autopkgtest`, `piuparts` or `reprotest` images, and no i386 images.
Note that the Lintian and blhc images *are* built for every Ubuntu release, yet
the corresponding jobs are disabled anyway: an available image does not imply an
enabled job.

### Kali

Kali maintains its own fork of the pipeline
([kalilinux/tools/kali-ci-pipeline](https://gitlab.com/kalilinux/tools/kali-ci-pipeline)),
so [recipes/kali.yml](recipes/kali.yml) points at that fork instead. Kali is a
rolling release: [vars/kali.yml](vars/kali.yml) pins `RELEASE` to `kali-dev`
rather than deriving it from `debian/changelog`, enables the `non-free` and
`non-free-firmware` components, and uses its own image registry and autopkgtest
LXC images. Rather than disabling most QA jobs, Kali marks `blhc`, `lintian` and
`reprotest` as `allow_failure: true`, so the maintainers still get the feedback
without the jobs gating their commits, and it suppresses the `no-manual-page`
and `orig-tarball-missing-upstream-signature` Lintian tags, which do not apply to
Kali packages.

[.images-kali.yml](.images-kali.yml) builds `base` and `generic_tests` for amd64
and i386 on `kali-rolling`, `kali-dev` and `kali-experimental`; `lintian`
additionally on the first two; and `aptly`, `autopkgtest`, `blhc`, `gbp`,
`piuparts` and `reprotest` on `kali-dev` only. There are no ARM, PPC64EL or
RISC-V images, and no `build` image: the build jobs use `SALSA_CI_IMAGES_BUILD`,
which resolves into Kali's own registry because `vars/kali.yml` overrides
`SALSA_CI_IMAGES`.

### eLxr

[.images-elxr.yml](.images-elxr.yml) is maintained by Wind River and builds a
subset of the Debian images (currently bookworm and sid) under the `debian`
vendor name. There is no eLxr recipe or variable profile, so eLxr does not
change the job scope; it only narrows which images are available.

### Mandatory jobs per vendor

The jobs that gate the pipeline with an unmodified configuration. A dash (–)
means the job is either disabled or non-blocking, and in both cases the pipeline
passes regardless of it. The jobs not listed are mandatory for no vendor, since
they are disabled by default everywhere.

| Job | Debian | Ubuntu | Kali |
| --- | --- | --- | --- |
| build (amd64) | ✔ | ✔ | ✔ |
| build source | ✔ | ✔ | ✔ |
| autopkgtest | ✔ | ✔ | ✔ |
| test-uscan | ✔ * | ✔ * | ✔ * |
| build i386 | ✔ | – | ✔ |
| test-build-any | ✔ | – | ✔ |
| test-build-all | ✔ | – | ✔ |
| lintian | ✔ | – | – |
| blhc | ✔ | – | – |
| piuparts | ✔ | – | ✔ |
| debrebuild | ✔ | – | – |

\* test-uscan only gates when the package has a `debian/watch` file.

Kali and Ubuntu end up with the same column, which is the point: Kali still runs
`lintian`, `blhc` and `reprotest`, and they still report their results, but they
are non-blocking, so they count as – here just like the jobs Ubuntu disables
outright.
