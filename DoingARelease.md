# How to do a release #

To release a new version of Oppia, follow the following steps:

0. If any changes have been made to the integrations\_dev folder or to /static/scripts/oppia-player-0.0.0.js since the last release, run the integrations release process and test these integrations. More information can be found [here](http://code.google.com/p/oppia/source/browse/integrations_dev/build_new_release.py).

1. Run the tests:
```
   bash scripts/run_js_tests.sh
   bash scripts/run_integration_tests.sh
   bash scripts/test.sh
```
Make sure they all pass.

2. Run
```
   bash scripts/start.sh
```
and play with the app for a while to make sure that nothing seems amiss.

3. Bump the version number by editing app.yaml, and update the CHANGELOG file.

**Note**: a handy way to get a summary of the most recent changes is:

```
   git log --pretty=format:"%h - %an, %ar : %s"
```
(In the future, we should consider also tagging changes with their commit hash, similar to [this](https://github.com/angular/angular.js/blob/master/CHANGELOG.md).)


4. Merge the release branch into both `master` and `develop`, and tag the new release:
```
   git checkout master
   git pull origin master
   git merge release-[VERSION_NUMBER]
   bash scripts/test.sh
   bash scripts/run_js_tests.sh
   bash scripts/run_integration_tests.sh
   git push origin master

   git tag -a v[VERSION_NUMBER] -m 'Version [VERSION_NUMBER]' master
   git push --tags

   git checkout develop
   git pull origin develop
   git merge release-[VERSION_NUMBER]
   git push origin develop
```

(replacing `[VERSION_NUMBER]` with the relevant version number, e.g. `1.1.0`).

5. Delete the release branch.
```
   git branch -D release-[VERSION_NUMBER]
   git push origin --delete release-[VERSION_NUMBER]
```

6. [Clone](https://code.google.com/p/oppia/source/checkout) a new copy of the Oppia repository, remove the .git subfolder, and zip everything else into a download file. If necessary, remove production files that are specific to an individual instance. Rename this file appropriately to include the date and version number, and push it to the `oppia.downloads` [repository](https://code.google.com/p/oppia/source/list?repo=downloads) using git.

7. Return to the oppia/ directory, and checkout the master branch.
```
   git checkout master
```

8. If you want emails to be sent to the admin on job failures, specify a valid email address in feconf.ADMIN\_EMAIL\_ADDRESS and set feconf.CAN\_SEND\_EMAILS\_TO\_ADMIN to True. You may also wish to edit cron.yaml and queue.yaml to change the times at which jobs are executed and the rate of job processing; if in doubt, use the default values. [**TODO**: make all these into deploy\_data settings.]

9. Update the test app at oppiatestserver.appspot.com by running
```
    python scripts/deploy.py --app_name=oppiatestserver
```
Note that data that is already in the datastore remains unmodified. You can reload demo explorations and do manual operations on the data via the [App Engine console](http://appengine.google.com).

10. If the `index.yaml` file has changed since the last update, update only the indexes on oppia.org by running
```
   ../oppia_tools/google_appengine_1.9.11/google_appengine/appcfg.py update_indexes . --oauth2
```
Wait for the indexes to finish uploading before proceeding with the next step.

11. Update the live server at oppia.org by running
```
   python scripts/deploy.py --app_name=oppiaserver
```
For this you will need the oppia.org deploy\_data folder, for which you should ask an Oppia administrator.

12. After updating the server, go to the App Engine console and flush memcache to remove stale data.

13. Announce the release in the [discussion forum](https://groups.google.com/forum/?fromgroups#!aboutgroup/oppia).

14. Update the [Development Status](DevelopmentStatus.md) page and the links on the front page of the codesite.

Congratulations, you've just made a release!