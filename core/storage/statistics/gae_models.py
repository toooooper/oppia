# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Models for Oppia statistics."""

__author__ = 'Sean Lip'

import datetime
import logging

from core.platform import models
(base_models,) = models.Registry.import_models([models.NAMES.base_model])
import feconf
import utils

from google.appengine.ext import ndb

MAX_ANSWER_HASH_LEN = 100


def hash_answer(answer):
    return utils.convert_to_hash(answer, MAX_ANSWER_HASH_LEN)


class StateCounterModel(base_models.BaseModel):
    """A set of counts that correspond to a state.

    The id/key of instances of this class has the form
        [EXPLORATION_ID].[STATE_NAME].
    """
    # Number of times the state was entered for the first time in a reader
    # session.
    first_entry_count = ndb.IntegerProperty(default=0, indexed=False)
    # Number of times the state was entered for the second time or later in a
    # reader session.
    subsequent_entries_count = ndb.IntegerProperty(default=0, indexed=False)
    # Number of times an answer submitted for this state was subsequently
    # resolved by an exploration admin and removed from the answer logs.
    resolved_answer_count = ndb.IntegerProperty(default=0, indexed=False)
    # Number of times an answer was entered for this state and was not
    # subsequently resolved by an exploration admin.
    active_answer_count = ndb.IntegerProperty(default=0, indexed=False)

    @classmethod
    def get_or_create(cls, exploration_id, state_name):
        instance_id = '.'.join([exploration_id, state_name])
        counter = cls.get(instance_id, strict=False)
        if not counter:
            counter = cls(id=instance_id)
        return counter

    def get_exploration_id_and_state_name(self):
        first_dot_loc = self.id.find('.')
        return self.id[:first_dot_loc], self.id[first_dot_loc + 1:]


class StateRuleAnswerLogModel(base_models.BaseModel):
    """The log of all answers hitting a given state rule.

    The id/key of instances of this class has the form
        [EXPLORATION_ID].[STATE_NAME].[HANDLER_NAME].[RULE_NAME]

    WARNING: If a change is made to existing rules in data/objects (e.g.
    renaming them or changing their signature), this class will contain
    invalid values.

    WARNING: Rule names and args that are used to construct the key here must
    be < 400 characters in length, since these are used as part of the key.
    """
    # Log of answers that hit this rule and that have not been resolved. The
    # JSON blob represents a dict. The keys of this dict are the answers
    # encoded as HTML strings, and the values are integer counts representing
    # how many times the answer has been entered.
    # WARNING: do not use default={} in JsonProperty, it does not work as you
    # expect.
    answers = ndb.JsonProperty(indexed=False)

    @classmethod
    def get_or_create(cls, exploration_id, state_name, handler_name, rule_str):
        # TODO(sll): Deprecate this method.
        return cls.get_or_create_multi(exploration_id, [{
            'state_name': state_name,
            'handler_name': handler_name,
            'rule_str': rule_str
        }])[0]

    @classmethod
    def _get_entity_key(cls, exploration_id, entity_id):
        return ndb.Key(cls._get_kind(), entity_id)

    @classmethod
    def get_or_create_multi(cls, exploration_id, rule_data):
        """Gets or creates entities for the given rules.

        Args:
            exploration_id: the exploration id
            rule_data: a list of dicts, each with the following keys:
                (state_name, handler_name, rule_str).
        """
        # TODO(sll): Use a hash instead to disambiguate.
        entity_ids = ['.'.join([
            exploration_id, datum['state_name'],
            datum['handler_name'], datum['rule_str']
        ])[:490] for datum in rule_data]

        entity_keys = [cls._get_entity_key(exploration_id, entity_id)
                       for entity_id in entity_ids]

        entities = ndb.get_multi(entity_keys)
        entities_to_put = []
        for ind, entity in enumerate(entities):
            if entity is None:
                new_entity = cls(id=entity_ids[ind], answers={})
                entities_to_put.append(new_entity)
                entities[ind] = new_entity

        ndb.put_multi(entities_to_put)
        return entities


