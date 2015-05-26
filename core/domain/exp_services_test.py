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

__author__ = 'Sean Lip'

import datetime
import os
import StringIO
import zipfile

from core.domain import config_services
from core.domain import event_services
from core.domain import exp_domain
from core.domain import exp_services
from core.domain import fs_domain
from core.domain import param_domain
from core.domain import rating_services
from core.domain import rights_manager
from core.domain import rule_domain
from core.domain import user_services
from core.platform import models
(base_models, exp_models) = models.Registry.import_models([
    models.NAMES.base_model, models.NAMES.exploration
])
search_services = models.Registry.import_search_services()
taskqueue_services = models.Registry.import_taskqueue_services()
transaction_services = models.Registry.import_transaction_services()
from core.tests import test_utils
import feconf
import utils

# TODO(msl): test ExpSummaryModel changes if explorations are updated,
# reverted, deleted, created, rights changed


class ExplorationServicesUnitTests(test_utils.GenericTestBase):
    """Test the exploration services module."""

    EXP_ID = 'An_exploration_id'

    def setUp(self):
        """Before each individual test, create a dummy exploration."""
        super(ExplorationServicesUnitTests, self).setUp()

        self.OWNER_ID = self.get_user_id_from_email(self.OWNER_EMAIL)
        self.EDITOR_ID = self.get_user_id_from_email(self.EDITOR_EMAIL)
        self.VIEWER_ID = self.get_user_id_from_email(self.VIEWER_EMAIL)

        user_services.get_or_create_user(self.OWNER_ID, self.OWNER_EMAIL)
        user_services.get_or_create_user(self.EDITOR_ID, self.EDITOR_EMAIL)
        user_services.get_or_create_user(self.VIEWER_ID, self.VIEWER_EMAIL)

        self.signup(self.OWNER_EMAIL, self.OWNER_USERNAME)
        self.signup(self.EDITOR_EMAIL, self.EDITOR_USERNAME)
        self.signup(self.VIEWER_EMAIL, self.VIEWER_USERNAME)

        self.set_admins([self.ADMIN_EMAIL])
        self.user_id_admin = self.get_user_id_from_email(self.ADMIN_EMAIL)


class ExplorationQueriesUnitTests(ExplorationServicesUnitTests):
    """Tests query methods."""

    def test_count_explorations(self):
        """Test count_explorations()."""

        self.assertEqual(exp_services.count_explorations(), 0)

        self.save_new_default_exploration(self.EXP_ID, self.OWNER_ID)
        self.assertEqual(exp_services.count_explorations(), 1)

        self.save_new_default_exploration(
            'A_new_exploration_id', self.OWNER_ID)
        self.assertEqual(exp_services.count_explorations(), 2)

    def test_get_exploration_titles_and_categories(self):
        self.assertEqual(
            exp_services.get_exploration_titles_and_categories([]), {})

        self.save_new_default_exploration('A', self.OWNER_ID, 'TitleA')
        self.assertEqual(
            exp_services.get_exploration_titles_and_categories(['A']), {
                'A': {
                    'category': 'A category',
                    'title': 'TitleA'
                }
            })

        self.save_new_default_exploration('B', self.OWNER_ID, 'TitleB')
        self.assertEqual(
            exp_services.get_exploration_titles_and_categories(['A']), {
                'A': {
                    'category': 'A category',
                    'title': 'TitleA'
                }
            })
        self.assertEqual(
            exp_services.get_exploration_titles_and_categories(['A', 'B']), {
                'A': {
                    'category': 'A category',
                    'title': 'TitleA',
                },
                'B': {
                    'category': 'A category',
                    'title': 'TitleB',
                },
            })
        self.assertEqual(
            exp_services.get_exploration_titles_and_categories(['A', 'C']), {
                'A': {
                    'category': 'A category',
                    'title': 'TitleA'
                }
            })


class ExplorationCreateAndDeleteUnitTests(ExplorationServicesUnitTests):
    """Test creation and deletion methods."""

    def test_retrieval_of_explorations(self):
        """Test the get_exploration_by_id() method."""
        with self.assertRaisesRegexp(Exception, 'Entity .* not found'):
            exp_services.get_exploration_by_id('fake_eid')

        exploration = self.save_new_default_exploration(
            self.EXP_ID, self.OWNER_ID)
        retrieved_exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        self.assertEqual(exploration.id, retrieved_exploration.id)
        self.assertEqual(exploration.title, retrieved_exploration.title)

        with self.assertRaises(Exception):
            exp_services.get_exploration_by_id('fake_exploration')

    def test_retrieval_of_multiple_explorations(self):
        exps = {}
        chars = 'abcde'
        exp_ids = ['%s%s' % (self.EXP_ID, c) for c in chars]
        for _id in exp_ids:
            exp = self.save_new_valid_exploration(_id, self.OWNER_ID)
            exps[_id] = exp

        result = exp_services.get_multiple_explorations_by_id(
            exp_ids)
        for _id in exp_ids:
            self.assertEqual(result.get(_id).title, exps.get(_id).title)

        # Test retrieval of non-existent ids.
        result = exp_services.get_multiple_explorations_by_id(
            exp_ids + ['doesnt_exist'], strict=False
        )
        for _id in exp_ids:
            self.assertEqual(result.get(_id).title, exps.get(_id).title)

        self.assertNotIn('doesnt_exist', result)

        with self.assertRaises(Exception):
            exp_services.get_multiple_explorations_by_id(
                exp_ids + ['doesnt_exist'])

    def test_soft_deletion_of_explorations(self):
        """Test that soft deletion of explorations works correctly."""
        # TODO(sll): Add tests for deletion of states and version snapshots.

        self.save_new_default_exploration(self.EXP_ID, self.OWNER_ID)
        # The exploration shows up in queries.
        self.assertEqual(
            len(exp_services.get_at_least_editable_exploration_summaries(
                self.OWNER_ID)), 1)

        exp_services.delete_exploration(self.OWNER_ID, self.EXP_ID)
        with self.assertRaises(Exception):
            exp_services.get_exploration_by_id(self.EXP_ID)

        # The deleted exploration does not show up in any queries.
        self.assertEqual(
            exp_services.get_at_least_editable_exploration_summaries(
                self.OWNER_ID),
            {})

        # But the models still exist in the backend.
        self.assertIn(
            self.EXP_ID,
            [exp.id for exp in exp_models.ExplorationModel.get_all(
                include_deleted_entities=True)]
        )

        # The exploration summary is deleted however
        self.assertNotIn(
            self.EXP_ID,
            [exp.id for exp in exp_models.ExpSummaryModel.get_all(
                include_deleted_entities=True)]
        )

    def test_hard_deletion_of_explorations(self):
        """Test that hard deletion of explorations works correctly."""
        self.save_new_default_exploration(self.EXP_ID, self.OWNER_ID)
        # The exploration shows up in queries.
        self.assertEqual(
            len(exp_services.get_at_least_editable_exploration_summaries(
                self.OWNER_ID)), 1)

        exp_services.delete_exploration(
            self.OWNER_ID, self.EXP_ID, force_deletion=True)
        with self.assertRaises(Exception):
            exp_services.get_exploration_by_id(self.EXP_ID)

        # The deleted exploration does not show up in any queries.
        self.assertEqual(
            exp_services.get_at_least_editable_exploration_summaries(
                self.OWNER_ID),
            {})

        # The exploration model has been purged from the backend.
        self.assertNotIn(
            self.EXP_ID,
            [exp.id for exp in exp_models.ExplorationModel.get_all(
                include_deleted_entities=True)]
        )

    def test_summaries_of_hard_deleted_explorations(self):
        """Test that summaries of hard deleted explorations are
        correctly deleted."""
        self.save_new_default_exploration(self.EXP_ID, self.OWNER_ID)

        exp_services.delete_exploration(
            self.OWNER_ID, self.EXP_ID, force_deletion=True)
        with self.assertRaises(Exception):
            exp_services.get_exploration_by_id(self.EXP_ID)

        # The deleted exploration summary does not show up in any queries.
        self.assertEqual(
            exp_services.get_at_least_editable_exploration_summaries(
                self.OWNER_ID), {})

        # The exploration summary model has been purged from the backend.
        self.assertNotIn(
            self.EXP_ID,
            [exp.id for exp in exp_models.ExpSummaryModel.get_all(
                include_deleted_entities=True)]
        )

    def test_explorations_are_removed_from_index_when_deleted(self):
        """Tests that explorations are removed from the search index when
        deleted.
        """

        self.save_new_default_exploration(self.EXP_ID, self.OWNER_ID)

        def mock_delete_docs(doc_ids, index):
            self.assertEqual(index, exp_services.SEARCH_INDEX_EXPLORATIONS)
            self.assertEqual(doc_ids, [self.EXP_ID])

        delete_docs_swap = self.swap(
            search_services, 'delete_documents_from_index', mock_delete_docs)

        with delete_docs_swap:
            exp_services.delete_exploration(self.OWNER_ID, self.EXP_ID)

    def test_create_new_exploration_error_cases(self):
        exploration = exp_domain.Exploration.create_default_exploration(
            self.EXP_ID, '', '')
        with self.assertRaisesRegexp(Exception, 'between 1 and 50 characters'):
            exp_services.save_new_exploration(self.OWNER_ID, exploration)

        exploration = exp_domain.Exploration.create_default_exploration(
            self.EXP_ID, 'title', '')
        with self.assertRaisesRegexp(Exception, 'between 1 and 50 characters'):
            exp_services.save_new_exploration(self.OWNER_ID, exploration)

    def test_save_and_retrieve_exploration(self):
        exploration = self.save_new_valid_exploration(
            self.EXP_ID, self.OWNER_ID)
        exploration.param_specs = {
            'theParameter': param_domain.ParamSpec('Int')}
        exp_services._save_exploration(self.OWNER_ID, exploration, '', [])

        retrieved_exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        self.assertEqual(retrieved_exploration.title, 'A title')
        self.assertEqual(retrieved_exploration.category, 'A category')
        self.assertEqual(len(retrieved_exploration.states), 1)
        self.assertEqual(len(retrieved_exploration.param_specs), 1)
        self.assertEqual(
            retrieved_exploration.param_specs.keys()[0], 'theParameter')

    def test_save_and_retrieve_exploration_summary(self):
        exploration = self.save_new_valid_exploration(
            self.EXP_ID, self.OWNER_ID)
        exploration.param_specs = {
            'theParameter': param_domain.ParamSpec('Int')}
        exp_services._save_exploration(self.OWNER_ID, exploration, '', [])

        # change title and category
        exp_services.update_exploration(
            self.OWNER_ID, self.EXP_ID, [{
                'cmd': 'edit_exploration_property',
                'property_name': 'title',
                'new_value': 'A new title'
            }, {
                'cmd': 'edit_exploration_property',
                'property_name': 'category',
                'new_value': 'A new category'
            }],
            'Change title and category')

        retrieved_exp_summary = exp_services.get_exploration_summary_by_id(
            self.EXP_ID)

        self.assertEqual(retrieved_exp_summary.title, 'A new title')
        self.assertEqual(retrieved_exp_summary.category, 'A new category')


