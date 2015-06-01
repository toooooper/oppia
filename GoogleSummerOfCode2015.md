# Update on GSoC acceptance #

Unfortunately, Oppia was not accepted as part of Google Summer of Code this year, so this page is now obsolete. If you're a student who'd like to take part in GSoC, you can view the list of selected organizations [here](https://www.google-melange.com/gsoc/org/list/public/google/gsoc2015).

We still welcome anyone who is interested in any of the projects below to contribute, and would be happy to provide guidance and mentoring. Please feel free to get in touch via the [Oppia developers mailing list](https://groups.google.com/forum/#!forum/oppia-dev) if you would like to help out!


---


# Introduction #

This page contains instructions for students who are interested in working on Oppia as part of [Google Summer of Code 2015](http://www.google-melange.com/gsoc/homepage/google/gsoc2015) (GSoC).

Please note that this year is the first time Oppia has participated in GSoC, and we do not yet know whether our application will be accepted or how many student slots we'll be allocated. For a description of the GSoC timeline, please see [this page](http://www.google-melange.com/gsoc/events/google/gsoc2015).

Note that while working on Oppia for GSoC students will be asked to proactively maintain contact at least once a week via meetings or requests for reviews of code and/or design docs, as well as keep a regular public log of their work and update it at least once every two weeks. The finer details of how to do this should be worked out with your mentor.


# Things to do #

  * Join the [Oppia developers mailing list](https://groups.google.com/forum/#!forum/oppia-dev) and introduce yourself! This helps us to get to know you, and you can also use the list to get feedback on ideas for projects, as well as to get help as you start working with the codebase.
  * Get a development instance of the Oppia server set up on your machine. You can find instructions for doing this [here](https://code.google.com/p/oppia/wiki/GettingStarted).
  * Write and submit a proposal to the [Google Summer of Code website](https://www.google-melange.com). When writing your proposal, please follow these [guidelines](http://en.flossmanuals.net/GSoCStudentGuide/ch008_writing-a-proposal/), with the following amendments/additions:
    * There is no formal length limit, but please be concise.
    * The most important sections are "deliverables" and "biographical information"; you can skip "related work" if you wish.
    * In the "deliverables" section, please ensure that your proposal makes clear that you've looked at the [codebase](https://code.google.com/p/oppia/source/browse/) and/or relevant [wiki documentation](https://code.google.com/p/oppia/wiki/CodebaseOverview). Ideally, it would reference specific places to which you would be making changes.
    * If you've created any explorations on the [oppia.org](https://www.oppia.org) site that you’re particularly proud of, feel free to link to them!
    * At the end of your proposal, please include a brief description of some small improvement to the codebase (this may be something you've noticed while using Oppia, or an issue already filed in our [issue tracker](https://code.google.com/p/oppia/issues/list)). You are welcome to implement the change immediately, in which case please make a clone of our codebase following these [instructions](https://code.google.com/p/oppia/wiki/MakingAChange) and link to the corresponding commit(s) in your proposal. Alternatively, you can wait for us to notify you that we are interested in your application, at which point we would be happy to help you work through the process of making the change and committing it.
  * How to reach us: If you need help understanding the existing system, please feel free to ask the community! You can use the [oppia-dev@](https://groups.google.com/forum/#!forum/oppia-dev) mailing list for technical questions and the [oppia@](https://groups.google.com/forum/#!forum/oppia-dev) mailing list for non-technical ones. You can also use this forum to talk to the mentors for the projects suggested below.

## List of project ideas ##

Here is a list of project ideas. Note that we also welcome ideas not present on this list, so please feel free to suggest them. Oppia’s overall aim is to make it possible for anyone to learn anything they want to in an effective, enjoyable way, and anything contributing towards this goal is ‘in scope’.

Generally, all projects require work in Python and HTML/CSS/AngularJS. We’ve classified projects into the categories of backend, frontend and full-stack, which correspond respectively to ‘more Python-oriented’, ‘more HTML/CSS/AngularJS oriented’, or ‘both’.


### Make it easy for users to improve learning material ###
**Aim:** Invent mechanisms that make it easy for users to suggest improvements to existing learning material, so that explorations on the site do not stagnate, and can be continuously improved over time. Part of this involves some “design of the rules” -- e.g., should explorations be released for general editing if the original creator fails to respond to suggestions or requests for improvement? The aim is to design and implement a system that ensures that explorations do not stagnate.

  * **Category:** Full-stack
  * **Difficulty:** Open-ended
  * **Possible mentors:** Marcel Schmittfull

### Improve the statistics that we offer to exploration creators ###
**Aim:** We would like to understand the degree to which explorations are more or less effective than other forms of teaching, as well as determine what attributes/features are common to the ‘best’ explorations. The aim of this project is to define effectiveness, run studies that measure it, and create visualizations that help exploration creators easily determine when and how a exploration needs to be improved, so that they can do so.

  * **Category:** Full-stack
  * **Additional skills:** Familiarity with statistics, a willingness to do research and user testing
  * **Difficulty:** Open-ended
  * **Possible mentors:** Marcel Schmittfull
  * **Other contacts:** Stephanie Federwisch

### Create interactions to support particular types of content ###
**Aim:** Oppia has an [extensible framework](https://code.google.com/p/oppia/wiki/CreatingInteractiveWidgets) for creating ‘interactions’ which provide a UI for learners to interact with it; these interactions range from a numeric input field to a clickable world map to a music staff. However, we are aware that there are other useful interactions that we do not yet support. Students should therefore propose a vision for an educational experience they would like to create, but which Oppia does not currently support. The project would then be to make use of Oppia’s extension system to add the types of interactions they need to create that experience. To give a concrete example: in the context of mathematics, it might be useful to have an interaction that runs checks on equations written by students to see if they are equivalent to a particular one.

  * **Category:** Mostly frontend
  * **Additional skills:** teaching experience, expertise in some area that you would like to convey and share with others
  * **Difficulty:** Open-ended
  * **Possible mentors:** Sean Lip and Abraham Mgowano


### Make Oppia fully-responsive ###
**Aim:** All pages of the Oppia site should be easy to use on a phone or a tablet.

  * **Category:** frontend
  * **Additional skills:** UI design
  * **Difficulty:** Open-ended
  * **Possible mentors:** Sean Lip, Amit Deutsch and Abraham Mgowano


### Internationalize Oppia ###
**Aim:** The platform text for Oppia's learner pages should be displayable in at least 30 different languages, and the interface for non-English-speaking users should be intuitive.

  * **Category:** frontend
  * **Difficulty:** Medium
  * **Possible mentors:** Sean Lip and Abraham Mgowano


### Implement a recommendation system ###
**Aim:** After a learner has played through an exploration, we would like to display recommendations to them (that would be most useful to them) for which explorations to play next. We would also like to highlight such explorations in their dashboard, or on the main page of the site. These recommendations should be useful to learners and the recommendation system should be self-correcting based on online feedback (i.e., learners might indicate in some way that a recommendation is or isn’t useful to them, and the design of the system should incorporate a way to take this feedback into account when making future recommendations).

  * **Category:** full-stack
  * **Additional skills:** familiarity with recommendation systems and machine learning
  * **Difficulty:** Open-ended
  * **Possible mentors:** Sean Lip


### Integration test infrastructure ###
**Aim:** [Integration tests](https://code.google.com/p/oppia/wiki/WritingIntegrationTests) provide a valuable way to ensure that regressions do not make it into the codebase. However, they take a long time to run and are not currently parallelized. They also don’t fail gracefully -- so, when a developer causes a test failure in test #4, the remaining tests from #5 onwards automatically fail. This leads to inefficiencies when a developer decides to take a break for the tests to run, and returns after 15 minutes to find that it failed on the 4th step; it also makes fixing the tests very incremental since only one error is displayed at a time. The output from the integration tests is also very verbose, and this can obscure failure messages. The ideal integration test framework would run fast, and display all errors in each run. Note that contributions to this project may involve contribution to other upstream repositories like Protractor, on which our integration tests are based.

  * **Category:** full-stack
  * **Difficulty:** Hard
  * **Possible mentors:** Sean Lip
  * **Other contacts:** Jacob Davis