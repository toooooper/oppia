// Copyright 2014 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Controller for a state's gadgets editor.
 *
 * @author vjoisar@google.com (Vishal Joisar)
 */

// TODO(vjoisar): desc for the gadget ui editor
oppia.controller('GadgetEditor', [
  '$scope', '$http', '$rootScope', '$modal', '$filter', 'editorContextService',
  'gadgetNameService', 'gadgetCustomizationArgsService', 'gadgetLayoutService', 
  'gadgetStateVisibilityService', 'extensionTagAssemblerService', 
  'explorationGadgetsService', 'GADGET_SPECS',
  function($scope, $http, $rootScope, $modal, $filter, editorContextService,
    gadgetNameService, gadgetCustomizationArgsService, gadgetLayoutService, 
    gadgetStateVisibilityService, extensionTagAssemblerService, 
    explorationGadgetsService, GADGET_SPECS) {
    var _gadgetPreviewHtml = function(gadgetData){
        console.log(gadgetData);
      var el = $(
        '<oppia-gadget-' + $filter('camelCaseToHyphens')(gadgetData.gadget_id) + '>');
      el = extensionTagAssemblerService.formatCustomizationArgAttributesForElement(
        el, gadgetData.customization_args);
      return el.get(0).outerHTML;
    };
    $scope.$on('gadgetsInitialized', function(evt) {
      $scope.gadgets = explorationGadgetsService.getGadgets();
      $scope.panels = explorationGadgetsService.getPanels();
      $scope.gadgetPreviewHtml = '';
      for (var gadgetName in $scope.gadgets){
        $scope.gadgetPreviewHtml += _gadgetPreviewHtml($scope.gadgets[gadgetName]);
      }
    });

    $scope.openAddGadgetModal = function(isEditing) {
      $modal.open({
        templateUrl: 'modals/addGadget',
        // Clicking outside this modal should not dismiss it.
        backdrop: 'static',
        resolve: {},
        controller: [
          '$scope', '$modalInstance', 'explorationStatesService', 
          'editorContextService', 'explorationGadgetsService', 
          'gadgetNameService', 'gadgetCustomizationArgsService', 
          'gadgetLayoutService',  'gadgetStateVisibilityService','GADGET_SPECS',
          function($scope, $modalInstance, explorationStatesService, 
            editorContextService, explorationGadgetsService, gadgetNameService,
            gadgetCustomizationArgsService, gadgetLayoutService, 
            gadgetStateVisibilityService, GADGET_SPECS) {

        $scope.ALLOWED_GADGETS = GLOBALS.ALLOWED_GADGETS;
        $scope.GADGET_SPECS = GADGET_SPECS;

        $scope.gadgetNameService = gadgetNameService;
        $scope.gadgetCustomizationArgsService = gadgetCustomizationArgsService;
        $scope.gadgetLayoutService = gadgetLayoutService;
        $scope.gadgetStateVisibilityService = gadgetStateVisibilityService;

        $scope.explorationStates = Object.keys(explorationStatesService.getStates());

        $scope.onChangeGadgetId = function(newGadgetId) {
          $scope.selectedGadgetId = newGadgetId;
          gadgetNameService.displayed = (
            explorationGadgetsService.getUniqueGadgetName(newGadgetId)
          );
          gadgetStateVisibilityService.displayed = 
              [editorContextService.getActiveStateName()];
          var gadgetSpec = GADGET_SPECS[newGadgetId];
          $scope.customizationArgSpecs = gadgetSpec.customization_arg_specs;
          gadgetCustomizationArgsService.displayed = {};
          for (var i = 0; i < $scope.customizationArgSpecs.length; i++) {
              var argName = $scope.customizationArgSpecs[i].name;
            gadgetCustomizationArgsService.displayed[argName] = {
              value: angular.copy(
                $scope.customizationArgSpecs[i].default_value
              )
            };
          }
          $scope.$broadcast('schemaBasedFormsShown');
          $scope.form = {};
        };

        $scope.setTargetPanel = function (panelName) {
          gadgetLayoutService.displayed = panelName;
        };

        $scope.manageVisibilityInStates = function (stateName) {
          var index = gadgetStateVisibilityService.displayed.indexOf(stateName);
          // is currently selected
          if (index > -1) {
            gadgetStateVisibilityService.displayed.splice(index, 1);
          }
          // is newly selected
          else {
            gadgetStateVisibilityService.displayed.push(stateName);
          }
        };
        $scope.returnToGadgetSelector = function() {
          gadgetNameService.displayed = null;
          gadgetCustomizationArgsService.displayed = {};
          gadgetLayoutService.displayed = null;
          gadgetStateVisibilityService.displayed = [];
        };
        $scope.cancel = function() {
          $modalInstance.dismiss('cancel');
        };
        $scope.addGadget = function() {
          //TODO(vjoisar):Add Validation if any field is empty to warn user 
          //  before saving or closing the dialog;
          $modalInstance.close($scope.selectedGadgetId);
        };
        }]
      }).result.then(function(gadgetId){
        gadgetNameService.saveDisplayedValue();
        gadgetCustomizationArgsService.saveDisplayedValue();
        gadgetLayoutService.saveDisplayedValue();
        gadgetStateVisibilityService.saveDisplayedValue();
        _saveNewGadget(gadgetId);
      }, function() {
        console.log('Gadget modal closed');
      });
    };

    $scope.deleteGadget = function(gadgetId) {
      explorationGadgetsService.deleteGadget(gadgetId);
    }
    var _saveNewGadget = function(gadgetId) {
      gadgetDict = {
        gadgetId: gadgetId,
        name: gadgetNameService.savedMemento,
        customizationArgs: gadgetCustomizationArgsService.savedMemento,
         visibleInStates: gadgetStateVisibilityService.savedMemento
      };
      explorationGadgetsService.addGadget(gadgetDict, gadgetLayoutService.savedMemento);
    }
}]);