class LoadingAndDeletionOfDemosTest(ExplorationServicesUnitTests):

    def test_loading_and_validation_and_deletion_of_demo_explorations(self):
        """Test loading, validation and deletion of the demo explorations."""
        self.assertEqual(exp_services.count_explorations(), 0)

        self.assertGreaterEqual(
            len(feconf.DEMO_EXPLORATIONS), 1,
            msg='There must be at least one demo exploration.')

        for ind in range(len(feconf.DEMO_EXPLORATIONS)):
            start_time = datetime.datetime.utcnow()

            exp_id = str(ind)
            exp_services.load_demo(exp_id)
            exploration = exp_services.get_exploration_by_id(exp_id)
            warnings = exploration.validate(strict=True)
            if warnings:
                raise Exception(warnings)

            duration = datetime.datetime.utcnow() - start_time
            processing_time = duration.seconds + duration.microseconds / 1E6
            self.log_line(
                'Loaded and validated exploration %s (%.2f seconds)' % (
                exploration.title.encode('utf-8'), processing_time))

        self.assertEqual(
            exp_services.count_explorations(), len(feconf.DEMO_EXPLORATIONS))

        for ind in range(len(feconf.DEMO_EXPLORATIONS)):
            exp_services.delete_demo(str(ind))
        self.assertEqual(exp_services.count_explorations(), 0)


class ZipFileExportUnitTests(ExplorationServicesUnitTests):
    """Test export methods for explorations represented as zip files."""

    SAMPLE_YAML_CONTENT = (
"""author_notes: ''
blurb: ''
default_skin: conversation_v1
init_state_name: %s
language_code: en
objective: The objective
param_changes: []
param_specs: {}
schema_version: 5
skin_customizations:
  panels_contents: {}
states:
  %s:
    content:
    - type: text
      value: ''
    interaction:
      customization_args:
        placeholder:
          value: ''
        rows:
          value: 1
      handlers:
      - name: submit
        rule_specs:
        - definition:
            rule_type: default
          dest: %s
          feedback: []
          param_changes: []
      id: TextInput
    param_changes: []
  New state:
    content:
    - type: text
      value: ''
    interaction:
      customization_args:
        placeholder:
          value: ''
        rows:
          value: 1
      handlers:
      - name: submit
        rule_specs:
        - definition:
            rule_type: default
          dest: New state
          feedback: []
          param_changes: []
      id: TextInput
    param_changes: []
tags: []
""" % (
    feconf.DEFAULT_INIT_STATE_NAME, feconf.DEFAULT_INIT_STATE_NAME,
    feconf.DEFAULT_INIT_STATE_NAME))

    UPDATED_YAML_CONTENT = (
"""author_notes: ''
blurb: ''
default_skin: conversation_v1
init_state_name: %s
language_code: en
objective: The objective
param_changes: []
param_specs: {}
schema_version: 5
skin_customizations:
  panels_contents: {}
states:
  %s:
    content:
    - type: text
      value: ''
    interaction:
      customization_args:
        placeholder:
          value: ''
        rows:
          value: 1
      handlers:
      - name: submit
        rule_specs:
        - definition:
            rule_type: default
          dest: %s
          feedback: []
          param_changes: []
      id: TextInput
    param_changes: []
  Renamed state:
    content:
    - type: text
      value: ''
    interaction:
      customization_args:
        placeholder:
          value: ''
        rows:
          value: 1
      handlers:
      - name: submit
        rule_specs:
        - definition:
            rule_type: default
          dest: Renamed state
          feedback: []
          param_changes: []
      id: TextInput
    param_changes: []
tags: []
""" % (
    feconf.DEFAULT_INIT_STATE_NAME, feconf.DEFAULT_INIT_STATE_NAME,
    feconf.DEFAULT_INIT_STATE_NAME))

    def test_export_to_zip_file(self):
        """Test the export_to_zip_file() method."""
        exploration = self.save_new_valid_exploration(
            self.EXP_ID, self.OWNER_ID, objective='The objective')
        exploration.states[exploration.init_state_name].interaction.handlers[
            0].rule_specs[0].dest = exploration.init_state_name
        exploration.add_states(['New state'])
        exploration.states['New state'].update_interaction_id('TextInput')
        exp_services._save_exploration(self.OWNER_ID, exploration, '', [])

        zip_file_output = exp_services.export_to_zip_file(self.EXP_ID)
        zf = zipfile.ZipFile(StringIO.StringIO(zip_file_output))

        self.assertEqual(zf.namelist(), ['A title.yaml'])
        self.assertEqual(
            zf.open('A title.yaml').read(), self.SAMPLE_YAML_CONTENT)

    def test_export_to_zip_file_with_assets(self):
        """Test exporting an exploration with assets to a zip file."""
        exploration = self.save_new_valid_exploration(
            self.EXP_ID, self.OWNER_ID, objective='The objective')
        exploration.states[exploration.init_state_name].interaction.handlers[
            0].rule_specs[0].dest = exploration.init_state_name
        exploration.add_states(['New state'])
        exploration.states['New state'].update_interaction_id('TextInput')
        exp_services._save_exploration(self.OWNER_ID, exploration, '', [])

        with open(os.path.join(feconf.TESTS_DATA_DIR, 'img.png')) as f:
            raw_image = f.read()
        fs = fs_domain.AbstractFileSystem(
            fs_domain.ExplorationFileSystem(self.EXP_ID))
        fs.commit(self.OWNER_ID, 'abc.png', raw_image)

        zip_file_output = exp_services.export_to_zip_file(self.EXP_ID)
        zf = zipfile.ZipFile(StringIO.StringIO(zip_file_output))

        self.assertEqual(zf.namelist(), ['A title.yaml', 'assets/abc.png'])
        self.assertEqual(
            zf.open('A title.yaml').read(), self.SAMPLE_YAML_CONTENT)
        self.assertEqual(zf.open('assets/abc.png').read(), raw_image)

    def test_export_by_versions(self):
        """Test export_to_zip_file() for different versions."""
        exploration = self.save_new_valid_exploration(
            self.EXP_ID, self.OWNER_ID, objective='The objective')
        self.assertEqual(exploration.version, 1)

        exploration.states[exploration.init_state_name].interaction.handlers[
            0].rule_specs[0].dest = exploration.init_state_name
        exploration.add_states(['New state'])
        exploration.states['New state'].update_interaction_id('TextInput')
        with open(os.path.join(feconf.TESTS_DATA_DIR, 'img.png')) as f:
            raw_image = f.read()
        fs = fs_domain.AbstractFileSystem(
            fs_domain.ExplorationFileSystem(self.EXP_ID))
        fs.commit(self.OWNER_ID, 'abc.png', raw_image)
        exp_services._save_exploration(self.OWNER_ID, exploration, '', [])
        self.assertEqual(exploration.version, 2)

        exploration.rename_state('New state', 'Renamed state')
        exp_services._save_exploration(self.OWNER_ID, exploration, '', [])
        self.assertEqual(exploration.version, 3)

        # Download version 2
        zip_file_output = exp_services.export_to_zip_file(self.EXP_ID, 2)
        zf = zipfile.ZipFile(StringIO.StringIO(zip_file_output))
        self.assertEqual(
            zf.open('A title.yaml').read(), self.SAMPLE_YAML_CONTENT)

        # Download version 3
        zip_file_output = exp_services.export_to_zip_file(self.EXP_ID, 3)
        zf = zipfile.ZipFile(StringIO.StringIO(zip_file_output))
        self.assertEqual(
            zf.open('A title.yaml').read(), self.UPDATED_YAML_CONTENT)


