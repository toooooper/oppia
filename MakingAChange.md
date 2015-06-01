# How to make and submit a code change #

Thank you for contributing code to the Oppia project! Before submitting anything, please note the following points:

  1. Please note that, before we can accept any commits you make, you'll need to sign a [Contributor License Agreement](https://developers.google.com/open-source/cla/individual).
  1. Make sure you're developing based on the latest version of the 'develop' branch. Please see the [Development Workflow](DevelopmentWorkflow.md) page for more information.
  1. Make sure that your code is tested and doesn't break existing tests.
    * You can find out more about how to run tests [here](SettingUpTests.md).
    * As far as possible, write new tests that exercise the functionality of your code. If it's a bug fix, write a test that passes with the fix and fails without it. If it's a new feature, please try and cover most of the expected behavior with tests so that future contributors don't break your code.
    * Start up a local instance of Oppia by following the [setup instructions](https://code.google.com/p/oppia/wiki/GettingStarted), and make sure that your change behaves as expected (and doesn't break other things!)
  1. For consistency, please try to conform to the following style guides: [Python](http://google-styleguide.googlecode.com/svn/trunk/pyguide.html), [Javascript](https://google-styleguide.googlecode.com/svn/trunk/javascriptguide.xml). In addition, code should be formatted in a way that is consistent with other code surrounding it. Where these two guidelines differ, prefer the latter.

Does the code pass all tests? Does it look consistent with other code? If so, you can submit it for review!

  1. First, let's find somewhere to put your code so that a reviewer can see it and comment on it.
    * You can clone the Oppia repository to another code.google.com repository and make your changes there. Instructions for making a code.google.com clone of the Oppia repository can be found at the bottom of [this page](https://code.google.com/p/oppia/source/checkout). Note that, for the startup and test scripts to run, you will need to rename the folder containing the code to '`oppia`'. In addition, please click the checkbox in Administer > Source that says "allow non-members to review code", so that it is possible for the reviewer to leave comments on it. While developing on your clone, please follow the procedure on the [development workflow](https://code.google.com/p/oppia/wiki/DevelopmentWorkflow) wiki page -- start from the 'develop' branch and make a feature branch with your commits. This makes it easier for reviewers to see how the change would subsequently look like in the Oppia repository, and will also give you practice with the git workflow that the development team uses.
    * If you already have commit access to the Oppia repository, you could make a [feature branch](UsingGit.md).
    * If none of these work for you, please let us know: send an email to `admin@oppia.org`.
  1. When you're done, create a new review request using our [issue tracker](https://code.google.com/p/oppia/issues/list). One of the developers will get in touch by email within a couple of days (usually sooner). We'll get it reviewed and, if all goes well, pull it in.

If you have any questions at all about this, please send an email to us at `admin@oppia.org` -- we'd be happy to help! Also, if you have any feedback or suggestions for improvements to this process, we'd love to hear them.

You might also be interested in our [How to Contribute](Contributing.md) page, which has plenty of suggestions for ways to contribute (that both do and don't involve writing code).