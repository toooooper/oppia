### Introduction ###

Code review is an important part of the Oppia development cycle. Having a second pair of eyes look at your code can help to catch silly mistakes and serve as a check for whether your code is readable/understandable by other team members (which is important for maintainability).

This page will explain how to use the code review tool, and the conventions we currently use for code reviews.

### Before the review: squashing commits ###
If you have a bunch of small unreviewed commits, you might want to squash them into a single large commit before they are reviewed. To squash the last three commits, do
```
     git reset --soft HEAD~3 &&
     git commit -m "{{YOUR_COMMIT_MESSAGE_HERE}}"
```
Be careful to only squash "local" commits -- never squash anything that has been uploaded to the codesite before (no matter what branch). In particular, don't squash commits that already have code review comments on them. Also, don't squash any commit that merged two branches.

If you want to squash commits that you previously pushed to the codesite, make a new local branch that includes the small commits, squash the commits locally, and push the new branch.

### To request a code review ###

  1. Go to the [list of changes](https://code.google.com/p/oppia/source/list) page and click "Request code review" in the sub-navbar.
  1. Fill out the form shown. Add the main reviewer to the 'Owner' field, and other reviewers to the 'Cc' field.
  1. Click the 'Submit' button. This creates a new issue in the issue tracker and notifies the recipient of the review request by email.

### When you receive a code review request ###

  1. Please try to do the review as soon as possible! Often, the person who submitted the request is going to be blocked until the review is completed.
  1. Click on the links given by the requester to see the commits to review. For each of those, click one of the 'diff' links to see a side-by-side view of the files to review. You can leave inline comments by double-clicking the relevant lines in the file. Here are some of the things to look out for when doing a code review:
    * Do you understand what the code is doing? If not, it's probably the writer's fault, and you should tell him/her so.
    * Is the code doing the correct thing?
    * Does the design look sensible?
    * Are there tests/docs which should be present, but aren't?
    * Consider checking out the branch and looking at it in a browser, if the change affects the UI. Does the UI look good and intuitive to the user?
      * **Note:** to do this, run
```
    git pull
    git checkout {{BRANCH_NAME}}
```
  1. When you've finished, click 'Publish your comments' in the top-right.
  1. Return to the commit page, scroll down, add a general comment if necessary, and score the review.
    * If you like the change, say LGTM ('looks good to me!') and give it a +1. This marks the change as "has been reviewed and does not need to be looked at further".
    * If you like the change, but have one or more comments that you want to ensure are followed up on, give it a -1. This does not mean "I don't like it", despite what the code review form says. It means "This code review is unresolved; please follow up on these comments and either fix them or respond to them."
      * When you subsequently get a reply or resolution from the code author, go back to the -1 and change it to a +1 to indicate "this has been reviewed, and does not need to be looked at further".
      * Also, please note it is the **reviewer** who should change the -1 to +1, not the code author.
    * If you don't like it, give it a -1 and make your intentions clear in the 'general message' field -- e.g., ask that the commit be reverted.
  1. Click the Submit button at the bottom of the page to submit the review.

### When you, as an author, receive a code review ###
  1. Fix (or respond to) the issues raised, and leave inline comments by double-clicking the relevant lines in the code diff views. Each comment should be either 'Done' or a response explaining why the corresponding suggestion was not implemented.
  1. Push a subsequent commit to the same branch with the fixes (if applicable).
  1. Add a general comment pointing to your new commit, and click the Submit button at the bottom of the page to submit your responses. This will send an email alert to the reviewer, who will continue the review.
  1. Do not merge your change into 'develop' until you get a +1!

**Note:** You don't have to file a subsequent review request on the issue tracker if you are making a commit that addresses points raised in an existing review -- your reviewer will automatically get an email alert once you reply to his/her comments on the existing review.

### Merging into 'develop' ###

With the above scoring system, it should be straightforward to tell from the summary of changes whether any commits are still in need of resolution: just look for anything red (-1). Please wait until all red marks have been resolved before merging the branch into 'develop'.