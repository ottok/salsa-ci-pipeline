# Salsa CI pipeline job tiers

The most important jobs are `build` and `autopkgtest`. They must always pass,
otherwise the package cannot migrate from Debian *unstable* to *testing*, and
most certainly is visibly broken for all users as well.

The next most important jobs are the variations of the build. Even if the most
basic amd64 binary build would pass, if the other builds are failing the package
will not migrate from Debian *unstable* to *testing*, and for any user needing
those alternative binary versions the package would be unusable. Lintian and
Piuparts are also essential and can reveal serious issues in the package, though
they may also error on minor issues that do not necessarily indicate that the
package is unusable, and thus these two are slightly lower in importance than
autopkgtest.

The other jobs such as rc-bugs, blhc, reprotest, wrap-and-sort and test-build-*
jobs are relevant mainly for the new package versions. Debian maintainers should
strive to have these jobs pass in the next version going into Debian unstable,
and do the necessary build rule changes or patch the upstream source code to
improve the code quality.

| Job | Requirement tier | Debian release | Debian release overlay* |
| --- | --- | --- | --- |
| build (amd64) | Mandatory | * | sid+experimental, \*+*-backports |
| build arm64 | Mandatory | * | sid+experimental, \*+*-backports |
| build armel | Mandatory | sid, trixie, bookworm | sid+experimental, \*+*-backports |
| build armhf | Mandatory | sid, trixie, bookworm, bullseye | sid+experimental, \*+*-backports |
| build riscv64 | Mandatory | sid, trixie | sid+experimental |
| build *-backports | Optional | sid | sid+experimental |
| build i386 | Mandatory | bookworm, bullseye | *+*-backports |
| build source | Mandatory | sid, trixie, bookworm, bullseye | sid+experimental, \*+*-backports |
| test-crossbuild-armel | Optional | sid | sid+experimental |
| test-crossbuild-armhf | Optional | sid | sid+experimental |
| reprotest | Optional | sid | sid+experimental |
| autopkgtest | Mandatory | * | sid+experimental, \*+*-backports |
| lintian | While some Lintian tests reveal serious flaws and are mandatory to fix, most Lintian errors are optional to fix. | sid, trixie, bookworm, bullseye | sid+experimental, \*+*-backports |
| missing-breaks | Mandatory | sid | sid+experimental |
| piuparts | Mandatory | sid | sid+experimental, \*+*-backports |
| rc-bugs | Optional | sid | sid+experimental |
| test-build-all/any | Optional | sid | sid+experimental |
| test-build-profiles | Optional | sid | sid+experimental |
| test-build-twice | Optional | sid | sid+experimental |
| test-crossbuild-arm64 | Optional | sid | sid+experimental |
| wrap-and-sort | Optional | sid | sid+experimental |

* Debian release overlay refers to releases that are not self-sufficient, but
  need to be overlayed on a full release. For example Debian experimental cannot
  be used on its own, but must be activated on top of a Debian unstable (sid)
  environment.
