# Salsa CI – Quality Assurance for Debian packaging

## TL;DR

This Salsa CI pipeline increases the quality of Debian packages by providing
[Continuous Integration](https://about.gitlab.com/product/continuous-integration/)
that can be run on every commit on any Debian package.

To activate Salsa CI, open settings at `https://salsa.debian.org/TEAM/PROJECT/-/settings/ci_cd`,
and in _General pipelines_ set the project _CI/CD configuration file_ to
`debian/salsa-ci.yml`, and on the Debian packaging git branch create the file
containing:

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml
```

## Table of contents

* [Benefits – Why use Salsa CI?](#benefits--why-use-salsa-ci)
* [Activate Salsa CI](#activate-salsa-ci)
  * [Enable feature 'CI/CD' in Settings](#enable-feature-cicd-in-settings)
  * [Include Salsa CI in an existing GitLab CI pipeline](#include-salsa-ci-in-an-existing-gitlab-ci-pipeline)
* [Customize Salsa CI](#customize-salsa-ci)
  * [Select which jobs run in the CI pipeline](#select-which-jobs-run-in-the-ci-pipeline)
  * [Allow a job to fail](#allow-a-job-to-fail)
  * [Disable the pipeline on certain branches](#disable-the-pipeline-on-certain-branches)
  * [Allow pipeline to run when git tags are pushed](#allow-pipeline-to-run-when-git-tags-are-pushed)
  * [Setting variables on pipeline creation](#setting-variables-on-pipeline-creation)
  * [Run only selected jobs](#run-only-selected-jobs)
* [Customize builds and build dependencies](#customize-builds-and-build-dependencies)
  * [Set build timeout](#set-build-timeout)
  * [Disabling building on i386](#disabling-building-on-i386)
  * [Enable building on ARM and RISC-V](#enable-building-on-arm-and-risc-v)
  * [Testing build of arch=any and arch=all packages](#testing-build-of-archany-and-archall-packages)
  * [Testing build profiles](#testing-build-profiles)
  * [Enable building packages twice in a row](#enable-building-packages-twice-in-a-row)
  * [Enable generation of dbgsym packages](#enable-generation-of-dbgsym-packages)
  * [Build with non-free dependencies](#build-with-non-free-dependencies)
  * [Add private repositories to the builds](#add-private-repositories-to-the-builds)
  * [Add extra arguments to dpkg-buildpackage](#add-extra-arguments-to-dpkg-buildpackage)
  * [Adding extra arguments to gbp-buildpackage](#adding-extra-arguments-to-gbp-buildpackage)
  * [Git attributes](#git-attributes)
  * [Customize reprotest](#customize-reprotest)
* [Lintian, Autopkgtests, Piuparts and other quality assurance CI jobs](#lintian-autopkgtests-piuparts-and-other-quality-assurance-ci-jobs)
  * [Customize Lintian](#customize-lintian)
  * [Make autopkgtest more strict](#make-autopkgtest-more-strict)
  * [Add extra arguments to autopkgtest](#add-extra-arguments-to-autopkgtest)
  * [Avoid autopkgtest failures on systemd masked tmp](#avoid-autopkgtest-failures-on-systemd-masked-tmp)
  * [Run a pre-install / post-install script in piuparts](#run-a-pre-install--post-install-script-in-piuparts)
  * [Using automatically built apt repository](#using-automatically-built-apt-repository)
  * [Enable wrap-and-sort job](#enable-wrap-and-sort-job)
  * [Debian release bump](#debian-release-bump)
* [Distribution and release selection](#distribution-and-release-selection)
  * [Customise what Debian release to use](#customise-what-debian-release-to-use)
  * [Experimental: Ubuntu support](#experimental-ubuntu-support)
* [General Debian packaging support and resources](#general-debian-packaging-support-and-resources)
* [General Salsa information](#general-salsa-information)
* [Support for Salsa CI use](#support-for-salsa-ci-use)
* [Contributing](#contributing)


## Benefits – Why use Salsa CI?

The official building and testing performed by Debian QA is run asynchronously
and takes a long time to provide feedback because it is only accessible after
pushing a release to the archive. Any issues with the package will be flagged,
but remain broken and may cause havoc until a fixed version is uploaded.

The Salsa CI pipeline mimics the tests that are run after each upload to Debian,
but instead of having to wait for results or risk the health of the Debian
repositories, Salsa CI provides you with instant feedback about any problems the
changes you made may have created or solved.

Salsa CI currently offers:

* Building the package from the source using
  [git-buildpackage](https://manpages.debian.org/unstable/git-buildpackage/git-buildpackage.1.en.html)
  with multiple build profiles and architectures
* Static analysis for Debian packages using [Lintian](https://lintian.debian.org)
* Functional testing using [Autopkgtest](https://salsa.debian.org/ci-team/autopkgtest/raw/master/doc/README.package-tests.rst)
* Package installation and removal testing using [Piuparts](https://piuparts.debian.org)
* Checking proper use of secure build flags etc using [Buildd Log Scanner](https://qa.debian.org/bls/)
* Build reproducibility testing using [Reprotest](https://reproducible-builds.org/tools)

## Activate Salsa CI

### Enable feature 'CI/CD' in Settings

To use the Salsa Pipeline, the first thing to do is to enable the project's
Pipeline. Go to `Settings` (General), expand `Visibility, project features,
permissions`, and in `Repository`, enable `CI/CD`. This makes the `CI/CD`
settings and menu available. Then, change the project's setting to make it point
to the pipeline's config file. This can be done on `Settings` ⇾ `CI/CD`,
expand `General Pipelines` and update the field `CI/CD configuration file`.

It is recommended to set this value to `debian/salsa-ci.yml` and create the file
containing at least the following lines:

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml
```

If creating a new file is too much hassle, and there is no need to modify it,
the alternative way is to just set `recipes/debian.yml@salsa-ci-team/pipeline`
as the config path, which refers to a file kept in the `salsa-ci-team/pipeline`
repository.

> :warning: **Note:** The pipeline is not run automatically after configuring
> it. You can either trigger it by
> [running the pipeline manually](https://salsa.debian.org/help/ci/pipelines/index.md#run-a-pipeline-manually)
> or pushing something.

### Alternatively use command-line tools `salsa` or `glab`

If you wish to activate Salsa CI directly from the command-line, set up the
[salsa](https://manpages.debian.org/unstable/devscripts/salsa.1.en.html) tool
and run this for all your projects:

```shell
salsa update_projects $NAMESPACE/$PROJECT \
  --jobs yes --ci-config-path recipes/debian.yml@salsa-ci-team/pipeline
```

Alternatively, use the more generic command-line tool
[glab](https://manpages.debian.org/unstable/glab/glab.1.en.html) which works for
any GitLab instance.

### Include Salsa CI in an existing GitLab CI pipeline

If your project already has a GitLab pipeline, you can add Salsa CI in the
`.gitlab-ci.yml` file as an additional child pipeline with:

```yaml
stage: package
trigger:
  include: debian/salsa-ci.yml
  strategy: depend
rules:
  - if: $CI_COMMIT_TAG != null
    when: never
```

#### Don't run Salsa CI on every commit

If you don't want to run Salsa CI on every commit, you can add custom `rules`
to trigger the Salsa CI pipeline only manually or for example when a scheduled
pipeline run takes place. The typical use case is when maintaining native Debian
packages where the program code is tested on every git commit, and the commits
are frequent, while the packaging needs to be tested only infrequently.

```yaml
stage: package
trigger:
  include: debian/salsa-ci.yml
  strategy: depend
    # run if user manually presses the "play" icon on pipeline
    - if: $CI_PIPELINE_SOURCE == "web"
      when: manual
    # run during for scheduled pipeline runs
    - if: $CI_PIPELINE_SOURCE == "schedule"
      when: always
    # never allow other pipeline sources to trigger running this job
    - when: never
```


## Customize Salsa CI

Salsa CI is designed to as-is for the vast majority of Debian packages. In most
cases Salsa CI should be used without any customizations. However, for packages
that need it, Salsa CI offers many ways to customize how it runs and what it
runs.

The easiest way to grasp the possibilities is to browse various examples of Salsa CI
being used on prominent Debian packages, from simple to complex:

* https://salsa.debian.org/sudo-team/sudo/-/blob/master/debian/salsa-ci.yml
* https://salsa.debian.org/mariadb-team/mariadb-server/-/blob/debian/latest/debian/salsa-ci.yml
* https://salsa.debian.org/kernel-team/linux/-/blob/master/debian/salsa-ci.yml

Salsa CI offers a wide range of variables that can be used to easily turn on/off
certain features or customize how they behave.

It is even possible to only include the
[`salsa-ci.yml`](https://salsa.debian.org/salsa-ci-team/pipeline/blob/master/salsa-ci.yml)
template for jobs definitions without adding any jobs to the pipeline from
[`pipeline-jobs.yml`](https://salsa.debian.org/salsa-ci-team/pipeline/blob/master/pipeline-jobs.yml).

For an example of a very customized CI pipeline, one can have a look at the
[Debian's Linux kernel salsa-ci.yml](https://salsa.debian.org/kernel-team/linux/-/blob/master/debian/salsa-ci.yml),
which starts like this:

```yaml
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/salsa-ci.yml

# jobs are defined below ...
```

### Select which jobs run in the CI pipeline

There are several ways to skip a certain job. The recommended way is to set to
`1` (or "`yes`" or "`true`") the `SALSA_CI_DISABLE_*` variables that have been
created for this purpose.

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

# This sample disables all default tests, only disable those that you
# don't want
variables:
  SALSA_CI_DISABLE_APTLY: 1
  SALSA_CI_DISABLE_AUTOPKGTEST: 1
  SALSA_CI_DISABLE_BLHC: 1
  SALSA_CI_DISABLE_LINTIAN: 1
  SALSA_CI_DISABLE_PIUPARTS: 1
  SALSA_CI_DISABLE_REPROTEST: 1
  SALSA_CI_DISABLE_BUILD_PACKAGE_ALL: 1
  SALSA_CI_DISABLE_BUILD_PACKAGE_ANY: 1
  SALSA_CI_DISABLE_BUILD_PACKAGE_I386: 1
  SALSA_CI_DISABLE_CROSSBUILD_ARM64: 1
```

Alternatively, it is possible to disable all tests, and then enable only the
ones you want, which is good when testing a specific test:

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

# This sample disables all default tests, and then enables just autopkgtest
variables:
  SALSA_CI_DISABLE_ALL_TESTS: 1
  SALSA_CI_ENABLE_AUTOPKGTEST: 1
```

### Allow a job to fail

Without completely disabling a job, you can allow it to fail without failing the
whole pipeline. That way, if the job fails, the pipeline will pass and show an
orange warning telling you something went wrong.

For example, even though reproducible builds are important, `reprotest`'s
behaviour can sometimes be a slightly flaky and fail randomly on packages that
aren't totally reproducible (yet!). In such case, you can allow `reprotest` to
fail by adding this variable in your salsa-ci.yml manifest:

```
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

reprotest:
  allow_failure: true
```

### Disable the pipeline on certain branches

It is possible to configure the pipeline to skip branches you don't want CI to
run on. The `SALSA_CI_IGNORED_BRANCHES` variable can be set to a regex that will
be compared against the ref name and will decide if a pipeline is created.

By default, pipelines are only created for branches that contain a `debian/` folder.

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_IGNORED_BRANCHES: 'some-branch|another-ref'
```

### Allow pipeline to run when git tags are pushed

By default, the pipeline is run only for commits, tags are ignored. To run the
pipeline against tags as well, export the `SALSA_CI_ENABLE_PIPELINE_ON_TAGS`
variable and set it to one of "1", "yes" or "true", like in the following
example:

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_ENABLE_PIPELINE_ON_TAGS: 1
```

### Setting variables on pipeline creation

You can set these and other similar variables when launching a new pipeline in different ways:

* Using the web interface under CI/CD, Run Pipeline, and setting the desired
  variables.
* Using the [GitLab API](https://salsa.debian.org/help/api/index.md). For
  example,  check the script
  [salsa_drive_build.py](https://salsa.debian.org/maxy/qt-kde-ci/blob/tooling/salsa_drive_build.py),
  in particular the function
  [launch_pipelines](https://salsa.debian.org/maxy/qt-kde-ci/blob/tooling/salsa_drive_build.py#L568).
* Setting them as part of a pipeline-triggered build.

### Skip pipeline temporairly when running a `git push`

There may be reasons to skip the whole pipeline for a `git push`, for example
when you are adding `salsa-ci.yml` to hundreds of repositories or doing other
mass changes.

You can achieve this in two ways:

You can insert `[ci skip]` or `[skip ci]`, using any capitalization, in the
commit message. With this marker, GitLab will not run the pipeline when the
commit is pushed.

Alternatively, one can pass the `ci.skip` [Git push](https://git-scm.com/docs/git-push#Documentation/git-push.txt--oltoptiongt)
option if using Git 2.10 or newer:

```
git push --push-option=ci.skip    # using git 2.10+
git push -o ci.skip               # using git 2.18+
```

See also https://salsa.debian.org/help/ci/pipelines/index.md#skip-a-pipeline

### Run only selected jobs

If you want to use the definitions provided by the Salsa CI Team, but want to
explicitly define which jobs to run, you might want to declare your YAML as
follows:

```yaml
---
include: https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/salsa-ci.yml

extract-source:
    extends: .provisioning-extract-source

variables:
  RELEASE: 'experimental'

build:
  extends: .build-package

test-build-any:
  extends: .test-build-package-any

test-build-all:
  extends: .test-build-package-all

test-crossbuild-arm64:
  extends: .test-crossbuild-package-arm64

reprotest:
  extends: .test-reprotest

lintian:
  extends: .test-lintian

autopkgtest:
  extends: .test-autopkgtest

blhc:
  extends: .test-blhc

piuparts:
  extends: .test-piuparts

aptly:
  extends: .publish-aptly
```

On the previous example, the package is built on Debian experimental and checked
through on all tests currently provided. You can choose to run only some of the
jobs by deleting any of the definitions above.

As new changes are expected to happen from time to time, we **firmly recommend
NOT to do define all jobs manually**. Most of the time it is better to simply
[select which jobs run in the CI pipeline](#select-which-jobs-run-in-the-ci-pipeline).


## Customize builds and build dependencies

### Set build timeout

At times your job may fail because it reached its max duration (either job
timeout, or runner timeout). In that case, the job would stop immediately
without entering the `after_script` phase, and without saving the cache and
without saving the artifacts.

To prevent this, the build phase of the build job and the build phase of the
reprotest job have a timeout of `2.75h` (the runner's timeout is 3h). This
permits also saving the cache of `ccache`. That way, on the next run, there is
more chance to finish the job since it can use ccache's cache.

You can set the `SALSA_CI_BUILD_TIMEOUT_ARGS` variable to override this. The
arguments can be any valid argument used by the `timeout` command. For example,
you may set:

```
variables:
  SALSA_CI_BUILD_TIMEOUT_ARGS: "0.75h"
```

### Disabling building on i386

The `build i386` job builds packages against the 32-bit x86 architecture. If for
any reason you need to skip this job, set the `SALSA_CI_DISABLE_BUILD_PACKAGE_I386`
in the variables' block to `1`, '`yes`' or '`true`'.  i.e;

```yaml

variables:
  SALSA_CI_DISABLE_BUILD_PACKAGE_I386: 1
```

### Enable building on ARM and RISC-V

Salsa CI includes builds jobs for armel, armhf, arm64 and riscv64. They are
disabled by default, but can be enabled if a project has a GitLab runner on
arm64 hardware available and tagged `arm64`, or on RISC-V tagged `riscv64`.

If you know you have such a runner available, you can activate ARM or RISC-V
build respectively by setting the related variables to anything different than
1, 'yes' or 'true':

```yaml
variables:
  SALSA_CI_DISABLE_BUILD_PACKAGE_ARM64: 0
  SALSA_CI_DISABLE_BUILD_PACKAGE_ARMEL: 0
  SALSA_CI_DISABLE_BUILD_PACKAGE_ARMHF: 0
  SALSA_CI_DISABLE_BUILD_PACKAGE_RISCV64: 0
```

All Debian Developers can enable `salsaci-arm64-runner-01.debian.net` or
`salsaci riscv64 runner 01` in any project.

Contributors who fork the project might not have runners tagged `arm64` or
`riscv64` in their project. The example below illustrates how to limit the
special build jobs to the `debian` project name space with extra `rules`:

```yaml
build arm64:
  extends: .build-package-arm64
  rules:
    - if: $CI_PROJECT_ROOT_NAMESPACE  == "debian"

build armel:
  extends: .build-package-armel
  rules:
    - if: $CI_PROJECT_ROOT_NAMESPACE  == "debian"

build armhf:
  extends: .build-package-armhf
  rules:
    - if: $CI_PROJECT_ROOT_NAMESPACE  == "debian"

build riscv64:
  extends: .build-package-riscv64
  rules:
    - if: $CI_PROJECT_ROOT_NAMESPACE  == "debian"
```

If you want to add more architectures or for other reasons have your own
runners, see [Adding new runners for Salsa CI](RUNNERS.md).

### Testing build of arch=any and arch=all packages

If your package contains binary packages for `all` or `any`, you may want to
test if those can be built in isolation from the full build normally done.

This verifies the Debian buildds can build your package correctly when building
for other architectures that the one you uploaded in or in case a binNMU is
needed or you want to do source-only uploads.

The default `pipeline-jobs.yml` does this automatically based on the contents of
`debian/control`, but if you manually define the jobs to run, you also need to
include the `test-build-any` and `test-build-all` jobs manually as well:

```yaml
test-build-any:
  extends: .test-build-package-any

test-build-all:
  extends: .test-build-package-all
```

`.test-build-package-any` runs `dpkg-buildpackage` with the option `--build=any`
and will only build arch-specific packages.

`.test-build-package-all` does the opposite and runs `dpkg-buildpackage` with
the option `--build=all` building only arch-indep packages.

### Testing build profiles

As its name suggests, the `test-build-profiles` job makes it possible to easily
test specific build profiles. This job is disabled by default, so you need to
enable it manually and set the profile(s) in the `BUILD_PROFILES` variable as a
comma-separated list. For example:

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_ENABLE_BUILD_PACKAGE_PROFILES: 1
  BUILD_PROFILES: nocheck,nodoc
```

Also, it is also possible to run several jobs in parallel to test different
profiles independently:

```yaml
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_ENABLE_BUILD_PACKAGE_PROFILES: 1

test-build-profiles:
  extends: .test-build-package-profiles
  parallel:
    matrix:
      - BUILD_PROFILES: nocheck
      - BUILD_PROFILES: nodoc
```

### Enable building packages twice in a row

The job `test-build-twice` can be used to check whether it is possible to run
`dpkg-buildpackage` twice in a row. To enable this check, either run your
pipeline manually with `SALSA_CI_DISABLE_BUILD_PACKAGE_TWICE` set to anything
different than 1, 'yes' or 'true' or by adding the following to your
`debian/salsaci.yml`:

```yaml
variables:
  SALSA_CI_DISABLE_BUILD_PACKAGE_TWICE: 0
```

### Enable generation of dbgsym packages

To reduce the size of the artifacts produced by the build jobs, auto-generation
of dbgsym packages is disabled by default. This behaviour can be controlled by
the `SALSA_CI_DISABLE_BUILD_DBGSYM`. Set it to anything different than 1, 'yes'
or 'true', to generate those packages.

```yaml
variables:
  SALSA_CI_DISABLE_BUILD_DBGSYM: 0
```

### Build with non-free dependencies

By default, only `main` repositories are used. If your package has dependencies
or build-dependencies in the `contrib` or `non-free` components (archive areas),
set `SALSA_CI_COMPONENTS` to indicate this:

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
    RELEASE: 'stretch'
    SALSA_CI_COMPONENTS: 'main contrib non-free'
```

This is currently used for `piuparts`, but is likely to be used for
other stages in future.

It is possible to use the `SALSA_CI_EXTRA_REPOSITORY` support to add a
suitable apt source to the build environment and allow builds to access
build-dependencies from contrib and non-free. You will need permission
to modify the Salsa Settings for the project.

The CI/CD settings are at a URL like:

`https://salsa.debian.org/<team>/<project>/-/settings/ci_cd`
Expand the section on Variables and add a **File** type variable:

> Key: SALSA_CI_EXTRA_REPOSITORY

> Value: deb [signed-by=/usr/share/keyrings/debian-archive-keyring.gpg] https://deb.debian.org/debian/ sid contrib non-free

The apt source should reference `sid` or `unstable`.

Many `contrib` and `non-free` packages only build on `amd64`, so the
32-bit x86 build (`build i386`) should be disabled. (refer to the
[Disabling building on i386](#Disabling-building-on-i386) Section).

### Add private repositories to the builds

The variables `SALSA_CI_EXTRA_REPOSITORY` and `SALSA_CI_EXTRA_REPOSITORY_KEY`
can be used to add private apt repositories to the sources.list, to be used by
the build and tests, and (optionally) the signing key for the repositories in
armor format. Alternatively, the single variable `SALSA_CI_EXTRA_REPOSITORY_SOURCES`
 can be used to add an extra repository (with its corresponding signing key) in
 deb822-style format (which is conveniently rendered by the aptly job). These
 variables are of [type file](https://salsa.debian.org/help/ci/variables/index.md#cicd-variable-types),
 which eases the multiline handling, but have the disadvantage that their
 content can't be set on the salsa-ci.yml file - but they can be added to the
 repository as files and have their filenames then set in the salsa-ci.yml file:

```yaml
---
include: https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/salsa-ci.yml

variables:
  SALSA_CI_EXTRA_REPOSITORY: debian/ci/extra_repository.list
  SALSA_CI_EXTRA_REPOSITORY_KEY: debian/ci/extra_repository.asc
  # or
  SALSA_CI_EXTRA_REPOSITORY_SOURCES: debian/ci/extra_repository.sources
```

See also
[Using automatically built apt repository](#using-automatically-built-apt-repository)

### Add extra arguments to dpkg-buildpackage

Sometimes it is desirable to add direct options to the dpkg-buildpackage that is
run for the package building.

You can do this using the `SALSA_CI_DPKG_BUILDPACKAGE_ARGS` variable.

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_DPKG_BUILDPACKAGE_ARGS: --your-option
```

### Adding extra arguments to gbp-buildpackage

Sometimes it is desirable to add direct options to the `gbp buildpackage` command.

You can do this using the `SALSA_CI_GBP_BUILDPACKAGE_ARGS` variable.

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_GBP_BUILDPACKAGE_ARGS: --your-option
```

### Git attributes

Some upstream projects ship a `.gitattributes` file to set up special
attributes to specific paths. To properly handle those path attributes, the
Salsa CI's pipeline relies on `gbp setup-gitattributes`, that is call after
fetching all the required branches from the repository.  See `gitattributes(5)`
and `gbp-setup-gitattributes(1)`, and
[#322](https://salsa.debian.org/salsa-ci-team/pipeline/-/issues/322). If `gbp
setup-gitattributes` is causing trouble (such as staging changes or encoding
inconsistencies), the `gbp setup-gitattributes` call can be disabled setting
the `SALSA_CI_DISABLE_GBP_SETUP_GITATTRIBUTES` variable to 1, 'yes' or 'true':

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/salsa-ci.yml
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/pipeline-jobs.yml

variables:
  SALSA_CI_DISABLE_GBP_SETUP_GITATTRIBUTES: 1
```

### Customize reprotest

The `reprotest` job runs with the `time` (see below) and `build_path`
variations disabled by default. To save memory usage, it also runs with
`diffoscope` disabled. This behaviour can be modified as explained here below.

#### Faketime is currently disabled

Note that reprotest's faketime support is currently disabled, as it causes false
positives on files touched by quilt. It will be re-enabled once this is fixed.
https://salsa.debian.org/salsa-ci-team/pipeline/-/issues/251

#### Add extra arguments to reprotest

Sometimes it is desirable to disable (or enable) some `reprotest` validations
because the reproducibility issue comes inherently from the programming
language being used, and not from the code being packaged.

You can customize the variations tested by `reprotest` by adding extra parameters
in the `SALSA_CI_REPROTEST_ARGS` variable.
For example, some compilers embed the build path in the generated binaries. As
mentioned above, the `build_path` variation is disabled by default, but if you
still want to test it, you can enable it as shown below.
Please refer to `reprotest(1)` to find more information about the variations
available.

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_REPROTEST_ARGS: --vary=+build_path
```

#### Run reprotest with diffoscope

Reprotest stage can be run with [diffoscope](https://try.diffoscope.org/), which
is an useful tool that helps identifying reproducibility issues. Large projects
will not pass on low resources runners as the ones available right now.

To enable diffoscope, setting `SALSA_CI_REPROTEST_ENABLE_DIFFOSCOPE` to 1 (or
'yes' or 'true') is needed.

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_REPROTEST_ENABLE_DIFFOSCOPE: 1
```

#### Break up the reprotest job into the different variations

By default, reprotest applies all the known variations together (see the full
list at
[reprotest(1)](https://manpages.debian.org/unstable/reprotest/reprotest.1.en.html)).
One way to debug a failing reprotest job and find out what variations are
producing unreproducibility issues is to run the variations independently.

If you want to run multiple reprotest jobs, one for each variation, set the
`SALSA_CI_ENABLE_ATOMIC_REPROTEST` variable to 1, 'yes' or 'true':

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_ENABLE_ATOMIC_REPROTEST: 1
```

You can also set the `SALSA_CI_ENABLE_ATOMIC_REPROTEST` variable when
triggering the pipeline, without the need of creating a specific commit.


## Lintian, Autopkgtests, Piuparts and other quality assurance CI jobs

### Customize Lintian

The Lintian job can be customized to ignore certain tags.

To ignore a tag, add it to the setting `SALSA_CI_LINTIAN_SUPPRESS_TAGS`.

By default, the Lintian jobs fail either if a Lintian run-time error occurs or
if Lintian finds a tag of the error category.

To also fail the job on findings of the category warning, set
`SALSA_CI_LINTIAN_FAIL_WARNING` to 1 (or "yes" or "true").

To make Lintian shows overridden tags, set `SALSA_CI_LINTIAN_SHOW_OVERRIDES` to
1 (or "yes" or "true").

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_LINTIAN_FAIL_WARNING: 1
  SALSA_CI_LINTIAN_SUPPRESS_TAGS: 'orig-tarball-missing-upstream-signature'
```

It is possible to add any other lintian argument using `SALSA_CI_LINTIAN_ARGS`.
Those arguments will be appended after the arguments generated by the pipeline.

### Make autopkgtest more strict

By default, the autopkgtest job will succeed if autopkgtest exits with status
0, 2 or 8. If you would like the autopkgtest job to only succeed if all tests
pass and fail otherwise, you can restrict success to exit status 0 by writing:

```yaml
variables:
  SALSA_CI_AUTOPKGTEST_ALLOWED_EXIT_STATUS: '0'
```

To allow multiple exit codes, separate them by comma.

### Add extra arguments to autopkgtest

Sometimes it is desirable to add arguments to autopkgtest.

You can do this by setting the arguments in the `SALSA_CI_AUTOPKGTEST_ARGS`
variable.

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_AUTOPKGTEST_ARGS: '--debug'
```

Note that autopkgtest can access the repository in the current directory, making
it possible for `--setup-commands` to read commands from a file. For example:

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_AUTOPKGTEST_ARGS: '--setup-commands=ci/pin-django-from-backports.sh'
```

### Avoid autopkgtest failures on systemd masked tmp

If an autopkgtest fail with:

```shell
$> systemctl restart myservice
Failed to restart myservice.service: Unit tmp.mount is masked.
```
The error is probably due to bug [#1078157](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1078157).

You could workaround by adding at the top of the autopkgtest:

```shell
SERVICE=myservice
mkdir -p /run/systemd/system/$SERVICE.service.d
tee /run/systemd/system/$SERVICE.service.d/disabletmp.conf << "EOF"
[Service]
PrivateTmp=no
EOF
systemctl daemon-reload
```

### Run a pre-install / post-install script in piuparts

Sometimes it is desirable to execute a pre-install or post-install scripts in
piuparts.

You can do this using the `SALSA_CI_PIUPARTS_PRE_INSTALL_SCRIPT` and
`SALSA_CI_PIUPARTS_POST_INSTALL_SCRIPT` variables, that may point to the path of
scripts in the project repository. This could be used, for instance, to pin
dependencies. For example, if you had a `ci/pin-django-from-backports.sh`
script:

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_PIUPARTS_PRE_INSTALL_SCRIPT: 'ci/pin-django-from-backports.sh'
```

The `ci/pin-django-from-backports.sh`:

```shell
#!/bin/sh

set -e

# Ensure that python3-django from bullseye-backports will be
# installed as needed (bullseye has too old version)
cat >/etc/apt/preferences.d/99django-backports <<EOT
Package: python3-django
Pin: release a=bullseye-backports
Pin-Priority: 900
EOT
```

### Using automatically built apt repository

The [Aptly](https://www.aptly.info/) task runs in the publish stage and will
save published apt repository files as its artifacts, so downstream CI tasks may
access built binary/source packages directly through artifacts url via apt. This
is currently disabled by default. To enable it, set the `SALSA_CI_DISABLE_APTLY`
variable of the repository whose artifacts you want to use to anything other
than `1`, '`yes`' or '`true`'. (check example below)

To specify repository signing key, export the gpg key/passphrase as CI / CD
[Variables](https://salsa.debian.org/help/ci/variables/index.md)
`SALSA_CI_APTLY_GPG_KEY` and `SALSA_CI_APTLY_GPG_PASSPHRASE`. Otherwise, an
automatically generated one will be used.

For example, to let package `src:pkgA` of team `${TEAM}` and project
`${PROJECT}` setup an aptly repository and let package `src:pkgB` use the
repository, enable the `aptly` job by adding the following line to the
`debian/salsa-ci.yml` of `src:pkgA`:

```yaml
variables:
  SALSA_CI_DISABLE_APTLY: 0
```

The next time the pipeline of `src:pkgA` is run, a new job called `aptly` will
be part of the "Publish" stage of the pipeline. Click on the job to obtain the
job number which will be needed in the `debian/salsa-ci.yml` file of `src:pkgB`:

In the `debian/salsa-ci.yml` file of `src:pkgB` add the following lines after
the `variables` section

```yaml
before_script:
  - echo "deb [trusted=yes] https://salsa.debian.org/${TEAM}/${PROJECT}/-/jobs/${JOB_ID}/artifacts/raw/aptly unstable main" | tee /etc/apt/sources.list.d/pkga.list
  - apt-get update
```

Replace `{TEAM}`, `${PROJECT}` with appropriate `team` and `project` name
respectively and `${JOB_ID}` with the aptly job number of `src:pkgA` pipeline.
Now you can use the binary packages produced by `src:pkgA` in `src:pkgB`.

**Note:** When you make changes to `src:pkgA`, `src:pkgB` will continue using
the old repository that the job number points to. If you want `src:pkgB` to use
the updated binary packages, you have to retrieve the job number of the `aptly`
job from `src:pkgA` and update the `${JOB_ID}` of `src:pkgB`.

See also howto
[add private repositories to the builds](#add-private-repositories-to-the-builds).

### Enable wrap-and-sort job

The job `wrap-and-sort` can be used to check if files in the `debian/`
folder are wrapped properly using
[wrap-and-sort(1)](https://manpages.debian.org/testing/devscripts/wrap-and-sort.1.en.html).
To enable this check, either run your pipeline manually with
`SALSA_CI_DISABLE_WRAP_AND_SORT` set to anything different than 1, 'yes' or
'true' or by adding the following to your `debian/salsa-ci.yml`:

```yaml
variables:
  SALSA_CI_DISABLE_WRAP_AND_SORT: 0
```

You can configure the parameters passed to `wrap-and-sort` using the
`SALSA_CI_WRAP_AND_SORT_ARGS` variable like this:

```yaml
variables:
  SALSA_CI_DISABLE_WRAP_AND_SORT: 0
  SALSA_CI_WRAP_AND_SORT_ARGS: '-asbkt'
```

The style to use is a subjective decision.  The default behaviour may
change over time
[#895570](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=895570).
We suggest to consider `-a --wrap-always`, `-s --short-indent`, `-b
--sort-binary-packages`, `-k --keep-first`, and `-t --trailing-comma`
as they encourage a minimal, consistent and deterministic style.

### Debian release bump

By default, the build job will increase the release number using the +salsaci
suffix. To disable this behavior set the `SALSA_CI_DISABLE_VERSION_BUMP` to 1,
'yes' or 'true'.


## Distribution and release selection

### Customise what Debian release to use

By default, everything will run based on the target release in
`debian/changelog`. If the latest entry is `UNRELEASED`, then the target release
from the second entry will be used.

The target release can be customized by setting the `RELEASE` variable explicitly.

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  RELEASE: 'bookworm'
```

The following releases are available:
* stretch
* stretch-backports
* buster
* bullseye
* bullseye-backports
* bookworm
* bookworm-backports
* stable
* testing
* unstable
* experimental

### Experimental: Ubuntu support

> :warning: The Ubuntu support is experimental and exists to collect feedback
> and potential contributions from the wider Ubuntu community. It may be removed
> if the benefits are not clearly larger than the cost of maintaining it.

Test Ubuntu packages by using recipe `debian/salsa-ci.yml`:

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/ubuntu.yml
```

Additionally you must ensure a Ubuntu release is defined in the latest
`debian/changelog` entry or as a `RELEASE` variable.

Currently autopkgtest is the only test job enabled by default (see
[1](https://salsa.debian.org/salsa-ci-team/pipeline/-/issues/327#note_518079)
and
[2](https://salsa.debian.org/salsa-ci-team/pipeline/-/issues/327#note_523235)).
Other test jobs can be enabled using `SALSA_CI_DISABLE_*` variables.


## General Debian packaging support and resources

* The [Debian Policy](https://www.debian.org/doc/debian-policy/): packages must conform to it.
* The [Developers Reference](https://www.debian.org/doc/developers-reference/): details best packaging practices.
* The [Guide for Debian Maintainers](https://www.debian.org/doc/debmake-doc): puts a bit of the two above in practice.


## General Salsa information

The GitLab instance salsa.debian.org is maintained by the
[Debian Salsa admin team](https://wiki.debian.org/Salsa), which is separate from
the Salsa CI team.


## Support for Salsa CI use

The Salsa CI developers and users can be found at:

* Mailing list: [debian-salsa-ci_at_alioth-lists.debian.net](mailto:debian-salsa-ci_at_alioth-lists.debian.net)
* Matrix: [#salsaci:matrix.debian.social](https://matrix.to/#/#salsaci:matrix.debian.social)
* IRC: [#salsaci @ OFTC](ircs://irc.oftc.net/salsa) ([webchat](https://webchat.oftc.net/?channels=salsaci))
* Issue tracker: [salsa-ci-team/pipeline/issues](https://salsa.debian.org/salsa-ci-team/pipeline/issues)


## Contributing

The success of this project comes from meaningful contributions that are made by
interested contributors like you. If you want to contribute to this project,
follow the detailed guidelines in the [CONTRIBUTING file](CONTRIBUTING.md)
