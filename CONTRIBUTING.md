The Salsa CI project is a Debian open source project and welcomes contributions
such as:

* Opening up new issues that address specific areas to improve the pipeline.
* Improving the documentation e.g. by explaining concepts better or adding
  missing information
* Solving open issues. Some issues have labels attached to them which have
  different meanings. This also means they have been triaged and it would be
  great to have them solved. Some labels are:
    * **`Accepting MR`** - The issue has been triaged and is worthy of solving
      so a meaningful Merge Request is welcome
    * **`Newcomer`** - Issue is a good first start in case you are new to the
      project.
    * **`Nice-To-Have`** - The issue is good to solve but not urgent

To contribute to Salsa CI, you must have a Salsa (Debian's Gitlab Instance)
account. To create an account, please follow the instructions in the [Salsa
Documentation](https://wiki.debian.org/Salsa/Doc#Users).

## Merge Request worklow explanined

Proposed modifications to the Salsa CI's pipeline are done via merge requests.
For that:

1. Fork the project and clone the fork on your local machine. **_Your fork's
   visibility should be set to 'Public' for the pipeline to be shown on the
   merge request._** Committing directly to the upstream default branch is not
   allowed. To clone your project, we recommend you use the SSH option. You can
   find instructions about how to interact with Salsa via SSH at
   [salsa.debian.org/help/topics/authentication](https://salsa.debian.org/help/topics/authentication/index.md).

1. After cloning, run [`git config --local commit.gpgsign true`](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work#_everyone_must_sign)
   to ensure all your commits in this project are automatically signed. Debian
   relies on OpenPGP to guarantee the authenticity and integrity of contributions
   and code submissions to Salsa-CI will not be accepted if unsigned.

1. Branch off to the default branch to work on a meaningfully named branch (e.g.
   `git checkout -b 193-build-twice`). If you are fixing an issue, it is
   convenient to prefix the branch name with the issue number. **Slashes (`/`)
   are not allowed in the branch name, as the branch name is used as a staging
   tag on the generated images, which does not support slashes._**

1. Make necessary changes and commit. Make sure your syntax is flawless, scripts
   follow their language-wide coding style, and that git commit message is
   polished. *Note: YAML files follow a two-space indentation. To check for
   errors in your YAML files use of
   [yamllint](https://manpages.debian.org/unstable/yamllint/yamllint.1.en.html).*

1. If you are a new contributor, add your name and emails to the
   [CONTRIBUTORS](CONTRIBUTORS) list.

1. Once you are satisfied with your changes, push them to your fork's remote
   repository and create a Merge Request against the upstream default branch.

1. Remember to follow up on the Merge Request, verify that the CI passed, and
   respond to review feedback. If the code base evolves before your MR is
   merged, please occasionally rebase on latest upstream default branch to
   ensure your MR can apply cleanly.

If your Merge Request needs testing not covered by the pipeline's CI, it is
important to link the tests you have done in the MR description or comment
section to speed up the review. There are different ways to test different
scenarios. You can always ping fellow contributors to see how to carry out
certain tests.

### Allow images to be persistent

When triggered from staging (not the default) branches, there is a `clean
images` job that removes the images created during the first stage (the `images`
stage), in order to avoid consuming space in the Container Registry. Depending
on how you have to test your Merge Request, you may want to keep those images.

To disable this behavior set the `SALSA_CI_PERSIST_IMAGES` to 1, 'yes' or
'true' on a CI variable (*CI/CD Settings*).

### Avoid creating images (in staging branches)

During the development process, it is possible that you would like to make
several `git push`es. For each `git push`, all the staging images are built by
default, and that could be time-consuming. So if you are making several changes
and you want to save some time, you could:

1. Run a pipeline keeping the images, as described just above.

1. Run a second pipeline `SALSA_CI_DISABLE_BUILD_IMAGES` set to 1, 'yes' or
   'true'.

1. Once you are done, please remember to remove the staging images, setting
   `SALSA_CI_PERSIST_IMAGES` back to 0.Q

### Test creating production images (in staging branches)

By default, the pipeline for non-default branches (i.e. those from merge
requests) only triggers a subset of image building jobs. The production job
images that are built for every supported debian release, are limited to sid
for staging branches. This reduces the use of computing resources, while making
still possible to test the images. However, in some cases, contributors need to
test how the full set of images are built from the changes introduced by their
merge requests. To do that, set the `BUILD_ALL_IMAGES` variable to 1, 'yes' or
'true'.

### Test images built for non-default architectures (in staging branches)

By default, the test pipeline for non-default branches (i.e. those from merge
requests) only triggers test build jobs for x86 architectures (amd64 and i386).
If you want to test the images built for ARM and RISC-V, running build jobs for
those architectures, set the `SALSA_CI_TEST_NON_DEFAULT_ARCHS` variable to 1,
'yes' or 'true'.

```yaml

variables:
  SALSA_CI_TEST_NON_DEFAULT_ARCHS: 1
```

### Build Ubuntu images outside Salsa

By default, Ubuntu images are built on salsa.debian.org GitLab instance only;
There are SalsaCI forks which are interested in debian images only and operate
on other GitLab instances. If you want to build Ubuntu images on GitLab instaces
other than Salsa, set the `BUILD_UBUNTU_IMAGES` variable to 1, 'yes' or 'true'.
