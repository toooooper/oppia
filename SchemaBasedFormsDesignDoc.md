### Motivation ###

Oppia uses a lot of forms, and it is tiresome to have to write each one from scratch each time. This doc lays out an attempt to build a framework that allows such forms to be built declaratively. The mechanism used to do this is via a Python dict called a 'schema'.

There are several things that a schema can cover:
  * **How to present the form so that the input provided is valid.** For example, should the input field be text, numeric or multiple-choice?
  * **Validation.** What additional restrictions need to be placed on the input?
  * **UI niceties.** For example, should a placeholder be provided? Should the form be displayed in block form or inline? How large should the text input field be?

### General principles ###

This framework is meant to be a handy utility; it does not need to be all-encompassing. There should therefore be ways for developers to write:
  * a custom UI for a form
  * additional validators

Schemas defined in the backend for a given object type only care about specifying the restrictions that define the object (e.g. has type 'int', is between -180 and 180, etc.). This is done by incorporating validators.

There is a formBuilder in the frontend that takes a schema and generates a form whose return value satisfies the schema. The schema can be annotated with UI configuration options to tell the form how to display itself. A developer can use the formBuilder or create his/her own custom form; the only requirement is that the return type matches that defined by the schema.


### Description of schema ###
Each schema has a top-level field 'type' which is one of 'bool', 'int', 'float', 'unicode', 'list', 'dict', 'html'. The 'list' and 'dict' types have additional fields in their schemas (see below). In addition to these fields, there are also three optional top-level fields:
  * 'validators': a list of validators to apply to the return value, in order. This validation should also be applied automatically in the frontend.
  * 'choices': a list of values of the given type. The value entered must be equal to some element of this list.
  * 'ui\_config': a dict of configuration parameters for the UI. See below for more details on this field.

### Additional fields for lists and dicts ###
For lists, there are two possible additional fields:
  * 'items': required. The schema for an item in the list. Note that polymorphic lists are not allowed at this time.
  * 'len': optional. If present, the length of the list; must be an integer greater than 0. No elements can be added or deleted.

For dicts, there are two possible additional fields:
  * 'properties': required. This is a list whose elements are dicts. The list specifies the order in which the fields for the dict are displayed in the editor view. Each dict has two mandatory keys:
    * 'name': the name of the field
    * 'schema': the schema for the value corresponding to this field.
  * 'description': optional. If present, this gives a human-readable description of the field.

### UI configuration ###
The 'ui\_config' field in a schema is a dict of keys and values. All the keys are optional. The allowed keys, and the circumstances in which they are allowed, are as follows:
  * 'rows': only allowed for type 'unicode'; if specified, must be a positive integer. If this value is omitted, the unicode field is displayed as a regular text `<input>` field. Otherwise, it is displayed as a textarea with the given number of rows.
  * 'placeholder': only allowed for type 'unicode'; if specified, must be a string. It represents the placeholder for the input field.
  * 'coding\_mode': only allowed for type 'unicode'; if specified, must be either 'none' or 'python'. If this value is specified, a CodeMirror instance with the appropriate syntax highlighting is used as the input area, and the 'rows' and 'placeholder' properties above are ignored.
  * 'add\_element\_text': only allowed for type 'list'; if specified, must be a unicode string. If this value is omitted, no changes are made to the 'Add element' button; otherwise, the default 'Add element' text is replaced with the given value.
  * 'hide\_complex\_extensions': only allowed for type 'html'; if specified, must be a boolean. If true, omits the 'collapsible' and 'tabs' rich-text extensions from the toolbar menu.

Additional possible UI configuration options (TODO):
  * Are expressions permitted?
  * Inline/block view?