# Downloading and running a local instance of Oppia #

**Note: depending on what you want to do, you may not need to download and install anything.**
  * If you would like to create explorations, we have a hosted server at https://www.oppia.org. Please note that all published explorations on this server are world-viewable.
  * If you would like to try out Oppia to see how it works, you can play with a test server we've set up at https://oppiatestserver.appspot.com. This server is only meant for testing, and the content on it may be cleaned periodically.

On both these servers, you can play existing explorations without logging in, but you will have to log in to create or edit a new exploration -- this is so that we can tell who is allowed to edit which explorations.

If you would still like to download and run a local copy of Oppia, please follow the installation instructions below.

## Installing Oppia ##

The installation instructions on this page have been tested with Linux and Mac OS X. (In particular, they were last tested on 25 Feb 2014 with Linux Ubuntu 12.04 LTS, Linux Fedora 19 and Mac OS X Mavericks 10.9.)

For Windows installation instructions, please refer to [WindowsGuidelines](WindowsGuidelines.md) instead.

## Prerequisites ##

Oppia relies on a number of programs and third-party libraries. Many of these libraries are downloaded automatically for you when you run the `start.sh` script provided with Oppia. However, there are some things that you will need to do beforehand:

1. Ensure that you have [Python 2.7](http://www.python.org/download/releases/2.7/) and Java installed. (Java is needed for the code interaction.)
  * Linux: If in doubt then in a terminal run:
```
    sudo apt-get install default-jre
```

2. Make sure you have curl (which is used by the start.sh script for downloading third-party libraries).
  * Linux: In a terminal, run:
```
    sudo apt-get install curl
```
  * Mac: You should already have curl.

3. Ensure you have setuptools (which is needed to install coverage, which checks test coverage for the Python code).
  * Linux: In a terminal, run:
```
    sudo apt-get install python-setuptools
```
  * Mac: In the console, run:
```
    sudo easy_install setuptools
```

4. Download git. This allows you to store the source in version control.
  * Linux: In a terminal, run:
```
    sudo apt-get install git
```
  * Mac: Download git [here](http://git-scm.com/download/mac) (the download will start once you click the link), then run the package and follow instructions.


## Downloading Oppia ##

**Important note:** We suggest that you download Oppia into a **new, empty folder** on your computer, such as ~/opensource. This is because the Oppia installation process adds sibling folders to ~/opensource/oppia, such as ~/opensource/oppia\_tools. This is done in order to separate the files and folders that should be pushed to a production server (which are all in ~/opensource/oppia) from all other files and folders.

To get a copy of Oppia that you can play with on your own computer, either:
  * download the [latest release of Oppia](https://code.google.com/p/oppia/wiki/DevelopmentStatus), and unzip the file into a directory of your choice, or
  * (if you have git) clone the Oppia repository by following the instructions [here](https://code.google.com/p/oppia/source/checkout). If you are a developer, you may also want to checkout the `develop` branch by running the following command from the oppia/ root folder:
```
    git checkout develop
```

## Running Oppia on a development server ##

1. In a terminal, navigate to the `oppia/` root directory and run:
```
     bash scripts/start.sh
```

The first time you run this script, it will take a while (about 5 - 10 minutes when we last tested it in Feb 2014, though this depends on your Internet connection). Subsequent runs should be much faster. The `start.sh` script downloads and installs the required dependencies (such as Google App Engine) if they are not already present, and sets up a development server for you to play with. The development server logs are then output to this terminal, so you will not be able to enter further commands in it until you disconnect the server.

**Note**: The script will create two folders that are siblings of the `oppia/` root directory: `oppia_tools` and `node_modules`. This is done so that these two folders will not be uploaded to App Engine when the application is deployed to the web.

**Note**: If you run into errors while installing Oppia, please try deleting the directories
```
     ../oppia_tools/
     third_party/
     core/templates/prod/
```
and running `start.sh` again.

**Note**: Oppia uses the npm tool to install some packages. This tool accesses both ~/tmp and ~/.npm, and has been known to occasionally encounter permissions issues with those directories. You may need to either delete these directories and all their contents (if they do not contain anything else that needs to be preserved), or change their permissions so that they are owned by you, which you can do by running
```
    sudo chown -R {{YOUR_USERNAME}} ~/tmp
    sudo chown -R {{YOUR_USERNAME}} ~/.npm
```
where `{{YOUR_USERNAME}}` should be replaced by your username.

2. The `start.sh` script also opens up a development server at http://localhost:8181. At this address, you should see the welcome page and be able to play with your local version of Oppia. It should look something like this:

<img src='http://wiki.oppia.googlecode.com/git/images/defaultDevPage.png' width='300'>

You can also view the App Engine admin console at <a href='http://localhost:8000'>http://localhost:8000</a>.<br>
<br>
3. <b>Loading the demo explorations.</b> The default installation of Oppia comes with a set of <a href='http://code.google.com/p/oppia/source/browse/#git%2Fdata%2Fexplorations'>demo explorations</a>. On startup, none of these are loaded. To load the demo explorations, log in to your server as an admin, then click your username in the top-right corner and choose the 'Admin Page' option. This will open a new admin page which will allow you to load the demo explorations individually.<br>
<br>
4. <b>Shutting down the development server.</b> When you are done, you can shut down the development server by typing Ctrl+C into the terminal.<br>
<br>
<br>
<h2>Troubleshooting</h2>

<ul><li>If you get an error that ends with:<br>
<pre><code>    fancy_urllib.InvalidCertificateException?: Host appengine.google.com<br>
    returned an invalid certificate (ssl.c:507: error:14090086:SSL<br>
    routines:SSL3_GET_SERVER_CERTIFICATE:certificate verify failed): <br>
</code></pre>
try removing the <code>cacerts.txt</code> and <code>urlfetch_cacerts.txt</code> files as described <a href='http://stackoverflow.com/questions/13899530/gae-sdk-1-7-4-and-invalidcertificateexception'>here</a> and <a href='http://stackoverflow.com/questions/17777994/why-cant-i-launch-my-app-from-the-shell'>here</a>.</li></ul>

<h2>Next steps</h2>

<ul><li>Have a look at the <a href='CodebaseOverview.md'>codebase overview</a>, which describes how the Oppia code base is structured.<br>
</li><li>Learn how to <a href='MakingAChange.md'>make a code change</a>, or how to <a href='SettingUpTests.md'>set up and run tests</a>.<br>
</li><li>Read the <a href='DeployingOppia.md'>Deploying Oppia</a> page. This contains instructions for deploying your instance of Oppia to the web, so that other people can play with it.