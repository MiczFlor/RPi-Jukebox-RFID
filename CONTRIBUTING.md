
# Table of contents

* Naming conventions
* Structure of files and folders
* How to contribute

# Naming conventions

* **Files & folder names**
    * all **lower case**
    * separate words with **dashes** `-` (less keystrokes, better autocomplete recognition, in HTML links dashes can not be confused) not camel/PascalCaps or underscores
    * be **descriptive** in your wording (e.g. `raspberry`, not `juicy-red-thing`)
    * move **from general to specific** (e.g. `food-fruit-raspberry`, not `raspberry-food-fruit`)
    * unique and clear product IDs (e.g. MAX7219)
        * the product ID should be written as is (no lowercase)
        * the product ID should come last in a descriptive name (e.g. dot-matrix-module-MAX7219)
    * be consistent and look at existing examples before you invent something new

* **`README.md`**
    * written in capital letters, so it's easier to spot
    * every new folder of a component deserves a `README.md` file

# Structure of files and folders

Inside the root folder or the repo, these folders are important:

* `scripts`
    * this folder should contain **only actively used scripts** (controlling playout, rfid tiggers, etc.)
    * some possible services and features might live in the *components* directory (see below)
    * if one or more scripts are needed for the activation of a component (like daemons), they should be copied to the `scripts` directory during installation / activation
    * WHY? By copying, changes will NOT affect the github repo and make it easier for users to modify their components
* `components`
    * contains sub- und subsubfolders for additional features, services, hardware
    * **subfolders** are for categories (e.g. displays, soundcards) and are plural, even if there is only one
    * **subsubfolders** are specific hardware, services, features, protocols, etc. 

# How to contribute

Contributors have played a bigger role over time to keep Phoniebox on the edge of innovation :)

We want to keep it as easy as possible to contribute changes that get things working in your environment. There are a few guidelines that we need contributors to follow so that we can have a chance of keeping on top of things.

Development is done on the git branch `develop`. How to move to that branch, see below.

## Getting Started

* Make sure you have a [GitHub account](https://github.com/signup/free).
* Open an issue if one does not already exist.
  * Clearly describe the issue including steps to reproduce when it is a bug.
  * Make sure you fill in the earliest version that you know has the issue.
* Use the online line install script to get the box installed.
* By default this will get you to the `master` branch. You will move to the `develop` branch, do this:

~~~
cd /home/pi/RPi-Jukebox-RFID
git checkout develop
git fetch origin
git reset --hard origin/develop
git pull
~~~

The preferred way of code contributions are [pull requests (follow this link for a small howto)](https://www.digitalocean.com/community/tutorials/how-to-create-a-pull-request-on-github). And ideally pull requests using the "running code" on the `develop` branch of your Phoniebox. Alternatively, feel free to post tweaks, suggestions and snippets in the ["issues" section](https://github.com/chbuehlmann/RPi-Jukebox-RFID/issues).


## Making Changes

* Create a topic branch from where you want to base your work.
  * This is usually the master branch.
  * Only target release branches if you are certain your fix must be on that
    branch.
  * To quickly create a topic branch based on master, run `git checkout -b
    fix/master/my_contribution master`. Please avoid working directly on the
    `master` branch.
* Make commits of logical and atomic units.
* Check for unnecessary whitespace with `git diff --check` before committing.

~~~
      Added shuffle mode and RFID controls for it (issue #130) #140
      
      Adds a shuffle mode for MPD to be triggered by RFID card.
      The shuffle mode stays permanently active until deactivation (also after shutdown and reboot).
      That is why i decided to automatically set random off (if currently active) during shutdown 
      and reboot.
      
      Scenario: You use your toddlers phoniebox as party jukebox in the evening and shuffle over 
      folders with your music and forget to deactivate the shuffle mode.
      Next morning your toddler gets crazy because his preferred fairytale plays the chapters in 
      random mode => Therefore the automatism
      
      Update: This time without the need to create an extra random.txt file.and uptodate with the 
      master branch.
~~~
## Making Trivial Changes

For changes of a trivial nature, it is not always necessary to create a new issue. 
In this case, it is appropriate to start the first line of a
commit with one of  `(docs)`, `(maint)`, or `(packaging)` instead of a ticket
number.

For commits that address trivial repository maintenance tasks or packaging
issues, start the first line of the commit with `(maint)` or `(packaging)`,
respectively.

## Submitting Changes

* Push your changes to a topic branch in your fork of the repository.
* Submit a pull request to the repository.
* The core team looks at Pull Requests on a regular basis.
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
of its discovery, the commit(s) responsible _may_ be reverted, at the
discretion of the committer and Phonie maintainers. 
The original contributor will be notified of the revert. 

### Summary

* Changes resulting in test failures will be reverted if they cannot
  be resolved within one business day.

## Guidelines ##
* Currently Phoniebox runs on Raspian **Buster** and **Stretch**. Therefore all Python code should work with **Python 3.5**. Some existing code may still be Python 2, but new code has to be compatible with Python 3.5 and old code that is changed should then be ported to Python 3.5.
* For GPIO all code should work with RPi.GPIO. gpiozero is currently not intended to use.

## Additional Resources

* [General GitHub documentation](https://help.github.com/)
* [GitHub pull request documentation](https://help.github.com/articles/creating-a-pull-request/)
