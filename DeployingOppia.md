# Deploying Oppia to the web #

You can deploy your own instance of Oppia on Google App Engine as follows:

1. Create a new App Engine instance at https://appengine.google.com/ . When you do this, you will be asked to pick a name for your application. In the following, we will refer to this name as [APP\_NAME](APP_NAME.md).

2. Change the application name in the first line of the app.yaml file to [APP\_NAME](APP_NAME.md) (instead of 'oppiaserver', which is the application name for the demo server).

3. From the oppia/ directory, run the build script:
```
    python scripts/build.py
```

This generates minified HTML, JavaScript and CSS files in the core/templates/prod/head directory that will be used by the production server.

4. From the oppia/ directory, run the command
```
      ../oppia_tools/google_appengine_1.9.11/google_appengine/appcfg.py update .
```
(Note the period at the end.) This will initiate a deployment.

5. Check that your deployment has succeeded by visiting your instance on the Web at:
```
      https://[APP_NAME].appspot.com
```