class MaybeLeaveExplorationEventLogEntryModel(base_models.BaseModel):
    """An event triggered by a reader attempting to leave the
    exploration without completing.

    Due to complexity on browser end, this event may be logged when user clicks
    close and then cancel. Thus, the real event is the last event of this type
    logged for the session id.

    Note: shortly after the release of v2.0.0.rc.2, some of these events
    were migrated from StateHitEventLogEntryModel. These events have their
    client_time_spent_in_secs field set to 0.0 (since this field was not
    recorded in StateHitEventLogEntryModel), and they also have the wrong
    'last updated' timestamp. However, the 'created_on' timestamp is the
    same as that of the original model.

    Event schema documentation
    --------------------------
    V1:
        event_type: 'leave' (there are no 'maybe leave' events in V0)
        exploration_id: id of exploration currently being played
        exploration_version: version of exploration
        state_name: Name of current state
        play_type: 'normal'
        created_on date
        event_schema_version: 1
        session_id: ID of current student's session
        params: current parameter values, in the form of a map of parameter
            name to value
        client_time_spent_in_secs: time spent in this state before the event
            was triggered
    """
    # This value should be updated in the event of any event schema change.
    CURRENT_EVENT_SCHEMA_VERSION = 1

    # Which specific type of event this is
    event_type = ndb.StringProperty(indexed=True)
    # Id of exploration currently being played.
    exploration_id = ndb.StringProperty(indexed=True)
    # Current version of exploration.
    exploration_version = ndb.IntegerProperty(indexed=True)
    # Name of current state.
    state_name = ndb.StringProperty(indexed=True)
    # ID of current student's session
    session_id = ndb.StringProperty(indexed=True)
    # Time since start of this state before this event occurred (in sec).
    # Note: Some of these events were migrated from StateHit event instances
    # which did not record timestamp data. For this, we use a placeholder
    # value of 0.0 for client_time_spent_in_secs.
    client_time_spent_in_secs = ndb.FloatProperty(indexed=True)
    # Current parameter values, map of parameter name to value
    params = ndb.JsonProperty(indexed=False)
    # Which type of play-through this is (preview, from gallery)
    play_type = ndb.StringProperty(indexed=True,
                                   choices=[feconf.PLAY_TYPE_PLAYTEST,
                                            feconf.PLAY_TYPE_NORMAL])
    # The version of the event schema used to describe an event of this type.
    # Details on the schema are given in the docstring for this class.
    event_schema_version = ndb.IntegerProperty(
        indexed=True, default=CURRENT_EVENT_SCHEMA_VERSION)

    @classmethod
    def get_new_event_entity_id(cls, exp_id, session_id):
        timestamp = datetime.datetime.utcnow()
        return cls.get_new_id('%s:%s:%s' % (
                              utils.get_time_in_millisecs(timestamp),
                              exp_id,
                              session_id))

    @classmethod
    def create(cls, exp_id, exp_version, state_name, session_id,
               client_time_spent_in_secs, params, play_type):
        """Creates a new leave exploration event."""
        # TODO(sll): Some events currently do not have an entity id that was
        # set using this method; it was randomly set instead due to an error.
        # Might need to migrate them.
        entity_id = cls.get_new_event_entity_id(
            exp_id, session_id)
        leave_event_entity = cls(
            id=entity_id,
            event_type=feconf.EVENT_TYPE_MAYBE_LEAVE_EXPLORATION,
            exploration_id=exp_id,
            exploration_version=exp_version,
            state_name=state_name,
            session_id=session_id,
            client_time_spent_in_secs=client_time_spent_in_secs,
            params=params,
            play_type=play_type)
        leave_event_entity.put()