class YAMLExportUnitTests(ExplorationServicesUnitTests):
    """Test export methods for explorations represented as a dict whose keys
    are state names and whose values are YAML strings representing the state's
    contents."""

    _SAMPLE_INIT_STATE_CONTENT = ("""content:
- type: text
  value: ''
interaction:
  customization_args:
    placeholder:
      value: ''
    rows:
      value: 1
  handlers:
  - name: submit
    rule_specs:
    - definition:
        rule_type: default
      dest: %s
      feedback: []
      param_changes: []
  id: TextInput
param_changes: []
""") % (feconf.DEFAULT_INIT_STATE_NAME)

    SAMPLE_EXPORTED_DICT = {
        feconf.DEFAULT_INIT_STATE_NAME: _SAMPLE_INIT_STATE_CONTENT,
        'New state': ("""content:
- type: text
  value: ''
interaction:
  customization_args:
    placeholder:
      value: ''
    rows:
      value: 1
  handlers:
  - name: submit
    rule_specs:
    - definition:
        rule_type: default
      dest: New state
      feedback: []
      param_changes: []
  id: TextInput
param_changes: []
""")
    }

    UPDATED_SAMPLE_DICT = {
        feconf.DEFAULT_INIT_STATE_NAME: _SAMPLE_INIT_STATE_CONTENT,
        'Renamed state': ("""content:
- type: text
  value: ''
interaction:
  customization_args:
    placeholder:
      value: ''
    rows:
      value: 1
  handlers:
  - name: submit
    rule_specs:
    - definition:
        rule_type: default
      dest: Renamed state
      feedback: []
      param_changes: []
  id: TextInput
param_changes: []
""")
    }

    def test_export_to_dict(self):
        """Test the export_to_dict() method."""
        exploration = self.save_new_valid_exploration(
            self.EXP_ID, self.OWNER_ID, objective='The objective')
        exploration.states[exploration.init_state_name].interaction.handlers[
            0].rule_specs[0].dest = exploration.init_state_name
        exploration.add_states(['New state'])
        exploration.states['New state'].update_interaction_id('TextInput')
        exp_services._save_exploration(self.OWNER_ID, exploration, '', [])

        dict_output = exp_services.export_states_to_yaml(self.EXP_ID, width=50)

        self.assertEqual(dict_output, self.SAMPLE_EXPORTED_DICT)

    def test_export_by_versions(self):
        """Test export_to_dict() for different versions."""
        exploration = self.save_new_valid_exploration(
            self.EXP_ID, self.OWNER_ID)
        self.assertEqual(exploration.version, 1)

        exploration.states[exploration.init_state_name].interaction.handlers[
            0].rule_specs[0].dest = exploration.init_state_name
        exploration.add_states(['New state'])
        exploration.states['New state'].update_interaction_id('TextInput')
        exploration.objective = 'The objective'
        with open(os.path.join(feconf.TESTS_DATA_DIR, 'img.png')) as f:
            raw_image = f.read()
        fs = fs_domain.AbstractFileSystem(
            fs_domain.ExplorationFileSystem(self.EXP_ID))
        fs.commit(self.OWNER_ID, 'abc.png', raw_image)
        exp_services._save_exploration(self.OWNER_ID, exploration, '', [])
        self.assertEqual(exploration.version, 2)

        exploration.rename_state('New state', 'Renamed state')
        exp_services._save_exploration(self.OWNER_ID, exploration, '', [])
        self.assertEqual(exploration.version, 3)

        # Download version 2
        dict_output = exp_services.export_states_to_yaml(
            self.EXP_ID, version=2, width=50)
        self.assertEqual(dict_output, self.SAMPLE_EXPORTED_DICT)

        # Download version 3
        dict_output = exp_services.export_states_to_yaml(
            self.EXP_ID, version=3, width=50)
        self.assertEqual(dict_output, self.UPDATED_SAMPLE_DICT)


def _get_change_list(state_name, property_name, new_value):
    """Generates a change list for a single state change."""
    return [{
        'cmd': 'edit_state_property',
        'state_name': state_name,
        'property_name': property_name,
        'new_value': new_value
    }]


