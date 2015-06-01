Oppia development is done using the 'gitflow' workflow. There is a good explanation of this workflow [here](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow); please take a look.

**IMPORTANT:** The central branch for development is called **develop**. In general, please do not push to **master** or to any of the hotfix or release branches (whose names will be prefixed by `hotfix` or `release`). Always use **develop**!

## Instructions for developing a new feature ##

For individual features, check out a new branch based off of **develop**. For consistency, pick a branch name that contains only lowercase letters and hyphens. Please **do not** prefix your branch name with 'hotfix' or 'release'; these keywords are reserved for special types of branches.

**Note: in the following, `<branch-name>` is a placeholder for the name of your branch.** Use lowercase letters and hyphens for the branch name. You do not need to type the '<' or '>'.

```
   $ git checkout develop
   $ git checkout -b <branch-name>      # This creates a new feature branch that is based on 'develop'.
```

Make commits and push to your individual branch as desired:

```
   $ git push origin <branch-name>
```

(OPTIONAL, only if your branch and develop are significantly out of sync) Every so often, pull other changes from **develop** into your feature branch, as follows:
  * Make **develop** up to date:
```
   $ git checkout develop
   $ git pull
```
  * Checkout your feature branch and pull the changes:
```
   $ git checkout <branch-name>
   $ git merge develop
```
  * Push these changes back to the code.google.com feature branch:
```
   $ git push origin <branch-name>
```

When the feature is complete:

  * get a code review from someone else by following the instructions here: [Code Review Guidelines](CodeReviewGuidelines.md).
  * when you get the review back, make changes accordingly and submit them in a further commit. Reply to each comment on the original review by double-clicking on the relevant line of code in the diff view of the commit, then click the "Publish your comments" link and submit your comments. Please address each comment made by the reviewer with either "Done" or a follow-up comment, since this makes it easier to keep track of what has been resolved and what has not.
  * when the review is successful, the reviewer will give a +1 and an LGTM. When this happens, you can merge the feature branch back into **develop** as follows:
```
   $ git checkout develop
   $ git merge <branch-name>
```
  * **Important**: run the tests and make sure they pass! Problems have been known to arise after a merge.
```
   $ bash scripts/test.sh
   $ bash scripts/run_js_tests.sh
```
  * Note: the output for passed tests differs between the first and second test scripts. With test.sh, the final output of the script will include a summary of the number of passed and failed tests. With run\_js\_tests.sh, the script will not end when the tests have completed, but Karma will state that Chrome is idle and no failed tests will be reported. When all tests pass, finish the merge and push your changes to the codesite:
```
   $ git push origin develop
```

Finally, delete the local and remote feature branches when they are no longer needed:
```
   $ git branch -D <branch-name>
   $ git push origin --delete <branch-name>
```