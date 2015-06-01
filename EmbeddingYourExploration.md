# Embed the exploration #

Oppia explorations that have been published can be easily embedded in other web pages. Just copy the Oppia embedding script below into the source code for your webpage, then add individual `<oppia>` HTML tags for each exploration you want to embed. You only need to include the embedding script code once; it will do all the work of embedding the explorations for you. (The instructions below are generic, but you can find URLs tailored to the particular exploration you want to embed by going to the corresponding exploration editor page and clicking the embed button on the top-right.)

**Important:** Please note that, since private explorations are not world-viewable, they cannot be embedded in other pages.

### Step 1: Include the embedding script ###

Option 1: Use one of the hosted scripts, by including one of the following codes on your page:

  * jsDelivr:
```
  <script src="//cdn.jsdelivr.net/oppia/0.0.1/oppia-player.min.js"></script>
```
  * CDNjs:
```
  <script src="//cdnjs.cloudflare.com/ajax/libs/oppia/0.0.1/oppia-player.min.js"></script>
```

Option 2: Download your own copy of the embedding script from the [static/scripts directory](https://code.google.com/p/oppia/source/browse/#git%2Fstatic%2Fscripts) and add it to your page as follows:

```
  <script src="//path/to/your/oppia-player.min.js"></script>
```

### Step 2: Add individual `<oppia>` tags ###

In each place where you want to embed an exploration, add an `<oppia>` tag that is structured as follows:

```
    <oppia oppia-id="fjJDek214F2g" src="https://www.oppia.org" exploration-version="3">
    </oppia>
```

The meanings of the various attributes are as follows:

  * `oppia-id`: the id of the exploration (which you can find in the exploration URL; it's the string of random characters between /create/ and #/gui/).
  * `src`: the domain that hosts the exploration. If you are embedding an exploration from oppia.org, this will be `https://www.oppia.org`. If you have set up your own instance of Oppia, use the corresponding domain name for that instance instead.
  * `exploration-version`: this is optional. If it is not specified, the latest version of the exploration will be embedded. If it is specified, it represents the version number of the exploration that you want to embed; you can determine this by looking at the History tab on the exploration editor page. Specifying an `exploration-version` attribute means that the embedded exploration will never change (even if subsequent changes are made to the original exploration), but it also means that you would have to update the version number on a regular basis if you wanted to incorporate these subsequent changes.

### Step 3: Check that everything works ###

That's it, you're done! Navigate to the page containing the exploration and check that everything works. If the exploration does not load, open the [development console](http://webmasters.stackexchange.com/questions/8525/how-to-open-the-javascript-console-in-different-browsers) in your browser, and check to see if there are any errors.


# Advanced options #

### Integration with particular platforms ###

We also have support for integration with platforms such as [Course Builder](https://code.google.com/p/course-builder/). More information can be found in the `integrations` subdirectory of the [Oppia source code](https://code.google.com/p/oppia/source/browse/#git%2Fintegrations).

### Event hooks (optional) ###

When a learner interaction happens within an Oppia exploration, an event is emitted to the embedding page. If you wish, you can listen to these events and add custom behavior to them. This is done by overwriting, in the embedding page, the corresponding event hooks -- so, for example, if you wanted to print a message to the console when an exploration is loaded, you could write:
```
  window.OPPIA_PLAYER.onExplorationLoadedPostHook = function(iframeNode) {
    console.log('Exploration loaded.');
  };
```

Other events are also emitted on state transitions or exploration completion. For more details, please see the bottom of the [embedding script file](https://code.google.com/p/oppia/source/browse/static/scripts/oppia-player-0.0.1.js).