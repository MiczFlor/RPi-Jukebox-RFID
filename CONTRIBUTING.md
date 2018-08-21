# How to contribute

Contributors are essential for keeping Phonie great.
We want to keep it as easy as possible to contribute changes that
get things working in your environment. There are a few guidelines that we
need contributors to follow so that we can have a chance of keeping on
top of things.

## Getting Started

* Make sure you have a [GitHub account](https://github.com/signup/free).
* Open an issue if one does not already exist.
  * Clearly describe the issue including steps to reproduce when it is a bug.
  * Make sure you fill in the earliest version that you know has the issue.
* Fork the repository on GitHub.

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

## Additional Resources

* [General GitHub documentation](https://help.github.com/)
* [GitHub pull request documentation](https://help.github.com/articles/creating-a-pull-request/)