class UpdateStateTests(ExplorationServicesUnitTests):
    """Test updating a single state."""

    def setUp(self):
        super(UpdateStateTests, self).setUp()
        exploration = self.save_new_valid_exploration(
            self.EXP_ID, self.OWNER_ID)

        self.init_state_name = exploration.init_state_name

        self.param_changes = [{
            'customization_args': {
                'list_of_values': ['1', '2'], 'parse_with_jinja': False
            },
            'name': 'myParam',
            'generator_id': 'RandomSelector',
            '$$hashKey': '018'
        }]

        self.interaction_handlers = {
            'submit': [{
                'description': 'is equal to {{x|NonnegativeInt}}',
                'definition': {
                    'rule_type': 'atomic',
                    'name': 'Equals',
                    'inputs': {'x': 0},
                    'subject': 'answer'
                },
                'dest': self.init_state_name,
                'feedback': ['Try again'],
                '$$hashKey': '03L'
            }, {
                'description': feconf.DEFAULT_RULE_NAME,
                'definition': {
                    'rule_type': rule_domain.DEFAULT_RULE_TYPE
                },
                'dest': self.init_state_name,
                'feedback': ['Incorrect', '<b>Wrong answer</b>'],
                '$$hashKey': '059'
            }]}

    def test_update_state_name(self):
        """Test updating of state name."""
        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        exp_services.update_exploration(self.OWNER_ID, self.EXP_ID, [{
            'cmd': 'rename_state',
            'old_state_name': feconf.DEFAULT_INIT_STATE_NAME,
            'new_state_name': 'new name',
        }], 'Change state name')

        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        self.assertIn('new name', exploration.states)
        self.assertNotIn(feconf.DEFAULT_INIT_STATE_NAME, exploration.states)

    def test_update_state_name_with_unicode(self):
        """Test updating of state name to one that uses unicode characters."""
        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        exp_services.update_exploration(self.OWNER_ID, self.EXP_ID, [{
            'cmd': 'rename_state',
            'old_state_name': feconf.DEFAULT_INIT_STATE_NAME,
            'new_state_name': u'¡Hola! αβγ',
        }], 'Change state name')

        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        self.assertIn(u'¡Hola! αβγ', exploration.states)
        self.assertNotIn(feconf.DEFAULT_INIT_STATE_NAME, exploration.states)

    def test_update_param_changes(self):
        """Test updating of param_changes."""
        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        exploration.param_specs = {'myParam': param_domain.ParamSpec('Int')}
        exp_services._save_exploration(self.OWNER_ID, exploration, '', [])
        exp_services.update_exploration(
            self.OWNER_ID, self.EXP_ID, _get_change_list(
                self.init_state_name, 'param_changes', self.param_changes), '')

        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        param_changes = exploration.init_state.param_changes[0]
        self.assertEqual(param_changes._name, 'myParam')
        self.assertEqual(param_changes._generator_id, 'RandomSelector')
        self.assertEqual(
            param_changes._customization_args,
            {'list_of_values': ['1', '2'], 'parse_with_jinja': False})

    def test_update_invalid_param_changes(self):
        """Check that updates cannot be made to non-existent parameters."""
        with self.assertRaisesRegexp(
                utils.ValidationError,
                r'The parameter with name \'myParam\' .* does not exist .*'):
            exp_services.update_exploration(
                self.OWNER_ID, self.EXP_ID, _get_change_list(
                    self.init_state_name, 'param_changes', self.param_changes),
                '')

    def test_update_invalid_generator(self):
        """Test for check that the generator_id in param_changes exists."""
        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        exploration.param_specs = {'myParam': param_domain.ParamSpec('Int')}
        exp_services._save_exploration(self.OWNER_ID, exploration, '', [])

        self.param_changes[0]['generator_id'] = 'fake'
        with self.assertRaisesRegexp(
                utils.ValidationError, 'Invalid generator id fake'):
            exp_services.update_exploration(
                self.OWNER_ID, self.EXP_ID,
                _get_change_list(
                    self.init_state_name, 'param_changes', self.param_changes),
                '')

    def test_update_interaction_id(self):
        """Test updating of interaction_id."""
        exp_services.update_exploration(
            self.OWNER_ID, self.EXP_ID, _get_change_list(
                self.init_state_name, exp_domain.STATE_PROPERTY_INTERACTION_ID,
                'MultipleChoiceInput'), '')

        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        self.assertEqual(
            exploration.init_state.interaction.id, 'MultipleChoiceInput')

    def test_update_interaction_customization_args(self):
        """Test updating of interaction customization_args."""
        exp_services.update_exploration(
            self.OWNER_ID, self.EXP_ID,
            _get_change_list(
                self.init_state_name, exp_domain.STATE_PROPERTY_INTERACTION_ID,
                'MultipleChoiceInput') +
            _get_change_list(
                self.init_state_name,
                exp_domain.STATE_PROPERTY_INTERACTION_CUST_ARGS,
                {'choices': {'value': ['Option A', 'Option B']}}),
            '')

        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        self.assertEqual(
            exploration.init_state.interaction.customization_args[
                'choices']['value'], ['Option A', 'Option B'])

    def test_update_interaction_handlers(self):
        """Test updating of interaction_handlers."""

        # We create a second state to use as a rule destination
        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        exploration.add_states(['State 2'])
        exploration.states['State 2'].update_interaction_id('TextInput')
        exp_services._save_exploration(self.OWNER_ID, exploration, '', [])

        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        self.interaction_handlers['submit'][1]['dest'] = 'State 2'
        exp_services.update_exploration(
            self.OWNER_ID, self.EXP_ID,
            _get_change_list(
                self.init_state_name, exp_domain.STATE_PROPERTY_INTERACTION_ID,
                'MultipleChoiceInput') +
            _get_change_list(
                self.init_state_name,
                exp_domain.STATE_PROPERTY_INTERACTION_HANDLERS,
                self.interaction_handlers),
            '')

        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        rule_specs = exploration.init_state.interaction.handlers[0].rule_specs
        self.assertEqual(rule_specs[0].definition, {
            'rule_type': 'atomic',
            'name': 'Equals',
            'inputs': {'x': 0},
            'subject': 'answer'
        })
        self.assertEqual(rule_specs[0].feedback, ['Try again'])
        self.assertEqual(rule_specs[0].dest, self.init_state_name)
        self.assertEqual(rule_specs[1].dest, 'State 2')

    def test_update_state_invalid_state(self):
        """Test that rule destination states cannot be non-existant."""
        self.interaction_handlers['submit'][0]['dest'] = 'INVALID'
        with self.assertRaisesRegexp(
                utils.ValidationError,
                'The destination INVALID is not a valid state'):
            exp_services.update_exploration(
                self.OWNER_ID, self.EXP_ID,
                _get_change_list(
                    self.init_state_name,
                    exp_domain.STATE_PROPERTY_INTERACTION_ID,
                    'MultipleChoiceInput') +
                _get_change_list(
                    self.init_state_name,
                    exp_domain.STATE_PROPERTY_INTERACTION_HANDLERS,
                    self.interaction_handlers),
                '')

    def test_update_state_missing_keys(self):
        """Test that missing keys in interaction_handlers produce an error."""
        del self.interaction_handlers['submit'][0]['definition']['inputs']
        with self.assertRaisesRegexp(KeyError, 'inputs'):
            exp_services.update_exploration(
                self.OWNER_ID, self.EXP_ID,
                _get_change_list(
                    self.init_state_name,
                    exp_domain.STATE_PROPERTY_INTERACTION_ID, 'NumericInput') +
                _get_change_list(
                    self.init_state_name,
                    exp_domain.STATE_PROPERTY_INTERACTION_HANDLERS,
                    self.interaction_handlers),
                '')

    def test_update_state_extra_keys(self):
        """Test that extra keys in rule definitions are detected."""
        self.interaction_handlers['submit'][0]['definition']['extra'] = 3
        with self.assertRaisesRegexp(
                utils.ValidationError, 'should conform to schema'):
            exp_services.update_exploration(
                self.OWNER_ID, self.EXP_ID,
                _get_change_list(
                    self.init_state_name,
                    exp_domain.STATE_PROPERTY_INTERACTION_ID,
                    'MultipleChoiceInput') +
                _get_change_list(
                    self.init_state_name,
                    exp_domain.STATE_PROPERTY_INTERACTION_HANDLERS,
                    self.interaction_handlers),
                '')

    def test_update_state_extra_default_rule(self):
        """Test that rules other than the last cannot be default."""
        self.interaction_handlers['submit'][0]['definition']['rule_type'] = (
            rule_domain.DEFAULT_RULE_TYPE)
        with self.assertRaisesRegexp(
                ValueError,
                'Invalid ruleset .*: rules other than the last one should '
                'not be default rules.'):
            exp_services.update_exploration(
                self.OWNER_ID, self.EXP_ID,
                _get_change_list(
                    self.init_state_name,
                    exp_domain.STATE_PROPERTY_INTERACTION_ID,
                    'MultipleChoiceInput') +
                _get_change_list(
                    self.init_state_name,
                    exp_domain.STATE_PROPERTY_INTERACTION_HANDLERS,
                    self.interaction_handlers),
                '')

    def test_update_state_missing_default_rule(self):
        """Test that the last rule must be default."""
        self.interaction_handlers['submit'][1]['definition']['rule_type'] = (
            'atomic')
        with self.assertRaisesRegexp(
                ValueError,
                'Invalid ruleset .* the last rule should be a default rule'):
            exp_services.update_exploration(
                self.OWNER_ID, self.EXP_ID,
                _get_change_list(
                    self.init_state_name,
                    exp_domain.STATE_PROPERTY_INTERACTION_ID,
                    'MultipleChoiceInput') +
                _get_change_list(
                    self.init_state_name,
                    exp_domain.STATE_PROPERTY_INTERACTION_HANDLERS,
                    self.interaction_handlers),
                '')

    def test_update_state_variable_types(self):
        """Test that parameters in rules must have the correct type."""
        self.interaction_handlers['submit'][0]['definition']['inputs']['x'] = (
            'abc')
        with self.assertRaisesRegexp(Exception, 'invalid literal for int()'):
            exp_services.update_exploration(
                self.OWNER_ID, self.EXP_ID,
                _get_change_list(
                    self.init_state_name,
                    exp_domain.STATE_PROPERTY_INTERACTION_ID,
                    'MultipleChoiceInput') +
                _get_change_list(
                    self.init_state_name,
                    exp_domain.STATE_PROPERTY_INTERACTION_HANDLERS,
                    self.interaction_handlers),
                '')

    def test_update_content(self):
        """Test updating of content."""
        exp_services.update_exploration(
            self.OWNER_ID, self.EXP_ID, _get_change_list(
                self.init_state_name, 'content', [{
                    'type': 'text',
                    'value': '<b>Test content</b>',
                    '$$hashKey': '014'
                }]),
            '')

        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        self.assertEqual(exploration.init_state.content[0].type, 'text')
        self.assertEqual(
            exploration.init_state.content[0].value, '<b>Test content</b>')

    def test_update_content_missing_key(self):
        """Test that missing keys in content yield an error."""
        with self.assertRaisesRegexp(KeyError, 'type'):
            exp_services.update_exploration(
                self.OWNER_ID, self.EXP_ID, _get_change_list(
                    self.init_state_name, 'content', [{
                        'value': '<b>Test content</b>',
                        '$$hashKey': '014'
                    }]),
                '')


class CommitMessageHandlingTests(ExplorationServicesUnitTests):
    """Test the handling of commit messages."""

    def setUp(self):
        super(CommitMessageHandlingTests, self).setUp()
        exploration = self.save_new_valid_exploration(
            self.EXP_ID, self.OWNER_ID, end_state_name='End')
        self.init_state_name = exploration.init_state_name

    def test_record_commit_message(self):
        """Check published explorations record commit messages."""
        rights_manager.publish_exploration(self.OWNER_ID, self.EXP_ID)

        exp_services.update_exploration(
            self.OWNER_ID, self.EXP_ID, _get_change_list(
                self.init_state_name,
                exp_domain.STATE_PROPERTY_INTERACTION_STICKY,
                False), 'A message')

        self.assertEqual(
            exp_services.get_exploration_snapshots_metadata(
                self.EXP_ID)[-1]['commit_message'],
            'A message')

    def test_demand_commit_message(self):
        """Check published explorations demand commit messages"""
        rights_manager.publish_exploration(self.OWNER_ID, self.EXP_ID)

        with self.assertRaisesRegexp(
                ValueError, 'Exploration is public so expected a commit '
                            'message but received none.'):
            exp_services.update_exploration(
                self.OWNER_ID, self.EXP_ID, _get_change_list(
                    self.init_state_name,
                    exp_domain.STATE_PROPERTY_INTERACTION_STICKY, False), '')

    def test_unpublished_explorations_can_accept_commit_message(self):
        """Test unpublished explorations can accept optional commit messages"""

        exp_services.update_exploration(
            self.OWNER_ID, self.EXP_ID, _get_change_list(
                self.init_state_name,
                exp_domain.STATE_PROPERTY_INTERACTION_STICKY, False
            ), 'A message')

        exp_services.update_exploration(
            self.OWNER_ID, self.EXP_ID, _get_change_list(
                self.init_state_name,
                exp_domain.STATE_PROPERTY_INTERACTION_STICKY, True
            ), '')

        exp_services.update_exploration(
            self.OWNER_ID, self.EXP_ID, _get_change_list(
                self.init_state_name,
                exp_domain.STATE_PROPERTY_INTERACTION_STICKY, True
            ), None)


