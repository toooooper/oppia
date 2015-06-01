# Design Doc: Value Generators for Parameters #

## Status ##
Implemented as described in [issue 47](https://code.google.com/p/oppia/issues/detail?id=47).

## Summary ##
  * The parameter model in Oppia is a bit confusing, and needs to be clarified.
  * Currently, parameter generation is done by random selection from a finite list. However, there are use cases for, e.g., generating a random integer in the range [1, N], and generating a random string from a given length and character set.
  * The current parameter model also cannot easily support the natural use case of restricting a widget parameter to a given set of choices. This is because, for this use case, the parameter editor itself needs to be customized. An example where this functionality is needed is the code widget: the language used (Python, Coffeescript, etc.) needs to be specified in the widget editor, but it must be a string that is selected from a particular set of choices.
  * There is some confusion in the current parameter model as to what should and should not be parsed using Jinja.
  * There is also some confusion in the current parameter model as to when a parameter should be cast to a string for display.
  * There needs to be conceptual clarity for distinguishing between parameter instances and parameter value generators. The current Parameter domain object in Oppia actually represents the latter.

## Definitions ##
  * A **parameter** is a named, typed object whose value can be changed during runtime.
  * A **parameter instance** is a specific name-to-value pairing like `musicNote == 'B4'`.
  * A **parameter specification** is a (name, type) pair that describes the type of a particular parameter. It has no associated value.
  * A **value generator** is a function that generates a value based on customization arguments.

## Proposal ##

Remove the existing Parameter domain object class. In its place, create a new domain object class called ValueGenerator.

This is a bit like a Rule: it has a generator\_id field, which is a string identifier, and it has a customizable function which takes in a list of customization args and outputs an instance of the parameter; this function does not maintain any state. The ValueGenerator can also be initialized with additional attributes.

In addition, the ValueGenerator should have a generate\_sample\_values() method that allows it to generate a set of sample values based on customization args; these will be used for checking that a ValueGenerator specification outputs a value with the correct expected type.

Examples of ValueGenerators (these are subclasses of a base ValueGenerator class):
  * Copier: no initialization. It is called with a value and a 'parse with Jinja' flag. If the 'parse with Jinja' flag is switched off, it outputs a copy of the input value. If the 'parse with Jinja' flag is switched on, the value is treated as a template string, and the generator outputs this template string, evaluated against any other parameters that are currently defined.
  * RandomSelector: no initialization. When called with a list, it outputs a value that is randomly selected from this list.
  * RangePicker: no initialization. When called with an int, N, it outputs a random int in the range [1, N].
  * RandomStringGenerator: no initialization. When called with an int, N, and a string, S, it outputs a string whose length is N and whose characters are each drawn from the string S.
  * Accumulator: no initialization. When called with a list of numbers, it outputs an int or float that represents their sum.
  * ValidatedCopier: this is initialized with a list. When called with an arg, it checks whether that arg is in the list. If so, it outputs a copy of that arg. If not, it raises an error.

Each ValueGenerator should define a customization UI (such as the simple list editor currently in our widget customization GUI). These customization UIs need to handle both the cases where the inputs are parameter names and where the inputs are value objects.

### Data definitions ###

In the YAML file that defines an exploration instance (with all its states), there are two types of fields relating to parameters: the exploration parameters and the state-level parameter changes.

The exploration parameters field should contain a list of parameter specifications for all parameters occurring in the exploration. Each field should have the following:
  * The parameter's name.
  * The expected type of the parameter value.

The type information is needed here in order for us to be able to classify on parameters: we will need to be able to determine which classification rules make sense for a particular parameter. The parameter values are automatically cast to their expected type after they are generated.

Within states, the fields called 'param\_change' should have the following:
  * The name of the param, so that it can be referred to in the state content, feedback, etc., and so that its type can be inferred from the exploration parameters field.
  * The id of the ValueGenerator to use.
  * The customization args for the ValueGenerator.

Such 'param\_change' fields account for both parameter definitions (i.e., when their values are first set) as well as parameter changes (i.e., subsequent changes to an already-defined parameter within a state). In a reader playthrough, there is never a case where a parameter is 'active' but has not been given a value: when a param\_change is encountered -- either at the beginning of an exploration, at the beginning of a state, or within a rule -- the parameter with that name is found (or created, if it doesn't exist), and the generated value is assigned to it.

In the Python customization file that defines a widget, there is a field called params. Each such field should have the following:
  * The name of the param, so that it can be used in the widget template.
  * The id of the ValueGenerator to use.
  * The initialization args for the ValueGenerator.
  * Default customization args for the ValueGenerator.
  * The expected type of the parameter value.

Note that widget params should be confined to the widget instance's scope so that their names don't clash with parameter names in the outer scope. The parameters for a widget instance are not accessible by their containing states or explorations.

### Editor interface ###

When an editor sets a parameter in the state editor GUI (and, later, in each rule), they get to pick from any ValueGenerator which does not have an initialization method. (This is because the initialization of a ValueGenerator is meant to be a customization of the ValueGenerator's editor, and while such customizations make sense for individual widgets, they are not necessary for parameter editors in states, which should be generic.) The editor can then specify the args to that ValueGenerator.

When an editor sets a parameter in the widget customization GUI, they enter customization args for the given ValueGenerator (that has been defined in the widget .py file). These override the widget's default customization args.

In these two cases, existing exploration parameters can be used as the customization args. If this is done, their values are automatically copied, so that subsequent changes that occur in the widget code do not affect the original values.

What Oppia does in each case depends on whether the parameter has been previously set:
  * When an editor sets a parameter for the first time in a state, Oppia checks the exploration parameters field for that parameter's name, finds that it doesn't exist, and asks the editor to specify the type of the parameter. It then adds an entry to the exploration parameters field and updates the parameter change specification for that state.
  * When an editor sets a parameter subsequently, Oppia checks the exploration parameters field, retrieves the parameter's expected type, and then validates the generation method and args to ensure that the output has the given type. In the case where the args that are being passed into the generator are themselves parameter values whose types are known but whose values are otherwise not strictly determined, full validation will be tricky, but we can do it on a best-effort basis for now.

For now, an editor cannot change the type of a parameter after it has been declared and used in other states. We may implement something more flexible later that looks for other states in which the parameter is used and alerts the editor.

### Reader interface ###

When a reader encounters a state that sets a parameter, the parameter's value is determined by creating an instance of the corresponding ValueGenerator and calling it with the customization args that had been set by the editor. The reader has no direct input into this process. The value of this parameter will persist until it is actively changed by the exploration definition; in particular, it will not be automatically regenerated on each state transition.

Sometimes we will want to display parameter values directly in the UI. This could be handled cleanly with a Jinja filter that calls the to\_html\_string() method of the relevant object type.

## Example scenario ##

Person CC ('content creator') creates an exploration with two states, A and B, where A always leads to B. He goes to A's state editor, sets a new parameter, `favoriteNumber`, and specifies that it should be equal to (a copy of) 0. Oppia asks CC what the type of this parameter should be, and CC says it should be an int.

CC then goes to B's state editor, and specifies that `favoriteNumber` should be set to be one of ['one', 'two', 'three'] using an equalsOneOf() ValueGenerator. Oppia tells CC that this has the wrong type and refuses to accept the parameter change. CC changes the list to [1, 2, 3] and the parameter change is accepted.

In B's state editor, CC wants to display a NumericInput widget that makes use of `favoriteNumber` as a placeholder. So he loads the widget and then tries to customize it. The NumericInput already has a parameter called `placeholder` whose type is a number, and whose generator is the isCopyOf() generator. CC types 6 into the generator's custom UI (which is a single numeric input field) and hits save; the widget preview now shows that the placeholder is equal to 6. CC then types '{{favoriteNumber}}' into the generator's custom UI and hits save; the widget preview shows a '{{favoriteNumber}}' placeholder and somehow indicates that a parameter value would have been substituted here, were this displayed to a reader.

Person R plays CC's exploration. She goes to state A, and sees that favoriteNumber is 0. She then goes to state B, and sees that favoriteNumber is 2, and sees a NumericInput widget whose placeholder is 2.

## Implementation milestones ##

  1. Create a base ValueGenerator object class.
  1. Create subclasses of this base class (Copier, RandomSelector, etc.).
  1. Change existing widget classes to use these ValueGenerators, and change the exploration yaml for the sample explorations accordingly.
  1. Allow the definition of GUIs for value generators and use these in the widget customization modals.
  1. Change the exploration yaml for the sample explorations to use ValueGenerators throughout.
  1. Deprecate the Parameter domain object class.