class StartExplorationEventLogEntryModel(base_models.BaseModel):
    """An event triggered by a student starting the exploration.

    Event schema documentation
    --------------------------
    V1:
        event_type: 'start'
        exploration_id: id of exploration currently being played
        exploration_version: version of exploration
        state_name: Name of current state
        client_time_spent_in_secs: 0
        play_type: 'normal'
        created_on date
        event_schema_version: 1
        session_id: ID of current student's session
        params: current parameter values, in the form of a map of parameter
            name to value
    """
    # This value should be updated in the event of any event schema change.
    CURRENT_EVENT_SCHEMA_VERSION = 1

    # Which specific type of event this is
    event_type = ndb.StringProperty(indexed=True)
    # Id of exploration currently being played.
    exploration_id = ndb.StringProperty(indexed=True)
    # Current version of exploration.
    exploration_version = ndb.IntegerProperty(indexed=True)
    # Name of current state.
    state_name = ndb.StringProperty(indexed=True)
    # ID of current student's session
    session_id = ndb.StringProperty(indexed=True)
    # Time since start of this state before this event occurred (in sec).
    client_time_spent_in_secs = ndb.FloatProperty(indexed=True)
    # Current parameter values, map of parameter name to value
    params = ndb.JsonProperty(indexed=False)
    # Which type of play-through this is (preview, from gallery)
    play_type = ndb.StringProperty(indexed=True,
                                   choices=[feconf.PLAY_TYPE_PLAYTEST,
                                            feconf.PLAY_TYPE_NORMAL])
    # The version of the event schema used to describe an event of this type.
    # Details on the schema are given in the docstring for this class.
    event_schema_version = ndb.IntegerProperty(
        indexed=True, default=CURRENT_EVENT_SCHEMA_VERSION)

    @classmethod
    def get_new_event_entity_id(cls, exp_id, session_id):
        timestamp = datetime.datetime.utcnow()
        return cls.get_new_id('%s:%s:%s' % (
                              utils.get_time_in_millisecs(timestamp),
                              exp_id,
                              session_id))

    @classmethod
    def create(cls, exp_id, exp_version, state_name, session_id,
               params, play_type, version=1):
        """Creates a new start exploration event."""
        # TODO(sll): Some events currently do not have an entity id that was
        # set using this method; it was randomly set instead due tg an error.
        # Might need to migrate them.
        entity_id = cls.get_new_event_entity_id(
            exp_id, session_id)
        start_event_entity = cls(
            id=entity_id,
            event_type=feconf.EVENT_TYPE_START_EXPLORATION,
            exploration_id=exp_id,
            exploration_version=exp_version,
            state_name=state_name,
            session_id=session_id,
            client_time_spent_in_secs=0.0,
            params=params,
            play_type=play_type)
        start_event_entity.put()


class StateHitEventLogEntryModel(base_models.BaseModel):
    """An event triggered by a student getting to a particular state. The
    definitions of the fields are as follows:
    - event_type: 'state_hit'
    - exploration_id: id of exploration currently being played
    - exploration_version: version of exploration
    - state_name: Name of current state
    - play_type: 'normal'
    - created_on date
    - event_schema_version: 1
    - session_id: ID of current student's session
    - params: current parameter values, in the form of a map of parameter name
              to its value
    """
    # This value should be updated in the event of any event schema change.
    CURRENT_EVENT_SCHEMA_VERSION = 1

    # Which specific type of event this is
    event_type = ndb.StringProperty(indexed=True)
    # Id of exploration currently being played.
    exploration_id = ndb.StringProperty(indexed=True)
    # Current version of exploration.
    exploration_version = ndb.IntegerProperty(indexed=True)
    # Name of current state.
    state_name = ndb.StringProperty(indexed=True)
    # ID of current student's session
    session_id = ndb.StringProperty(indexed=True)
    # Current parameter values, map of parameter name to value
    params = ndb.JsonProperty(indexed=False)
    # Which type of play-through this is (preview, from gallery)
    play_type = ndb.StringProperty(indexed=True,
                                   choices=[feconf.PLAY_TYPE_PLAYTEST,
                                            feconf.PLAY_TYPE_NORMAL])
    # The version of the event schema used to describe an event of this type.
    # Details on the schema are given in the docstring for this class.
    event_schema_version = ndb.IntegerProperty(
        indexed=True, default=CURRENT_EVENT_SCHEMA_VERSION)

    @classmethod
    def get_new_event_entity_id(cls, exp_id, session_id):
        timestamp = datetime.datetime.utcnow()
        return cls.get_new_id('%s:%s:%s' % (
                              utils.get_time_in_millisecs(timestamp),
                              exp_id,
                              session_id))

    @classmethod
    def create(
            cls, exp_id, exp_version, state_name, session_id, params,
            play_type):
        """Creates a new leave exploration event."""
        # TODO(sll): Some events currently do not have an entity id that was
        # set using this method; it was randomly set instead due to an error.
        # Might need to migrate them.
        entity_id = cls.get_new_event_entity_id(exp_id, session_id)
        state_event_entity = cls(
            id=entity_id,
            event_type=feconf.EVENT_TYPE_STATE_HIT,
            exploration_id=exp_id,
            exploration_version=exp_version,
            state_name=state_name,
            session_id=session_id,
            params=params,
            play_type=play_type)
        state_event_entity.put()