class ExplorationSnapshotUnitTests(ExplorationServicesUnitTests):
    """Test methods relating to exploration snapshots."""

    def test_get_exploration_snapshots_metadata(self):
        v1_exploration = self.save_new_valid_exploration(
            self.EXP_ID, self.OWNER_ID, end_state_name='End')

        snapshots_metadata = exp_services.get_exploration_snapshots_metadata(
            self.EXP_ID)
        self.assertEqual(len(snapshots_metadata), 1)
        self.assertDictContainsSubset({
            'commit_cmds': [{
                'cmd': 'create_new',
                'title': 'A title',
                'category': 'A category',
            }],
            'committer_id': self.OWNER_ID,
            'commit_message': (
                'New exploration created with title \'A title\'.'),
            'commit_type': 'create',
            'version_number': 1
        }, snapshots_metadata[0])
        self.assertIn('created_on', snapshots_metadata[0])

        # Publish the exploration. This does not affect the exploration version
        # history.
        rights_manager.publish_exploration(self.OWNER_ID, self.EXP_ID)

        snapshots_metadata = exp_services.get_exploration_snapshots_metadata(
            self.EXP_ID)
        self.assertEqual(len(snapshots_metadata), 1)
        self.assertDictContainsSubset({
            'commit_cmds': [{
                'cmd': 'create_new',
                'title': 'A title',
                'category': 'A category'
            }],
            'committer_id': self.OWNER_ID,
            'commit_message': (
                'New exploration created with title \'A title\'.'),
            'commit_type': 'create',
            'version_number': 1
        }, snapshots_metadata[0])
        self.assertIn('created_on', snapshots_metadata[0])

        # Modify the exploration. This affects the exploration version history.
        change_list = [{
            'cmd': 'edit_exploration_property',
            'property_name': 'title',
            'new_value': 'First title'
        }]
        exp_services.update_exploration(
            self.OWNER_ID, self.EXP_ID, change_list, 'Changed title.')

        snapshots_metadata = exp_services.get_exploration_snapshots_metadata(
            self.EXP_ID)
        self.assertEqual(len(snapshots_metadata), 2)
        self.assertIn('created_on', snapshots_metadata[0])
        self.assertDictContainsSubset({
            'commit_cmds': change_list,
            'committer_id': self.OWNER_ID,
            'commit_message': 'Changed title.',
            'commit_type': 'edit',
            'version_number': 2,
        }, snapshots_metadata[-1])
        self.assertDictContainsSubset({
            'commit_cmds': [{
                'cmd': 'create_new',
                'title': 'A title',
                'category': 'A category'
            }],
            'committer_id': self.OWNER_ID,
            'commit_message': (
                'New exploration created with title \'A title\'.'),
            'commit_type': 'create',
            'version_number': 1
        }, snapshots_metadata[-2])
        self.assertGreaterEqual(
            snapshots_metadata[-1]['created_on'],
            snapshots_metadata[-2]['created_on'])

        # Using the old version of the exploration should raise an error.
        with self.assertRaisesRegexp(Exception, 'version 1, which is too old'):
            exp_services._save_exploration(
                'committer_id_2', v1_exploration, '', [])

        # Another person modifies the exploration.
        new_change_list = [{
            'cmd': 'edit_exploration_property',
            'property_name': 'title',
            'new_value': 'New title'
        }]
        exp_services.update_exploration(
            'committer_id_2', self.EXP_ID, new_change_list, 'Second commit.')

        snapshots_metadata = exp_services.get_exploration_snapshots_metadata(
            self.EXP_ID)
        self.assertEqual(len(snapshots_metadata), 3)
        self.assertDictContainsSubset({
            'commit_cmds': new_change_list,
            'committer_id': 'committer_id_2',
            'commit_message': 'Second commit.',
            'commit_type': 'edit',
            'version_number': 3,
        }, snapshots_metadata[-1])
        self.assertDictContainsSubset({
            'commit_cmds': change_list,
            'committer_id': self.OWNER_ID,
            'commit_message': 'Changed title.',
            'commit_type': 'edit',
            'version_number': 2,
        }, snapshots_metadata[-2])
        self.assertDictContainsSubset({
            'commit_cmds': [{
                'cmd': 'create_new',
                'title': 'A title',
                'category': 'A category'
            }],
            'committer_id': self.OWNER_ID,
            'commit_message': (
                'New exploration created with title \'A title\'.'),
            'commit_type': 'create',
            'version_number': 1
        }, snapshots_metadata[-3])
        self.assertGreaterEqual(
            snapshots_metadata[-1]['created_on'],
            snapshots_metadata[-2]['created_on'])

    def test_versioning_with_add_and_delete_states(self):
        exploration = self.save_new_valid_exploration(
            self.EXP_ID, self.OWNER_ID)

        exploration.title = 'First title'
        exp_services._save_exploration(
            self.OWNER_ID, exploration, 'Changed title.', [])
        commit_dict_2 = {
            'committer_id': self.OWNER_ID,
            'commit_message': 'Changed title.',
            'version_number': 2,
        }
        snapshots_metadata = exp_services.get_exploration_snapshots_metadata(
            self.EXP_ID)
        self.assertEqual(len(snapshots_metadata), 2)

        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        exploration.add_states(['New state'])
        exploration.states['New state'].update_interaction_id('TextInput')
        exp_services._save_exploration(
            'committer_id_2', exploration, 'Added new state', [])

        commit_dict_3 = {
            'committer_id': 'committer_id_2',
            'commit_message': 'Added new state',
            'version_number': 3,
        }
        snapshots_metadata = exp_services.get_exploration_snapshots_metadata(
            self.EXP_ID)
        self.assertEqual(len(snapshots_metadata), 3)
        self.assertDictContainsSubset(
            commit_dict_3, snapshots_metadata[-1])
        self.assertDictContainsSubset(commit_dict_2, snapshots_metadata[-2])
        self.assertGreaterEqual(
            snapshots_metadata[-1]['created_on'],
            snapshots_metadata[-2]['created_on'])

        # Perform an invalid action: delete a state that does not exist. This
        # should not create a new version.
        with self.assertRaisesRegexp(ValueError, 'does not exist'):
            exploration.delete_state('invalid_state_name')

        # Now delete the new state.
        exploration.delete_state('New state')
        exp_services._save_exploration(
            'committer_id_3', exploration, 'Deleted state: New state', [])

        commit_dict_4 = {
            'committer_id': 'committer_id_3',
            'commit_message': 'Deleted state: New state',
            'version_number': 4,
        }
        snapshots_metadata = exp_services.get_exploration_snapshots_metadata(
            self.EXP_ID)
        self.assertEqual(len(snapshots_metadata), 4)
        self.assertDictContainsSubset(commit_dict_4, snapshots_metadata[-1])
        self.assertDictContainsSubset(commit_dict_3, snapshots_metadata[-2])
        self.assertDictContainsSubset(commit_dict_2, snapshots_metadata[-3])
        self.assertGreaterEqual(
            snapshots_metadata[0]['created_on'],
            snapshots_metadata[1]['created_on'])
        self.assertGreaterEqual(
            snapshots_metadata[1]['created_on'],
            snapshots_metadata[2]['created_on'])

        # The final exploration should have exactly one state.
        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        self.assertEqual(len(exploration.states), 1)

    def test_versioning_with_reverting(self):
        exploration = self.save_new_valid_exploration(
            self.EXP_ID, self.OWNER_ID)

        # In version 1, the title was 'A title'.
        # In version 2, the title becomes 'V2 title'.
        exploration.title = 'V2 title'
        exp_services._save_exploration(
            self.OWNER_ID, exploration, 'Changed title.', [])

        # In version 3, a new state is added.
        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        exploration.add_states(['New state'])
        exploration.states['New state'].update_interaction_id('TextInput')
        exp_services._save_exploration(
            'committer_id_v3', exploration, 'Added new state', [])

        # It is not possible to revert from anything other than the most
        # current version.
        with self.assertRaisesRegexp(Exception, 'too old'):
            exp_services.revert_exploration(
                'committer_id_v4', self.EXP_ID, 2, 1)

        # Version 4 is a reversion to version 1.
        exp_services.revert_exploration('committer_id_v4', self.EXP_ID, 3, 1)
        exploration = exp_services.get_exploration_by_id(self.EXP_ID)
        self.assertEqual(exploration.title, 'A title')
        self.assertEqual(len(exploration.states), 1)
        self.assertEqual(exploration.version, 4)

        snapshots_metadata = exp_services.get_exploration_snapshots_metadata(
            self.EXP_ID)

        commit_dict_4 = {
            'committer_id': 'committer_id_v4',
            'commit_message': 'Reverted exploration to version 1',
            'version_number': 4,
        }
        commit_dict_3 = {
            'committer_id': 'committer_id_v3',
            'commit_message': 'Added new state',
            'version_number': 3,
        }
        self.assertEqual(len(snapshots_metadata), 4)
        self.assertDictContainsSubset(
            commit_dict_4, snapshots_metadata[-1])
        self.assertDictContainsSubset(commit_dict_3, snapshots_metadata[-2])
        self.assertGreaterEqual(
            snapshots_metadata[-1]['created_on'],
            snapshots_metadata[-2]['created_on'])


