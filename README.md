# Debian pipeline for Developers

Build and test on reproducible environments on every push.

TL;DR: Use this CI/CD configuration file setting:

```
recipes/debian.yml@salsa-ci-team/pipeline
```

## Table of contents
* [Introduction](#introduction)
* [What does this pipeline give to my project?](#what-does-this-pipeline-provide-for-my-projectpackage)
* [Basic Use](#basic-use)
* [Advanced Use](#advanced-use)
* [Contributing](#contributing)
* [Support](#support)

## Introduction

The Salsa CI Team's work aims to improve the Debian packaging lifecycle by providing [Continuous Integration](https://about.gitlab.com/product/continuous-integration/) fully compatible with Debian packaging.

Currently, all the building and testing performed by Debian QA is run asynchronously and takes a long time to give feedback because it is only accessible after pushing a release to the archive.

Our [pipeline](https://salsa.debian.org/help/ci/pipelines/index.md) definition is focused on speeding up this process by giving developers faster feedback.

## What does this _pipeline_ provide for my project/package?

The [pipeline](https://salsa.debian.org/help/ci/pipelines/index.md) builds your package(s) and runs multiple checks on them after every push to Salsa.

This provides you with instant feedback about any problems the changes you made may have created or solved, without the need to do a push to the archive, speeding up your development cycle and improving the quality of packages uploaded to Debian.

While the pipeline is a Work-In-Progress project, it will always try to replicate the tests run by Debian QA.
The services we got working are the following:

 * Building the package from the source (only gbp is supported)
 * [Lintian](https://lintian.debian.org)
 * Reproducible build using [Reprotest](https://reproducible-builds.org/tools)
 * [Piuparts](https://piuparts.debian.org)
 * [Autopkgtest](https://salsa.debian.org/ci-team/autopkgtest/raw/master/doc/README.package-tests.rst)
 * [Buildd Log Scanner](https://qa.debian.org/bls/)

Those services are enabled by something we called `salsa-pipeline` and it will be shared for all Salsa projects who adopt it.
Having this on GitLab CI ensures that every package accomplishes the minimum quality to be in the archive and if we improve or add a new service the project will get the benefit instantaneously.

## Basic Use

To use the Salsa Pipeline, the first thing to do is to enable the project's Pipeline. Go to `Settings` (General), expand `Visibility, project features, permissions`, and in `Repository`, enable `CI/CD`. This makes the `CI/CD` settings and menu available.
Then, change the project's setting to make it point to the pipeline's config file.
This can be done on `Settings` -> `CI/CD` (on the expanded menu, don't click on the CI / CD rocket) -> `General Pipelines` -> `CI/CD configuration file`.

If the base pipeline configuration fits your needs without further modifications, the recommended way is to use `recipes/debian.yml@salsa-ci-team/pipeline` as the config path, which refers to a file kept in the `salsa-ci-team/pipeline` repository.

> :warning: **Note:** The pipeline is not run automatically after configuring it. You can either trigger it by [running the pipeline manually](https://salsa.debian.org/help/ci/pipelines/index.md#run-a-pipeline-manually) or pushing something.

On the other hand, if you want to use the base configuration and apply customizations on top, the recommended path to create this file is `debian/salsa-ci.yml`.
It should contain at least the following lines:

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml
```

> :warning: **Note:** On Debian projects, you would normally want to put this file under the `debian/` folder.

## Advanced Use

Following the basic instructions will allow you to add all the building and testing stages as provided by the Salsa CI Team.
However, customization of the scripts is possible.

The [`salsa-ci.yml`](https://salsa.debian.org/salsa-ci-team/pipeline/blob/master/salsa-ci.yml) template delivers the jobs definitions.
Including only this file, no job will be added to the pipeline.
On the other hand, [`pipeline-jobs.yml`](https://salsa.debian.org/salsa-ci-team/pipeline/blob/master/pipeline-jobs.yml) includes all the jobs' instances.

For an example of a very customized CI pipeline, one can have a look at the [salsa-ci.yml for the kernel](https://salsa.debian.org/kernel-team/linux/-/blob/master/debian/salsa-ci.yml), which starts like this:

```yaml
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/salsa-ci.yml

# jobs are defined below ...
```

### Changing the Debian Release

By default, everything will run on the suite declared at the top of debian/changelog,
or - if debian/changelog cannot be parsed for a suitable release - on the `'unstable'` suite.
Changing the release is as easy as setting a `RELEASE` variable.

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  RELEASE: 'buster'
```

The following releases are currently supported:
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

### Avoid running CI on certain branches

It is possible to configure the pipeline to skip branches you don't want CI to run on.
The `SALSA_CI_IGNORED_BRANCHES` variable can be set to a regex that will be compared against the ref name and will decide if a pipeline is created.

By default, pipelines are only created for branches that contain a `debian/` folder.

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_IGNORED_BRANCHES: 'some-branch|another-ref'
```

### Building with non-free dependencies
By default, only `main` repositories are used.
If your package has dependencies or build-dependencies in the `contrib` or `non-free` components (archive areas), set `SALSA_CI_COMPONENTS` to indicate this:

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
32-bit x86 build (`build i386`) should be disabled. (refer to the [Disabling building on i386](#Disabling-building-on-i386) Section).

### Skipping a job
There are many ways to skip a certain job. The recommended way is to set to `1` (or "`yes`" or "`true`") the `SALSA_CI_DISABLE_*` variables that have been created for this purpose.

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

### Disabling building on i386
The `build i386` job builds packages against the 32-bit x86 architecture. If for any reason you need to skip this job, set the `SALSA_CI_DISABLE_BUILD_PACKAGE_I386` in the variables' block to `1`, '`yes`' or '`true`'.  i.e;

```yaml

variables:
  SALSA_CI_DISABLE_BUILD_PACKAGE_I386: 1
```

### Allowing a job to fail
Without completely disabling a job, you can allow it to fail without failing the whole pipeline. That way, if the job fails, the pipeline will pass and show an orange warning telling you something went wrong.

For example, even though reproducible builds are important, `reprotest`'s behavior can sometimes be a little erratic and fail randomly on packages that aren't totally reproducible (yet!). In such case, you can allow `reprotest` to fail by adding this variable in your salsa-ci.yml manifest:

```
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

reprotest:
  allow_failure: true
```

### Set build timeout
At times your job may fail because it reached its max duration (either job timeout, or runner timeout).
In that case, the job would stop immediately without entering the `after_script` phase, and without saving the cache and without saving the artifacts.

To prevent this, the build phase of the build job and the build phase of the reprotest job have a timeout of `2.75h` (the runner's timeout is 3h). This permits also saving the cache of ccache. That way, on the next run, there is more chance to finish the job since it can use ccache's cache.

You can set the `SALSA_CI_BUILD_TIMEOUT_ARGS` variable to override this. The arguments can be any valid argument used by the `timeout` command. For example, you may set:

```
variables:
  SALSA_CI_BUILD_TIMEOUT_ARGS: "0.75h"
```

### Enabling the pipeline for tags
By default, the pipeline is run only for commits, tags are ignored. To run the pipeline against tags as well, export the `SALSA_CI_ENABLE_PIPELINE_ON_TAGS` variable and set it to one of "1", "yes" or "true", like in the following example:

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_ENABLE_PIPELINE_ON_TAGS: 1
```

### Skipping the whole pipeline on push

There may be reasons to skip the whole pipeline for a `git push`, for example when you are adding `salsa-ci.yml` to hundreds of repositories or doing other mass changes.

You can achieve this in two ways:

You can insert `[ci skip]` or `[skip ci]`, using any capitalization, in the commit message. With this marker, GitLab will not run the pipeline when the commit is pushed.

Alternatively, one can pass the `ci.skip` [Git push](https://git-scm.com/docs/git-push#Documentation/git-push.txt--oltoptiongt) option if using Git 2.10 or newer:

```
git push --push-option=ci.skip    # using git 2.10+
git push -o ci.skip               # using git 2.18+
```

See also https://salsa.debian.org/help/ci/pipelines/index.md#skip-a-pipeline

### Adding your private repositories to the builds

The variables `SALSA_CI_EXTRA_REPOSITORY` and `SALSA_CI_EXTRA_REPOSITORY_KEY` can be
used to add private apt repositories to the sources.list, to be
used by the build and tests, and (optionally) the signing key for the
repositories in armor format.
Alternatively, the single variable `SALSA_CI_EXTRA_REPOSITORY_SOURCES`
can be used to add an extra repository (with its corresponding signing key)
in deb822-style format (which is conveniently rendered by the aptly job).
These variables are of
[type file](https://salsa.debian.org/help/ci/variables/index.md#cicd-variable-types),
which eases the multiline handling, but have the disadvantage that their content can't
be set on the salsa-ci.yml file - but they can be added to the repository as files and
have their filenames then set in the salsa-ci.yml file:

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

### Setting variables on pipeline creation

You can set these and other similar variables when launching a new pipeline in different ways:
 * Using the web interface under CI/CD, Run Pipeline, and setting the
desired variables.
 * Using the [GitLab API](https://salsa.debian.org/help/api/index.md). For example,  check the script
[salsa_drive_build.py](https://salsa.debian.org/maxy/qt-kde-ci/blob/tooling/salsa_drive_build.py),
in particular the function
[launch_pipelines](https://salsa.debian.org/maxy/qt-kde-ci/blob/tooling/salsa_drive_build.py#L568).
 * Setting them as part of a pipeline-triggered build.

### Only running selected jobs

If you want to use the definitions provided by the Salsa CI Team, but want to explicitly define which jobs to run, you might want to declare your YAML as follows:

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

On the previous example, the package is built on Debian experimental and checked through on all tests currently provided.
You can choose to run only some of the jobs by deleting any of the definitions above.

As new changes are expected to happen from time to time, we **firmly recommend NOT to do define all jobs manually**.
Please consider if [skipping jobs](#skipping-a-job) meets your needs instead.

### Testing build of arch=any and arch=all packages

If your package contains binary packages for `all` or `any`, you may want to test if those can be built in isolation from the full build normally done.

This verifies the Debian buildds can build your package correctly when building for other architectures that the one you uploaded in or in case a binNMU is needed or you want to do source-only uploads.

The default `pipeline-jobs.yml` does this automatically based on the contents of `debian/control`, but if you manually define the jobs to run, you also need to include the `test-build-any` and `test-build-all` jobs manually as well:

```yaml
test-build-any:
  extends: .test-build-package-any

test-build-all:
  extends: .test-build-package-all
```

`.test-build-package-any` runs `dpkg-buildpackage` with the option `--build=any` and will only build arch-specific packages.

`.test-build-package-all` does the opposite and runs `dpkg-buildpackage` with the option `--build=all` building only arch-indep packages.

### Enable generation of dbgsym packages

To reduce the size of the artifacts produced by the build jobs, auto-generation
of dbgsym packages is disabled by default. This behaviour can be controlled by
the `SALSA_CI_DISABLE_BUILD_DBGSYM`. Set it to anything different than 1, 'yes'
or 'true', to generate those packages.

```yaml
variables:
  SALSA_CI_DISABLE_BUILD_DBGSYM: 0
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

### Enable wrap-and-sort job

The job `wrap-and-sort` can be used to check if files in the `debian/`
folder are wrapped properly using
[wrap-and-sort(1)](https://manpages.debian.org/testing/devscripts/wrap-and-sort.1.en.html). To
enable this check, either run your pipeline manually with
`SALSA_CI_DISABLE_WRAP_AND_SORT` set to anything different than 1,
'yes' or 'true' or by adding the following to your
`debian/salsa-ci.yml`:

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

### Customizing Lintian

The Lintian job can be customized to ignore certain tags.

To ignore a tag, add it to the setting `SALSA_CI_LINTIAN_SUPPRESS_TAGS`.

By default, the Lintian jobs fail either if a Lintian run-time error occurs or if Lintian finds a tag of the error category.

To also fail the job on findings of the category warning, set `SALSA_CI_LINTIAN_FAIL_WARNING` to 1 (or "yes" or "true").

To make Lintian shows overridden tags, set `SALSA_CI_LINTIAN_SHOW_OVERRIDES` to 1 (or "yes" or "true").

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_LINTIAN_FAIL_WARNING: 1
  SALSA_CI_LINTIAN_SUPPRESS_TAGS: 'orig-tarball-missing-upstream-signature'
```

It is possible to add any other lintian argument using `SALSA_CI_LINTIAN_ARGS`. Those
arguments will be appended after the arguments generated by the pipeline.

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

```
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

### Adding extra arguments to autopkgtest

Sometimes it is desirable to add arguments to autopkgtest.

You can do this by setting the arguments in the `SALSA_CI_AUTOPKGTEST_ARGS` variable.

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_AUTOPKGTEST_ARGS: '--debug'
```

Note that autopkgtest can access the repository in the current directory, making it possible for `--setup-commands` to read commands from a file. For example:

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_AUTOPKGTEST_ARGS: '--setup-commands=ci/pin-django-from-backports.sh'
```

### Making autopkgtest more strict

By default, the autopkgtest job will succeed if autopkgtest exits with status
0, 2 or 8. If you would like the autopkgtest job to only succeed if all tests
pass and fail otherwise, you can restrict success to exit status 0 by writing:

```yaml
variables:
  SALSA_CI_AUTOPKGTEST_ALLOWED_EXIT_STATUS: '0'
```

To allow multiple exit codes, separate them by comma.

### Adding extra arguments to dpkg-buildpackage

Sometimes it is desirable to add direct options to the dpkg-buildpackage that is run for the package building.

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

### Executing a pre-install / post-install script in piuparts

Sometimes it is desirable to execute a pre-install or post-install scripts in piuparts.

You can do this using the `SALSA_CI_PIUPARTS_PRE_INSTALL_SCRIPT` and `SALSA_CI_PIUPARTS_POST_INSTALL_SCRIPT` variables, that may point to the path of scripts in the project repository. This could be used, for instance, to pin dependencies. For example, if you had a `ci/pin-django-from-backports.sh` script:

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
The [Aptly](https://www.aptly.info/) task runs in the publish stage and will save published apt repository files as its artifacts, so downstream CI tasks may access built binary/source packages directly through artifacts url via apt. This is currently disabled by default. To enable it, set the `SALSA_CI_DISABLE_APTLY` variable of the repository whose artifacts you want to use to anything other than `1`, '`yes`' or '`true`'. (check example below)

To specify repository signing key, export the gpg key/passphrase as CI / CD [Variables](https://salsa.debian.org/help/ci/variables/index.md) `SALSA_CI_APTLY_GPG_KEY` and `SALSA_CI_APTLY_GPG_PASSPHRASE`. Otherwise, an automatically generated one will be used.

For example, to let package `src:pkgA` of team `${TEAM}` and project `${PROJECT}` setup an aptly repository and let package `src:pkgB` use the repository, enable the `aptly` job by adding the following line to the `debian/salsa-ci.yml` of `src:pkgA`:

```yaml
variables:
  SALSA_CI_DISABLE_APTLY: 0
```

The next time the pipeline of `src:pkgA` is run, a new job called `aptly` will be part of the "Publish" stage of the pipeline. Click on the job to obtain the job number which will be needed in the `debian/salsa-ci.yml` file of `src:pkgB`:

In the `debian/salsa-ci.yml` file of `src:pkgB` add the following lines after the `variables` section

```yaml
before_script:
  - echo "deb [trusted=yes] https://salsa.debian.org/${TEAM}/${PROJECT}/-/jobs/${JOB_ID}/artifacts/raw/aptly unstable main" | tee /etc/apt/sources.list.d/pkga.list
  - apt-get update
```

Replace `{TEAM}`, `${PROJECT}` with appropriate `team` and `project` name respectively and `${JOB_ID}` with the aptly job number of `src:pkgA` pipeline. Now you can use the binary packages produced by `src:pkgA` in `src:pkgB`. \
**Note:** When you make changes to `src:pkgA`, `src:pkgB` will continue using the old repository that the job number points to. If you want `src:pkgB` to use the updated binary packages, you have to retrieve the job number of the `aptly` job from `src:pkgA` and update the `${JOB_ID}` of `src:pkgB`.

See also
[Adding your private repositories to the builds](#adding-your-private-repositories-to-the-builds)

### Debian release bump
By default, the build job will increase the release number using the +salsaci suffix.
To disable this behavior set the `SALSA_CI_DISABLE_VERSION_BUMP` to 1, 'yes' or 'true'.

### Build jobs on ARM

Salsa CI includes builds jobs for armel, armhf and arm64, but those are
disabled by default. You can enable them for your project if you have an ARM
gitlab runner available. For that, you need to register your runner, tagging it
as `arm64`, and set the related variables to anything different than 1, 'yes'
or 'true':

```yaml
variables:
  SALSA_CI_DISABLE_BUILD_PACKAGE_ARMEL: 0
  SALSA_CI_DISABLE_BUILD_PACKAGE_ARMHF: 0
  SALSA_CI_DISABLE_BUILD_PACKAGE_ARM64: 0
```

### Build job on RISC-V

Salsa CI includes a riscv64 build job, but it is currently disabled by default.
You can enable it for your project if you have a RISC-V gitlab runner
available. For that, you need to register your runner, tagging it as `riscv64`,
and set the related variable to anything different than 1, 'yes' or 'true':

```yaml
variables:
  SALSA_CI_DISABLE_BUILD_PACKAGE_RISCV64: 0
```

### Customizing reprotest

#### Running reprotest with diffoscope

Reprotest stage can be run with [diffoscope](https://try.diffoscope.org/), which is an useful tool that helps identifying reproducibility issues.
Large projects will not pass on low resources runners as the ones available right now.

To enable diffoscope, setting `SALSA_CI_REPROTEST_ENABLE_DIFFOSCOPE` to 1 (or 'yes' or 'true') is needed.

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_REPROTEST_ENABLE_DIFFOSCOPE: 1
```

#### Adding extra arguments to reprotest

Sometimes it is desirable to disable some reprotest validations because the reproducibility issue comes inherently from the programming language being used, and not from the code being packaged. For example, some compilers embed the build path in the generated binaries.

You can get this level of customization by adding extra `reprotest` parameters in the `SALSA_CI_REPROTEST_ARGS` variable.

```yaml
---
include:
  - https://salsa.debian.org/salsa-ci-team/pipeline/raw/master/recipes/debian.yml

variables:
  SALSA_CI_REPROTEST_ARGS: --vary=-build_path
```

#### Breaking up the reprotest job into the different variations

By default, reprotest applies all the known variations (`--variations=+all`,
see the full list at
[reprotest(1)](https://manpages.debian.org/buster/reprotest/reprotest.1.en.html)).
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

#### Faketime is currently disabled

Note that reprotest's faketime support is currently disabled, as it causes false
positives on files touched by quilt. It will be re-enabled once this is fixed.
https://salsa.debian.org/salsa-ci-team/pipeline/-/issues/251

#### Git attributes

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

## Contributing

The success of this project comes from meaningful contributions that are made by interested contributors like you. If you want to contribute to this project, follow the detailed guidelines in the [CONTRIBUTING file](CONTRIBUTING.md)

## Support

We have different support media:

* IRC: \#salsaci @ OFTC
* Mailing list: [debian-salsa-ci_at_alioth-lists.debian.net](mailto:debian-salsa-ci_at_alioth-lists.debian.net)
* [Issue tracker](https://salsa.debian.org/salsa-ci-team/pipeline/issues)
