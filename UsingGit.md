# Basic Git Commands #

This page outlines some basic git commands for developers new to Git.

1. After [cloning Oppia](https://code.google.com/p/oppia/source/checkout), you can make code changes in your local directory, under oppia/ . These changes will be tracked by Git. At any time, you can check what git thinks has been changed using:

```
   $ git status
```

Note that new files will need to be explicitly 'git add'ed.

You can also view diffs of your changes by typing:

```
   $ git diff
```

2. To sync your local code with the latest updates from the code.google.com repository, run:
```
   $ git pull
```

3. When you are ready to commit a change to your local Git repository, run:

```
   $ git commit -a -m [COMMIT_MSG]
```

where [COMMIT\_MSG](COMMIT_MSG.md) is replaced by a commit message in quotes, e.g.:

```
   $ git commit -a -m "Add a new graphical editor."
```

4. When you are ready to push changes to the code.google.com repository, run:
```
   $ git push origin develop
```

If the push is successful, you should see something like this:
```
   Counting objects: 33, done.
   Delta compression using up to 8 threads.
   Compressing objects: 100% (15/15), done.
   Writing objects: 100% (17/17), 1.93 KiB, done.
   Total 17 (delta 14), reused 0 (delta 0)
   remote: Scanning pack: 100% (17/17), done.
   remote: Storing objects: 100% (17/17), done.
   remote: Processing commits: 100% (1/1), done.
   To https://committer%40example.com@code.google.com/p/oppia/
      2b6a42d..e7fd1e7  develop -> develop
```

5. To download a branch someone else created:
```
   $ git pull
   $ git checkout <branch-name>
   $ git pull origin <branch-name>
```

6. To patch a specific commit onto a different branch:

```
   $ git checkout <branch-to-patch-from>
   $ git format-patch -1 # goes back one commit
```
This should create a file with the extension .patch. The name should include part of the commit message from the change it is patching. You may need to move this file to somewhere where it won't disappear when you switch branches.

```
   $ git checkout <branch-to-patch-to>
   $ git apply <patch-file-name>
```