class ExplorationCommitLogUnitTests(ExplorationServicesUnitTests):
    """Test methods relating to the exploration commit log."""

    ALBERT_EMAIL = 'albert@example.com'
    BOB_EMAIL = 'bob@example.com'
    ALBERT_NAME = 'albert'
    BOB_NAME = 'bob'

    EXP_ID_1 = 'eid1'
    EXP_ID_2 = 'eid2'

    COMMIT_ALBERT_CREATE_EXP_1 = {
        'username': ALBERT_NAME,
        'version': 1,
        'exploration_id': EXP_ID_1,
        'commit_type': 'create',
        'post_commit_community_owned': False,
        'post_commit_is_private': True,
        'commit_message': 'New exploration created with title \'A title\'.',
        'post_commit_status': 'private'
    }

    COMMIT_BOB_EDIT_EXP_1 = {
        'username': BOB_NAME,
        'version': 2,
        'exploration_id': EXP_ID_1,
        'commit_type': 'edit',
        'post_commit_community_owned': False,
        'post_commit_is_private': True,
        'commit_message': 'Changed title.',
        'post_commit_status': 'private'
    }

    COMMIT_ALBERT_CREATE_EXP_2 = {
        'username': ALBERT_NAME,
        'version': 1,
        'exploration_id': 'eid2',
        'commit_type': 'create',
        'post_commit_community_owned': False,
        'post_commit_is_private': True,
        'commit_message': 'New exploration created with title \'A title\'.',
        'post_commit_status': 'private'
    }

    COMMIT_ALBERT_EDIT_EXP_1 = {
        'username': 'albert',
        'version': 3,
        'exploration_id': 'eid1',
        'commit_type': 'edit',
        'post_commit_community_owned': False,
        'post_commit_is_private': True,
        'commit_message': 'Changed title to Albert1 title.',
        'post_commit_status': 'private'
    }

    COMMIT_ALBERT_EDIT_EXP_2 = {
        'username': 'albert',
        'version': 2,
        'exploration_id': 'eid2',
        'commit_type': 'edit',
        'post_commit_community_owned': False,
        'post_commit_is_private': True,
        'commit_message': 'Changed title to Albert2.',
        'post_commit_status': 'private'
    }

    COMMIT_BOB_REVERT_EXP_1 = {
        'username': 'bob',
        'version': 4,
        'exploration_id': 'eid1',
        'commit_type': 'revert',
        'post_commit_community_owned': False,
        'post_commit_is_private': True,
        'commit_message': 'Reverted exploration to version 2',
        'post_commit_status': 'private'
    }

    COMMIT_ALBERT_DELETE_EXP_1 = {
        'username': 'albert',
        'version': 5,
        'exploration_id': 'eid1',
        'commit_type': 'delete',
        'post_commit_community_owned': False,
        'post_commit_is_private': True,
        'commit_message': feconf.COMMIT_MESSAGE_EXPLORATION_DELETED,
        'post_commit_status': 'private'
    }

    COMMIT_ALBERT_PUBLISH_EXP_2 = {
        'username': 'albert',
        'version': None,
        'exploration_id': 'eid2',
        'commit_type': 'edit',
        'post_commit_community_owned': False,
        'post_commit_is_private': False,
        'commit_message': 'Exploration published.',
        'post_commit_status': 'public'
    }

    def setUp(self):
        """Populate the database of explorations to be queried against.

        The sequence of events is:
        - (1) Albert creates EXP_ID_1.
        - (2) Bob edits the title of EXP_ID_1.
        - (3) Albert creates EXP_ID_2.
        - (4) Albert edits the title of EXP_ID_1.
        - (5) Albert edits the title of EXP_ID_2.
        - (6) Bob reverts Albert's last edit to EXP_ID_1.
        - (7) Albert deletes EXP_ID_1.
        - Bob tries to publish EXP_ID_2, and is denied access.
        - (8) Albert publishes EXP_ID_2.
        """
        super(ExplorationCommitLogUnitTests, self).setUp()

        self.ALBERT_ID = self.get_user_id_from_email(self.ALBERT_EMAIL)
        self.BOB_ID = self.get_user_id_from_email(self.BOB_EMAIL)
        self.signup(self.ALBERT_EMAIL, self.ALBERT_NAME)
        self.signup(self.BOB_EMAIL, self.BOB_NAME)

        # This needs to be done in a toplevel wrapper because the datastore
        # puts to the event log are asynchronous.
        @transaction_services.toplevel_wrapper
        def populate_datastore():
            exploration_1 = self.save_new_valid_exploration(
                self.EXP_ID_1, self.ALBERT_ID)

            exploration_1.title = 'Exploration 1 title'
            exp_services._save_exploration(
                self.BOB_ID, exploration_1, 'Changed title.', [])

            exploration_2 = self.save_new_valid_exploration(
                self.EXP_ID_2, self.ALBERT_ID)

            exploration_1.title = 'Exploration 1 Albert title'
            exp_services._save_exploration(
                self.ALBERT_ID, exploration_1,
                'Changed title to Albert1 title.', [])

            exploration_2.title = 'Exploration 2 Albert title'
            exp_services._save_exploration(
                self.ALBERT_ID, exploration_2, 'Changed title to Albert2.', [])

            exp_services.revert_exploration(self.BOB_ID, self.EXP_ID_1, 3, 2)

            exp_services.delete_exploration(self.ALBERT_ID, self.EXP_ID_1)

            # This commit should not be recorded.
            with self.assertRaisesRegexp(
                    Exception, 'This exploration cannot be published'):
                rights_manager.publish_exploration(self.BOB_ID, self.EXP_ID_2)

            rights_manager.publish_exploration(self.ALBERT_ID, self.EXP_ID_2)

        populate_datastore()

    def test_get_next_page_of_all_commits(self):
        all_commits = exp_services.get_next_page_of_all_commits()[0]
        self.assertEqual(len(all_commits), 8)
        for ind, commit in enumerate(all_commits):
            if ind != 0:
                self.assertGreater(
                    all_commits[ind - 1].last_updated,
                    all_commits[ind].last_updated)

        commit_dicts = [commit.to_dict() for commit in all_commits]

        # Note that commits are ordered from most recent to least recent.
        self.assertDictContainsSubset(
            self.COMMIT_ALBERT_CREATE_EXP_1, commit_dicts[-1])
        self.assertDictContainsSubset(
            self.COMMIT_BOB_EDIT_EXP_1, commit_dicts[-2])
        self.assertDictContainsSubset(
            self.COMMIT_ALBERT_CREATE_EXP_2, commit_dicts[-3])
        self.assertDictContainsSubset(
            self.COMMIT_ALBERT_EDIT_EXP_1, commit_dicts[-4])
        self.assertDictContainsSubset(
            self.COMMIT_ALBERT_EDIT_EXP_2, commit_dicts[-5])
        self.assertDictContainsSubset(
            self.COMMIT_BOB_REVERT_EXP_1, commit_dicts[-6])
        self.assertDictContainsSubset(
            self.COMMIT_ALBERT_DELETE_EXP_1, commit_dicts[-7])
        self.assertDictContainsSubset(
            self.COMMIT_ALBERT_PUBLISH_EXP_2, commit_dicts[-8])

    def test_get_next_page_of_all_non_private_commits(self):
        all_commits = (
            exp_services.get_next_page_of_all_non_private_commits()[0])
        self.assertEqual(len(all_commits), 1)
        commit_dicts = [commit.to_dict() for commit in all_commits]
        self.assertDictContainsSubset(
            self.COMMIT_ALBERT_PUBLISH_EXP_2, commit_dicts[0])

        #TODO(frederikcreemers@gmail.com) test max_age here.

    def test_paging(self):
        all_commits, cursor, more = exp_services.get_next_page_of_all_commits(
            page_size=5)
        self.assertEqual(len(all_commits), 5)
        commit_dicts = [commit.to_dict() for commit in all_commits]
        self.assertDictContainsSubset(
            self.COMMIT_ALBERT_EDIT_EXP_1, commit_dicts[-1])
        self.assertDictContainsSubset(
            self.COMMIT_ALBERT_EDIT_EXP_2, commit_dicts[-2])
        self.assertDictContainsSubset(
            self.COMMIT_BOB_REVERT_EXP_1, commit_dicts[-3])
        self.assertDictContainsSubset(
            self.COMMIT_ALBERT_DELETE_EXP_1, commit_dicts[-4])
        self.assertDictContainsSubset(
            self.COMMIT_ALBERT_PUBLISH_EXP_2, commit_dicts[-5])
        self.assertTrue(more)

        all_commits, cursor, more = exp_services.get_next_page_of_all_commits(
            page_size=5, urlsafe_start_cursor=cursor)
        self.assertEqual(len(all_commits), 3)
        commit_dicts = [commit.to_dict() for commit in all_commits]
        self.assertDictContainsSubset(
            self.COMMIT_ALBERT_CREATE_EXP_1, commit_dicts[-1])
        self.assertDictContainsSubset(
            self.COMMIT_BOB_EDIT_EXP_1, commit_dicts[-2])
        self.assertDictContainsSubset(
            self.COMMIT_ALBERT_CREATE_EXP_2, commit_dicts[-3])
        self.assertFalse(more)


class ExplorationCommitLogSpecialCasesUnitTests(ExplorationServicesUnitTests):
    """Test special cases relating to the exploration commit logs."""

    def test_paging_with_no_commits(self):
        all_commits, cursor, more = exp_services.get_next_page_of_all_commits(
            page_size=5)
        self.assertEqual(len(all_commits), 0)


