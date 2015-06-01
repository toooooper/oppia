# State Editor: Rules #

Each state in an exploration includes a set of classification rules. When readers enter some input, Oppia classifies it according to these rules, and displays the appropriate feedback. It also makes any necessary state changes. Each interaction also has a default rule, which Oppia uses if none of the other rules match.

The types of rules for each interaction differ depending on what sort of input the interaction accepts. For example, a text input field may test whether the input contains a certain sequence of characters, whereas an interactive map may test whether the input click is within a given radius of a particular location.

## Viewing the rules for a state ##

You can find the rule editor below the interaction editor. The rules are listed as individual tiles, in the order in which they are applied to the reader's answer. The first rule that matches the answer will be used. If no rule matches, the default rule (which is always the last one) is used.

In the screenshot below, there are three rules: two equality checks, and one default rule.

<img src='http://wiki.oppia.googlecode.com/git/images/rules.png' width='300'>

The dark blue header of each tile describes the test that is being made on the answer. This is followed by a list of possible responses from Oppia (one of which is chosen at random) and a destination state. Note that the refresh symbol (⟳) in the destination column means that, if the corresponding rule is used, Oppia will return the reader to the same state.<br>
<br>
<h2>Editing the rules for a state</h2>

To edit a rule, click on the 'Edit' button in the right-hand column. To add a new rule, click the 'Add new rule' button, and choose the type of rule you want to add. In the example below, we check whether the input text contains a given string.<br>
<br>
<img src='http://wiki.oppia.googlecode.com/git/images/rules1.png' width='300'>

Clicking 'Select' brings us to a new page where we can specify the details of the rule. In this case, we want to check whether the reader's answer contains the word 'factorial'.<br>
<br>
<img src='http://wiki.oppia.googlecode.com/git/images/rules2.png' width='300'>

In this dialog box, you can also specify the destination state, as well as the feedback given to the reader. You can enter as many feedback responses as you like; one will be chosen at random and displayed to the reader if this rule is triggered. This helps to make the conversation less stilted. If you do not specify any feedback, none will be shown to the reader.<br>
<br>
<b>Important</b>: If the destination state is the same as the current state, and no feedback is given, the reader will be presented with the same input field with no indication that any interaction has occurred. In general, this is not a good user experience, and we recommend that you always either send the reader to a different state, or provide some useful feedback that would help him/her when trying again. To help you spot cases like this, we show a small warning sign next to rules that have no feedback and loop to the same state, and we display the header of the rule tile using a different colour.<br>
<br>
When you have finished editing your rule, click "Save". You can add further rules, and rearrange the existing ones. Note that <i>order is important</i>: an incoming answer is compared against each of the rules in sequence, so if multiple rules match a given answer, only the first one is triggered.<br>
<br>
<h2>Extending Oppia's rules</h2>

If the given rules are not sufficient, you can create new ones, though you will need to edit Python code to do so. However, depending on what you want to do, the edits may end up being quite minimal. See <a href='CreatingRules.md'>Creating New Rules</a> for more details on how to do this.