class ExplorationAnnotationsModel(base_models.BaseMapReduceBatchResultsModel):
    """Batch model for storing MapReduce calculation output for
    exploration-level statistics."""
    # Id of exploration.
    exploration_id = ndb.StringProperty(indexed=True)
    # Version of exploration.
    version = ndb.StringProperty(indexed=False)
    # Number of students who started the exploration
    num_starts = ndb.IntegerProperty(indexed=False)
    # Number of students who have completed the exploration
    num_completions = ndb.IntegerProperty(indexed=False)
    # Keyed by state name that describes the numbers of hits for each state
    # {state_name: {'first_entry_count': ...,
    #               'total_entry_count': ...,
    #               'no_answer_count': ...}}
    state_hit_counts = ndb.JsonProperty(indexed=False)

    @classmethod
    def get_entity_id(cls, exploration_id, exploration_version):
        return '%s:%s' % (exploration_id, exploration_version)

    @classmethod
    def create(
        cls, exp_id, version, num_starts, num_completions, state_hit_counts):
        """Creates a new ExplorationAnnotationsModel."""
        entity_id = cls.get_entity_id(exp_id, version)
        cls(
            id=entity_id,
            exploration_id=exp_id,
            version=version,
            num_starts=num_starts,
            num_completions=num_completions,
            state_hit_counts=state_hit_counts).put()

    @classmethod
    def get_versions(cls, exploration_id):
        return [annotations.version for annotations in
            cls.get_all().filter(
                cls.exploration_id == exploration_id).fetch(
                    feconf.DEFAULT_QUERY_LIMIT)]


def process_submitted_answer(
        exploration_id, exploration_version, state_name, handler_name,
        rule, answer):
    """Adds an answer to the answer log for the rule it hits.

    Args:
        exploration_id: the exploration id
        state_name: the state name
        handler_name: a string representing the handler name (e.g., 'submit')
        rule: the rule
        answer: an HTML string representation of the answer
    """
    answer_log = StateRuleAnswerLogModel.get_or_create(
        exploration_id, state_name, handler_name, str(rule))
    if answer in answer_log.answers:
        answer_log.answers[answer] += 1
    else:
        answer_log.answers[answer] = 1

    # This may fail due to answer_log.answers being larger than 1 MB in size.
    try:
        answer_log.put()
    except Exception as e:
        logging.error(e)
        pass


def resolve_answers(
        exploration_id, state_name, handler_name, rule_str, answers):
    """Resolves selected answers for the given rule.

    Args:
        exploration_id: the exploration id
        state_name: the state name
        handler_name: a string representing the handler name (e.g., 'submit')
        rule_str: a string representation of the rule
        answers: a list of HTML string representations of the resolved answers
    """
    assert isinstance(answers, list)
    answer_log = StateRuleAnswerLogModel.get_or_create(
        exploration_id, state_name, handler_name, rule_str)

    for answer in answers:
        if answer not in answer_log.answers:
            logging.error(
                'Answer %s not found in answer log for rule %s of exploration '
                '%s, state %s, handler %s' % (
                    answer, rule_str, exploration_id, state_name,
                    handler_name))
        else:
            del answer_log.answers[answer]
    answer_log.put()