class SearchTests(ExplorationServicesUnitTests):
    """Test exploration search."""

    def test_demo_explorations_are_added_to_search_index(self):
        results, cursor = exp_services.search_explorations('Welcome', 2)
        self.assertEqual(results, [])

        exp_services.load_demo('0')
        results, cursor = exp_services.search_explorations('Welcome', 2)
        self.assertEqual(results, ['0'])

    def test_index_explorations_given_ids(self):
        all_exp_ids = ['id0', 'id1', 'id2', 'id3', 'id4']
        expected_exp_ids = all_exp_ids[:-1]
        all_exp_titles = [
            'title 0', 'title 1', 'title 2', 'title 3', 'title 4']
        expected_exp_titles = all_exp_titles[:-1]
        all_exp_categories = ['cat0', 'cat1', 'cat2', 'cat3', 'cat4']
        expected_exp_categories = all_exp_categories[:-1]

        def mock_add_documents_to_index(docs, index):
            self.assertEqual(index, exp_services.SEARCH_INDEX_EXPLORATIONS)
            ids = [doc['id'] for doc in docs]
            titles = [doc['title'] for doc in docs]
            categories = [doc['category'] for doc in docs]
            self.assertEqual(set(ids), set(expected_exp_ids))
            self.assertEqual(set(titles), set(expected_exp_titles))
            self.assertEqual(set(categories), set(expected_exp_categories))
            return ids

        add_docs_counter = test_utils.CallCounter(mock_add_documents_to_index)
        add_docs_swap = self.swap(search_services,
                                  'add_documents_to_index',
                                  add_docs_counter)

        for i in xrange(5):
            self.save_new_valid_exploration(
                all_exp_ids[i],
                self.OWNER_ID,
                all_exp_titles[i],
                category=all_exp_categories[i])

        # We're only publishing the first 4 explorations, so we're not
        # expecting the last exploration to be indexed.
        for i in xrange(4):
            rights_manager.publish_exploration(
                self.OWNER_ID,
                expected_exp_ids[i])

        with add_docs_swap:
            exp_services.index_explorations_given_ids(all_exp_ids)

        self.assertEqual(add_docs_counter.times_called, 1)

    def test_patch_exploration_search_document(self):

        def mock_get_doc(doc_id, index):
            self.assertEqual(doc_id, self.EXP_ID)
            self.assertEqual(index, exp_services.SEARCH_INDEX_EXPLORATIONS)
            return {'a': 'b', 'c': 'd'}

        def mock_add_docs(docs, index):
            self.assertEqual(index, exp_services.SEARCH_INDEX_EXPLORATIONS)
            self.assertEqual(docs, [{'a': 'b', 'c': 'e', 'f': 'g'}])

        get_doc_swap = self.swap(
            search_services, 'get_document_from_index', mock_get_doc)

        add_docs_counter = test_utils.CallCounter(mock_add_docs)
        add_docs_swap = self.swap(
            search_services, 'add_documents_to_index', add_docs_counter)

        with get_doc_swap, add_docs_swap:
            patch = {'c': 'e', 'f': 'g'}
            exp_services.patch_exploration_search_document(self.EXP_ID, patch)

        self.assertEqual(add_docs_counter.times_called, 1)

    def test_update_publicized_exploration_status_in_search(self):

        def mock_get_doc(doc_id, index):
            self.assertEqual(index, exp_services.SEARCH_INDEX_EXPLORATIONS)
            self.assertEqual(doc_id, self.EXP_ID)
            return {}

        def mock_add_docs(docs, index):
            self.assertEqual(index, exp_services.SEARCH_INDEX_EXPLORATIONS)
            self.assertEqual(docs, [{'is': 'featured'}])

        def mock_get_rights(exp_id):
            return rights_manager.ExplorationRights(
                self.EXP_ID,
                [self.OWNER_ID], [self.EDITOR_ID], [self.VIEWER_ID],
                status=rights_manager.EXPLORATION_STATUS_PUBLICIZED
            )

        get_doc_counter = test_utils.CallCounter(mock_get_doc)
        add_docs_counter = test_utils.CallCounter(mock_add_docs)

        get_doc_swap = self.swap(
            search_services, 'get_document_from_index', get_doc_counter)
        add_docs_swap = self.swap(
            search_services, 'add_documents_to_index', add_docs_counter)
        get_rights_swap = self.swap(
            rights_manager, 'get_exploration_rights', mock_get_rights)

        with get_doc_swap, add_docs_swap, get_rights_swap:
            exp_services.update_exploration_status_in_search(self.EXP_ID)

        self.assertEqual(get_doc_counter.times_called, 1)
        self.assertEqual(add_docs_counter.times_called, 1)

    def test_update_private_exploration_status_in_search(self):

        def mock_delete_docs(ids, index):
            self.assertEqual(ids, [self.EXP_ID])
            self.assertEqual(index, exp_services.SEARCH_INDEX_EXPLORATIONS)

        def mock_get_rights(exp_id):
            return rights_manager.ExplorationRights(
                self.EXP_ID,
                [self.OWNER_ID], [self.EDITOR_ID], [self.VIEWER_ID],
                status=rights_manager.EXPLORATION_STATUS_PRIVATE
            )

        delete_docs_counter = test_utils.CallCounter(mock_delete_docs)

        delete_docs_swap = self.swap(
            search_services, 'delete_documents_from_index',
            delete_docs_counter)
        get_rights_swap = self.swap(
            rights_manager, 'get_exploration_rights', mock_get_rights)

        with get_rights_swap, delete_docs_swap:
            exp_services.update_exploration_status_in_search(self.EXP_ID)

        self.assertEqual(delete_docs_counter.times_called, 1)

    def test_search_explorations(self):
        expected_query_string = 'a query string'
        expected_cursor = 'cursor'
        expected_sort = 'title'
        expected_limit = 30
        expected_result_cursor = 'rcursor'
        doc_ids = ['id1', 'id2']

        def mock_search(query_string, index, cursor=None, limit=20, sort='',
                        ids_only=False, retries=3):
            self.assertEqual(query_string, expected_query_string)
            self.assertEqual(index, exp_services.SEARCH_INDEX_EXPLORATIONS)
            self.assertEqual(cursor, expected_cursor)
            self.assertEqual(limit, expected_limit)
            self.assertEqual(sort, expected_sort)
            self.assertEqual(ids_only, True)
            self.assertEqual(retries, 3)

            return doc_ids, expected_result_cursor

        with self.swap(search_services, 'search', mock_search):
            result, cursor = exp_services.search_explorations(
                expected_query_string,
                expected_limit,
                sort=expected_sort,
                cursor=expected_cursor,
            )

        self.assertEqual(cursor, expected_result_cursor)
        self.assertEqual(result, doc_ids)

    def test_get_search_rank(self):
        self.save_new_valid_exploration(self.EXP_ID, self.OWNER_ID)

        self.assertEqual(exp_services._get_search_rank(self.EXP_ID), 20)

        rights_manager.publish_exploration(self.OWNER_ID, self.EXP_ID)
        rights_manager.publicize_exploration(self.user_id_admin, self.EXP_ID)
        self.assertEqual(exp_services._get_search_rank(self.EXP_ID), 50)

        rating_services.assign_rating(self.OWNER_ID, self.EXP_ID, 5)
        self.assertEqual(exp_services._get_search_rank(self.EXP_ID), 60)

        rating_services.assign_rating(self.user_id_admin, self.EXP_ID, 2)
        self.assertEqual(exp_services._get_search_rank(self.EXP_ID), 58)

    def test_search_ranks_cannot_be_negative(self):
        self.save_new_valid_exploration(self.EXP_ID, self.OWNER_ID)

        self.assertEqual(exp_services._get_search_rank(self.EXP_ID), 20)

        # A user can (down-)rate an exploration at most once.
        for i in xrange(50):
            rating_services.assign_rating('user_id_1', self.EXP_ID, 1)
        self.assertEqual(exp_services._get_search_rank(self.EXP_ID), 15)

        for i in xrange(50):
            rating_services.assign_rating('user_id_%s' % i, self.EXP_ID, 1)

        # The rank will be at least 0.
        self.assertEqual(exp_services._get_search_rank(self.EXP_ID), 0)


class ExplorationChangedEventsTests(ExplorationServicesUnitTests):

    def test_exploration_contents_change_event_triggers(self):
        recorded_ids = []

        @classmethod
        def mock_record(cls, exp_id):
            recorded_ids.append(exp_id)

        record_event_swap = self.swap(
            event_services.ExplorationContentChangeEventHandler,
            'record',
            mock_record)

        with record_event_swap:
            self.save_new_valid_exploration(self.EXP_ID, self.OWNER_ID)
            exp_services.update_exploration(self.OWNER_ID, self.EXP_ID, [], '')

        self.assertEqual(recorded_ids, [self.EXP_ID, self.EXP_ID])

    def test_exploration_status_change_event(self):
        recorded_ids = []

        @classmethod
        def mock_record(cls, exp_id):
            recorded_ids.append(exp_id)

        record_event_swap = self.swap(
            event_services.ExplorationStatusChangeEventHandler,
            'record',
            mock_record)

        with record_event_swap:
            self.save_new_default_exploration(self.EXP_ID, self.OWNER_ID)
            rights_manager.create_new_exploration_rights(
                self.EXP_ID, self.OWNER_ID)
            rights_manager.publish_exploration(
                self.OWNER_ID, self.EXP_ID)
            rights_manager.publicize_exploration(
                self.user_id_admin, self.EXP_ID)
            rights_manager.unpublicize_exploration(
                self.user_id_admin, self.EXP_ID)
            rights_manager.unpublish_exploration(
                self.user_id_admin, self.EXP_ID)

        self.assertEqual(recorded_ids, [self.EXP_ID, self.EXP_ID,
                                        self.EXP_ID, self.EXP_ID])


class ExplorationSummaryTests(ExplorationServicesUnitTests):
    """Test exploration summaries."""

    ALBERT_EMAIL = 'albert@example.com'
    BOB_EMAIL = 'bob@example.com'
    ALBERT_NAME = 'albert'
    BOB_NAME = 'bob'

    EXP_ID_1 = 'eid1'
    EXP_ID_2 = 'eid2'

    def test_is_exp_summary_editable(self):
        self.save_new_default_exploration(self.EXP_ID, self.OWNER_ID)

        # Check that only the owner may edit.
        exp_summary = exp_services.get_exploration_summary_by_id(self.EXP_ID)
        self.assertTrue(exp_services.is_exp_summary_editable(
            exp_summary, user_id=self.OWNER_ID))
        self.assertFalse(exp_services.is_exp_summary_editable(
            exp_summary, user_id=self.EDITOR_ID))
        self.assertFalse(exp_services.is_exp_summary_editable(
            exp_summary, user_id=self.VIEWER_ID))

        # Owner makes viewer a viewer and editor an editor.
        rights_manager.assign_role(
            self.OWNER_ID, self.EXP_ID, self.VIEWER_ID,
            rights_manager.ROLE_VIEWER)
        rights_manager.assign_role(
            self.OWNER_ID, self.EXP_ID, self.EDITOR_ID,
            rights_manager.ROLE_EDITOR)

        # Check that owner and editor may edit, but not viewer.
        exp_summary = exp_services.get_exploration_summary_by_id(self.EXP_ID)
        self.assertTrue(exp_services.is_exp_summary_editable(
            exp_summary, user_id=self.OWNER_ID))
        self.assertTrue(exp_services.is_exp_summary_editable(
            exp_summary, user_id=self.EDITOR_ID))
        self.assertFalse(exp_services.is_exp_summary_editable(
            exp_summary, user_id=self.VIEWER_ID))


