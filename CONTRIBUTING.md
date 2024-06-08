
# Table of contents

* Naming conventions
* Structure of files and folders
* How to contribute

# Differences to Version 2

The naming conventions have changed from Version 2 to Version 3. Do use the new naming convention!

# Naming conventions

The Jukebox core app is written entirely in Python. Therefore, we follow the [Python Style Guide](https://www.python.org/dev/peps/pep-0008/).

* **Files & folder names**
  * all **lower case**
  * separate words with **underscore** `_` (**no** dashes - this conflicts with Python module names!)
    * Note: This is the major difference to Version 2. Follow this rule!
  * be **descriptive** in your wording (e.g. `raspberry`, not `juicy-red-thing`)
  * move **from general to specific** (e.g. `food-fruit-raspberry`, not `raspberry-food-fruit`)
  * unique and clear product IDs (e.g. MAX7219)
    * the product ID should be written as is (no lowercase)
    * the product ID should come last in a descriptive name (e.g. `dot_matrix_module_MAX7219`)
  * be consistent and look at existing examples before you invent something new

* **Documentation**
  * You are expected to write some Documentation. It's easy. **Very** easy actually with [Python Docstrings](https://www.geeksforgeeks.org/python-docstrings/)
  
# Structure of files and folders

Inside the root folder or the repo, these folders are important:

* `src/jukebox`
  * contains the Jukebox Core App
* `src/jukebox/components`
  * contains the Python packages that are loaded using the plugin interface
* `src/webapp`
  * contains the Web Interface

All folders on all hierarchy levels starting with `scratch*` are ignored by git and flake8. These are intended
as local, temporary scratch areas.

# How to contribute

Contributors have played a bigger role over time to keep Phoniebox on the edge of innovation :)

Our goal is to make it simple for you to contribute changes that improve functionality in your specific environment.
To achieve this, we have a set of guidelines that we kindly request contributors to adhere to.
These guidelines help us maintain a streamlined process and stay on top of incoming contributions.

To report bug fixes and improvements, please follow the steps outlined below:

1. For bug fixes and minor improvements, simply open a new issue or pull request (PR).
2. If you intend to port a feature from Version 2.x to future3 or wish to implement a new feature, we recommend reaching out to us beforehand.
   * In such cases, please create an issue outlining your plans and intentions.
   * We will ensure that there are no ongoing efforts on the same topic.

We eagerly await your contributions! You can review the current [feature list](documentation/developers/status.md) to check for available features and ongoing work.

## Getting Started

* Make sure you have a [GitHub account](https://github.com/signup/free)
* Open an issue if one does not already exist
  * Mark the issue with the `future3` label. This is important to us, to distinguish between the versions.
    Version 2 will continue to live for quite a while.
  * Clearly describe the issue including steps to reproduce when it is a bug
  * Make sure you fill in the earliest version that you know has the issue

The preferred way of code contributions are [pull requests (follow this link for a small howto)](https://www.digitalocean.com/community/tutorials/how-to-create-a-pull-request-on-github).
And ideally pull requests use the "running code" of your Phoniebox.
Alternatively, feel free to post tweaks, suggestions and snippets in the ["issues" section](https://github.com/MiczFlor/RPi-Jukebox-RFID/issues).

## Making Changes

* Create a fork of this repository
* Create a topic branch from where you want to base your work.
  * This is usually the `future3/develop` branch.
  * Only target the `future3/main` branch if you are certain your fix must be on that
    branch.
* Make commits of logical and atomic units.
* Check for unnecessary whitespace with `git diff --check` before committing.
* See also the [documentation for developers](documentation/developers/README.md)

## Making Trivial Changes

For changes of a trivial nature, it is not always necessary to create a new issue. In this case
you can directly open a pull request. It is appropriate to start the first line of a
commit / pull request with one of  `(docs)`, `(maint)`, or `(packaging)` instead of a ticket
number.

For commits that address trivial repository maintenance tasks or packaging
issues, start with `(maint)` or `(packaging)`,
respectively.

## Staying on the edge

As new commits appear on Github you want to stay on the edge - especially if you are continuing to contribute.
From time to time, you will need to update the Web App or the dependencies. To find out when, we provide a
git hook script. To activate simply copy it in the git hook folder.

~~~bash
cp .githooks/post-merge .git/hooks/.
~~~

## Before submitting

Run the checks below on the code. Fix those issues! Or you are running in delays in the acceptance of your PR.
We provide git hooks for those checks for convenience. To activate

~~~bash
cp .githooks/pre-commit .git/hooks/.
~~~

### Python Code

If you touched *any* Python file (even if only for fixing spelling errors), run flake8 in the top-level folder.
It contains out setup file.

~~~bash
cd ~/RPi-Jukebox-RFID
./run_flake8.sh
~~~

If you are convinced some issue should not apply to your case or would require extensive re-coding, that could be OK.
Let us know in the pull request - we will look at it.

### Tests

Tests are very few at the moment, but it cannot hurt to run them. If you have tests for your new modules, please add
them.

~~~bash
cd ~/RPi-Jukebox-RFID/
./run_pytest.sh
~~~

## Submitting Changes

* Push your changes to a topic branch in your fork of the repository
* Submit a pull request to the repository
* The core team looks at Pull Requests on a regular basis
* After feedback has been given we expect responses within two weeks. After two
  weeks we may close the pull request if it isn't showing any activity.

## Revert Policy

By running tests in advance and by engaging with peer review for prospective
changes, your contributions have a high probability of becoming long lived
parts of the the project. After being merged, the code will run through a
series of testings. These Tests can reveal incompatibilities that are difficult
to detect in advance.

If the code change results in a test failure, we will make our best effort to
correct the error. If a fix cannot be determined and committed within 24 hours
of its discovery, the commit(s) responsible *may* be reverted, at the
discretion of the committer and Phonie maintainers.
The original contributor will be notified of the revert.

### Summary

* Changes resulting in test failures will be reverted if they cannot
  be resolved within one business day.

## Guidelines

* Phoniebox runs on Raspberry Pi OS.
* Minimum python version is currently **Python 3.9**.

## Additional Resources

* [General GitHub documentation](https://help.github.com/)
* [GitHub pull request documentation](https://help.github.com/articles/creating-a-pull-request/)
