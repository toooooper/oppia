# State Editor: Parameters #

When crafting an exploration, it is sometimes useful to keep track of 'parameters' that are specific to a particular learner, especially if you want to ask different questions depending on what the learner has already done or seen. For example, in an earlier part of the exploration, the learner may have encountered a question which uses the number 164. If you want to use this information in another state, you can define a parameter `x` to be 164, and in the second state you can refer to `x` to get the value used in the earlier state. Note that this information is not associated with the learner in the long term, and is only maintained within the context of a single playthrough of an exploration.

In general, Oppia allows you to define arbitrary parameters, store and change their values, and display and use these values in the exploration. Parameters are scoped to the entire exploration, regardless of where you first define them. Examples of applications of parameters include:
  * Remembering the learner's name
  * Randomizing a question by picking a different value every time the learner plays it
  * Keeping track of things the learner has done or seen already

## Special parameter: "answer" ##

The "answer" parameter is built into all Oppia explorations. Its value is the latest answer provided by the learner. So, if the learner just answered the question "what is your name?", in the next state, the "answer" parameter will be set to the learner's name.

## Using Parameters ##

You can refer to a parameter (or expressions whose values are computed using parameters) in the 'content' and 'rule feedback' sections of any state. To do this, write `{{YOUR_EXPRESSION}}`, where "YOUR\_EXPRESSION" is the expression you want to compute. For example, `{{answer}}` gives the latest answer provided by the reader, as described above.

The following expression types are supported:
  * `{{a}}`
    * Returns the value of parameter a.
  * `{{a+b}}`, `{{a-b}}`, `{{a*b}}`, `{{a/b}}`, `{{a%b}}`
    * Performs the indicated operation on parameters a and b, coercing them to numbers first if necessary. Numbers can also be substituted for a and/or b, e.g. `{{a+3}}`.
  * `{{a<=b}}`, `{{a>=b}}`, `{{a<b}}`, `{{a>b}}`, `{{a==b}}`, `{{a!=b}}`
    * Performs the indicated comparison on a and b, returning true or false as appropriate.
  * `{{a&&b}}`, `{{a||b}}`
    * Performs the indicated computation on a and b, returning true or false as appropriate.
  * `{{if a then b else c}}`
    * Prints the value of b if a is true, otherwise prints the value of c.
  * `{{floor(a)}}`, `{{pow(a, b)}}`, `{{log(a, base)}}`, `{{abs(a)}}`
    * Performs the indicated mathematical operation and prints the result. These functions coerce their arguments to numbers first, if necessary.

## Setting and Changing Parameters ##

You can change a parameter's value either in a state or at the exploration level. The interface for doing this at both levels is similar.

### State-level Parameter Changes ###
At the top of a state page, there is a list of all the parameter changes that will happen when that state is entered. You can add a new parameter change by clicking the "Add Parameter Change" button, or edit an existing parameter change specification by clicking on it.

You will have to specify the name of the parameter you want to change, as well as the expression you want to change it to. **Please note that parameter names can only include letters and numbers, and that they are case-sensitive.**

If you specify a parameter name that doesn't exist yet, a new parameter will be automatically created. This parameter can then be changed and used anywhere within the exploration.

### Exploration-level Parameter Initialization ###

On the exploration page, click on the plus sign next to "Exploration Metadata" to see information about the exploration, including a list of parameters that exist for this exploration. All the parameters you have ever defined and changed in the state-level parameter change interface, as described above, will be listed here.

You can also set initial values for the parameters. When an exploration starts, any parameter changes which are specified in the list of exploration-level parameter changes are applied before the learner enters the first state.


## Examples ##

### Remembering the learner's name ###

You can make a state that asks the reader for her name, and that takes a text answer. In the following state, the `{{answer}}` parameter will hold the user's name, since this would be the last answer entered. You could create a parameter change at the start of this state that sets a new parameter, `name`, to the value `{{answer}}`, selecting the option to evaluate parameters. What this will do is allow you to then use the `{{name}}` parameter in any subsequent state to display the reader's name. Note that the `{{answer}}` parameter can't be used long-term since it will always be overwritten with the most recent answer provided.

### Randomizing your exploration ###

Suppose you wanted to write an exploration involving two numbers which could take values at random between 1 and 5. You can do this by creating an exploration-level parameter (say, "firstNumber"), and listing all the values that it should be able to take.

In the state that uses the parameter, write {{firstNumber}} instead. Whenever a reader starts this exploration, Oppia will pick one of the possible numbers you specified for the parameter, and replace {[firstNumber}} with it.

### Mad Libs! ###

You can make states that ask the player to provide an adjective, noun, etc. and store these in parameters, in a similar way to the name-remembering example.
Then you can insert these into a Mad Libs text and display the result to the reader. You can even allow the reader to go back and change any of these values by returning to the states where you asked them to provide these words.

### Counting tries ###

You can use a parameter to keep track of the number of times the reader has tried a certain question. Initialize the parameter to be 0 in the settings tab. Then, in the state that you want to count, increment the parameter by setting it to the expression "{{num + 1}}", where "num" is the name of your parameter.