class ExplorationSummaryGetTests(ExplorationServicesUnitTests):
    """Test exploration summaries get_* functions."""

    ALBERT_EMAIL = 'albert@example.com'
    BOB_EMAIL = 'bob@example.com'
    ALBERT_NAME = 'albert'
    BOB_NAME = 'bob'

    EXP_ID_1 = 'eid1'
    EXP_ID_2 = 'eid2'

    EXPECTED_VERSION_1 = 4
    EXPECTED_VERSION_2 = 2

    def setUp(self):
        """Populate the database of explorations and their summaries.

        The sequence of events is:
        - (1) Albert creates EXP_ID_1.
        - (2) Bob edits the title of EXP_ID_1.
        - (3) Albert creates EXP_ID_2.
        - (4) Albert edits the title of EXP_ID_1.
        - (5) Albert edits the title of EXP_ID_2.
        - (6) Bob reverts Albert's last edit to EXP_ID_1.
        - (7) Albert deletes EXP_ID_1.
        - Bob tries to publish EXP_ID_2, and is denied access.
        - (8) Albert publishes EXP_ID_2.
        """
        super(ExplorationServicesUnitTests, self).setUp()

        self.ALBERT_ID = self.get_user_id_from_email(self.ALBERT_EMAIL)
        self.BOB_ID = self.get_user_id_from_email(self.BOB_EMAIL)
        self.signup(self.ALBERT_EMAIL, self.ALBERT_NAME)
        self.signup(self.BOB_EMAIL, self.BOB_NAME)

        exploration_1 = self.save_new_valid_exploration(
            self.EXP_ID_1, self.ALBERT_ID)

        exploration_1.title = 'Exploration 1 title'
        exp_services._save_exploration(
            self.BOB_ID, exploration_1, 'Changed title.', [])

        exploration_2 = self.save_new_valid_exploration(
            self.EXP_ID_2, self.ALBERT_ID)

        exploration_1.title = 'Exploration 1 Albert title'
        exp_services._save_exploration(
            self.ALBERT_ID, exploration_1,
            'Changed title to Albert1 title.', [])

        exploration_2.title = 'Exploration 2 Albert title'
        exp_services._save_exploration(
            self.ALBERT_ID, exploration_2, 'Changed title to Albert2.', [])

        exp_services.revert_exploration(self.BOB_ID, self.EXP_ID_1, 3, 2)

        with self.assertRaisesRegexp(
                Exception, 'This exploration cannot be published'):
            rights_manager.publish_exploration(self.BOB_ID, self.EXP_ID_2)

        rights_manager.publish_exploration(self.ALBERT_ID, self.EXP_ID_2)

    def test_get_non_private_exploration_summaries(self):

        actual_summaries = exp_services.get_non_private_exploration_summaries()

        expected_summaries = {
            self.EXP_ID_2: exp_domain.ExplorationSummary(
                self.EXP_ID_2, 'Exploration 2 Albert title',
                'A category', 'An objective', 'en', [],
                feconf.get_empty_ratings(),
                rights_manager.EXPLORATION_STATUS_PUBLIC,
                False, [self.ALBERT_ID], [], [], self.EXPECTED_VERSION_2,
                actual_summaries[self.EXP_ID_2].exploration_model_created_on,
                actual_summaries[self.EXP_ID_2].exploration_model_last_updated
                )}

        # check actual summaries equal expected summaries
        self.assertEqual(actual_summaries.keys(),
                         expected_summaries.keys())
        simple_props = ['id', 'title', 'category', 'objective',
                        'language_code', 'tags', 'ratings', 'status',
                        'community_owned', 'owner_ids',
                        'editor_ids', 'viewer_ids', 'version',
                        'exploration_model_created_on',
                        'exploration_model_last_updated']
        for exp_id in actual_summaries.keys():
            for prop in simple_props:
                self.assertEqual(getattr(actual_summaries[exp_id], prop),
                                 getattr(expected_summaries[exp_id], prop))

    def test_get_all_exploration_summaries(self):
        actual_summaries = exp_services.get_all_exploration_summaries()

        expected_summaries = {
            self.EXP_ID_1: exp_domain.ExplorationSummary(
                self.EXP_ID_1, 'Exploration 1 title',
                'A category', 'An objective', 'en', [],
                feconf.get_empty_ratings(),
                rights_manager.EXPLORATION_STATUS_PRIVATE,
                False, [self.ALBERT_ID], [], [], self.EXPECTED_VERSION_1,
                actual_summaries[self.EXP_ID_1].exploration_model_created_on,
                actual_summaries[self.EXP_ID_1].exploration_model_last_updated
            ),
            self.EXP_ID_2: exp_domain.ExplorationSummary(
                self.EXP_ID_2, 'Exploration 2 Albert title',
                'A category', 'An objective', 'en', [],
                feconf.get_empty_ratings(),
                rights_manager.EXPLORATION_STATUS_PUBLIC,
                False, [self.ALBERT_ID], [], [], self.EXPECTED_VERSION_2,
                actual_summaries[self.EXP_ID_2].exploration_model_created_on,
                actual_summaries[self.EXP_ID_2].exploration_model_last_updated
            )
        }

        # check actual summaries equal expected summaries
        self.assertEqual(actual_summaries.keys(),
                         expected_summaries.keys())
        simple_props = ['id', 'title', 'category', 'objective',
                        'language_code', 'tags', 'ratings', 'status',
                        'community_owned', 'owner_ids',
                        'editor_ids', 'viewer_ids', 'version',
                        'exploration_model_created_on',
                        'exploration_model_last_updated']
        for exp_id in actual_summaries.keys():
            for prop in simple_props:
                self.assertEqual(getattr(actual_summaries[exp_id], prop),
                                 getattr(expected_summaries[exp_id], prop))

    def test_get_private_at_least_viewable_exploration_summaries(self):

        actual_summaries = (
            exp_services.get_private_at_least_viewable_exploration_summaries(
                self.ALBERT_ID))

        expected_summaries = {
            self.EXP_ID_1: exp_domain.ExplorationSummary(
                self.EXP_ID_1, 'Exploration 1 title',
                'A category', 'An objective', 'en', [],
                feconf.get_empty_ratings(),
                rights_manager.EXPLORATION_STATUS_PRIVATE,
                False, [self.ALBERT_ID], [], [], self.EXPECTED_VERSION_1,
                actual_summaries[self.EXP_ID_1].exploration_model_created_on,
                actual_summaries[self.EXP_ID_1].exploration_model_last_updated
                )}

        # check actual summaries equal expected summaries
        self.assertEqual(actual_summaries.keys(),
                         expected_summaries.keys())
        simple_props = ['id', 'title', 'category', 'objective',
                        'language_code', 'tags', 'ratings', 'status',
                        'community_owned', 'owner_ids',
                        'editor_ids', 'viewer_ids', 'version',
                        'exploration_model_created_on',
                        'exploration_model_last_updated']
        for exp_id in actual_summaries.keys():
            for prop in simple_props:
                self.assertEqual(getattr(actual_summaries[exp_id], prop),
                                 getattr(expected_summaries[exp_id], prop))

        # do similar test for Bob
        actual_summaries = (
            exp_services.get_private_at_least_viewable_exploration_summaries(
                self.BOB_ID))

        expected_summaries = {}

        # check actual summaries equal expected summaries
        self.assertEqual(actual_summaries,
                         expected_summaries)

    def test_get_at_least_editable_exploration_summaries(self):
        exp_services.delete_exploration(self.ALBERT_ID, self.EXP_ID_1)

        actual_summaries = (
            exp_services.get_at_least_editable_exploration_summaries(
                self.ALBERT_ID))

        expected_summaries = {
            self.EXP_ID_2: exp_domain.ExplorationSummary(
                self.EXP_ID_2, 'Exploration 2 Albert title',
                'A category', 'An objective', 'en', [],
                feconf.get_empty_ratings(),
                rights_manager.EXPLORATION_STATUS_PUBLIC,
                False, [self.ALBERT_ID], [], [], self.EXPECTED_VERSION_2,
                actual_summaries[self.EXP_ID_2].exploration_model_created_on,
                actual_summaries[self.EXP_ID_2].exploration_model_last_updated
        )}

        # check actual summaries equal expected summaries
        self.assertEqual(actual_summaries.keys(),
                         expected_summaries.keys())
        simple_props = ['id', 'title', 'category', 'objective',
                        'language_code', 'tags', 'ratings','status',
                        'community_owned', 'owner_ids',
                        'editor_ids', 'viewer_ids', 'version',
                        'exploration_model_created_on',
                        'exploration_model_last_updated']
        for exp_id in actual_summaries.keys():
            for prop in simple_props:
                self.assertEqual(getattr(actual_summaries[exp_id], prop),
                                 getattr(expected_summaries[exp_id], prop))

        # do similar test for Bob
        actual_summaries = (
            exp_services.get_at_least_editable_exploration_summaries(
                self.BOB_ID))

        expected_summaries = {}

        # check actual summaries equal expected summaries
        self.assertEqual(actual_summaries,
                         expected_summaries)
