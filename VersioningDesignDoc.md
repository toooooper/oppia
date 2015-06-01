# Design Doc: Exploration Versioning #

This is a proposal for implementing versioning of explorations in order to support collaborative editing. It is a work in progress; comments are welcome.


## Summary ##

  * we need to version explorations and make it really easy to revert bad changes.
  * explorations only get versioned after they are 'published' (made collaboratively editable and visible to readers)
  * the ExplorationModel/StateModel will always store the version at HEAD.
  * when a user changes an exploration/state:
    * we update the ExplorationModel/StateModel
    * we serialize and save the exploration into an ExplorationSnapshotModel with a version number.
  * When a user reverts to a previous version:
    * we find and reconstitute the old version
    * we follow the above instructions for ‘user changes an exploration/state’, using a new version number.
  * In each snapshot, we should include metadata or a commit message of some sort, e.g. “Reverted to version 2”.

## Milestones ##
1. Convert the current one-person-editing case to be a special case of the multi-person workflow, and make sure everything still works for this one-person-editing case.
  * When an exploration is requested by the frontend editor, send the version number of the current datastore model with it. Include this version number in SAVE requests.
  * When a SAVE event comes in from the exploration, check that the version number matches the datastore version.
    * If it doesn’t, display an error message to the user; do not commit changes.
    * If it does, add a new snapshot instance and update the HEAD instance, all in a single transaction.

2. Implement reverting mechanism.
  * Add logic to reconstitute the old exploration from an existing snapshot.
  * Separate out the content of a snapshot from the snapshot metadata in the model layer, so that these things can be queried independently. (We only care about the former in the ‘preview and revert’ case, and the latter in the ‘version history’ case, so there’s not much point in bundling them as we currently do.)
  * Allow user to preview the YAML of the exploration he/she wants to revert to (in order to compare with the current exploration) before making any reverts. This makes an AJAX call to the backend to fetch the snapshot content.
  * In the preview dialog, add a ‘revert’ button in the editor UI. This sends a command to the backend to reconstitute the old version and save a new version to the datastore (with an appropriate commit message).

3. Handle exploration deletion correctly.
  * An exploration can only be deleted by an admin or its creator.
  * Mark explorations as deleted, rather than actually deleting them, so that they can be restored later if the admin/creator desires to do this. This might involve moving them to a DeletedExplorationModel so that they don’t show up in queries for all explorations.

4. Readable diffs.
  * In the backend, deduce which fields have changed, and add their addresses as a prefix to the commit message in some kind of standard format so that it is easy to see what has changed (this will also help us compute diffs). So commit messages will look something like

```
    [20] (Aug 24 2013, 00:41 by admin) [params, state.Initial_State.param_changes] 
         Allow classification based on reader’s skill level.
```

  * Currently, the possible addresses are (using generic state/handler names):
    * params (this represents exploration parameters)
    * state.Test\_Your\_ABCs.name
    * state.Test\_Your\_ABCs.content
    * state.Test\_Your\_ABCs.param\_changes
    * state.Test\_Your\_ABCs.widget.widget\_id
    * state.Test\_Your\_ABCs.widget.params
    * state.Test\_Your\_ABCs.widget.sticky
    * state.Test\_Your\_ABCs.widget.handlers.submit.rules

5. Improve the granularity of SAVE actions.
  * Require the user to explicitly save; don’t save on every tiny change. E.g. if you save directly after a new state is added, that new state won’t contain anything of interest and would make no sense to readers. It isn’t a point we’d ever want to revert to. (Basically, put only interesting things in the history log.)
  * Store diffs in a frontend queue and send only the list of diffs to the backend when the user clicks the save button. This is better than sending the entire exploration/state.
  * Apply the diffs to get a new exploration model, and save it as a snapshot.

6. Decide on the policies for collaborative editing in order to build a flourishing community. We want to minimize friction and create a positive feedback loop for contributors. We also need ways to deal with abuse.
  * Who can edit explorations? Anyone? Readers who have finished successfully? Readers who have either finished successfully or have spent an hour on it? (The potential for abuse may not matter so much here because we will, by then, have a mechanism for easy reverting.)
  * Do we need a review mechanism? But this slows things down (and, again, we have a mechanism for easy reverting…). The main use case here, I think, is if the contributor wants to get a second opinion before committing a change.

7. Better handling of diffs and merges.
  * If multiple people are viewing the same page, ask these people if they want to auto-save if they have made a change but not committed it in the last 5 minutes. Point out that there is a danger of someone else making a change and that their changes might be overwritten.
  * Use the channel API to propagate changes by one user to other users editing the same exploration, and to ask the other users to reload.

### An idea ###

In addition to the datastore, consider using external persistent storage to store the explorations -- e.g., logging into Oppia creates a GoogleCode/GitHub repo for the user and all explorations get saved in there as yaml (the repo takes care of the revision history). Then the server just keeps track of pointers to the published explorations from everybody, as well as the ‘active/default’ version of the exploration that they intend to show to users.