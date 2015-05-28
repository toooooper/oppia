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
  '$scope', '$http', '$rootScope', '$modal', '$filter', 'extensionTagAssemblerService',
  'explorationGadgetsService', 'editorContextService', 'GADGET_SPECS',
  function($scope, $http, $rootScope, $modal, $filter, extensionTagAssemblerService,
    explorationGadgetsService, editorContextService, GADGET_SPECS) {
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

    $scope.openAddGadgetModal = function() {
      $modal.open({
        templateUrl: 'modals/addGadget',
        backdrop: 'static',
        resolve: {},
        controller: [
          '$scope', '$modalInstance', 'explorationGadgetsService', 'editorContextService',
          'explorationStatesService', 'GADGET_SPECS',
          function($scope, $modalInstance, explorationGadgetsService, editorContextService,
            explorationStatesService, GADGET_SPECS) {
            $scope.ALLOWED_GADGETS = GLOBALS.ALLOWED_GADGETS;
            //TODO(vjoisar/anuzis): Fix the 2 way data binding for name and layout.
            $scope.GADGET_SPECS = GADGET_SPECS;
            $scope.gadgetLayout = 'left'; //left is default;
            $scope.gadgetName = '';
            $scope.visibleInStates = []
            $scope.explorationStates = Object.keys(explorationStatesService.getStates());
            $scope.onChangeGadgetId = function(newGadgetId) {
              $scope.selectedGadgetId = newGadgetId;
              $scope.gadgetName = explorationGadgetsService.getUniqueGadgetName(newGadgetId);
              $scope.visibleInStates.push(editorContextService.getActiveStateName());
              var gadgetSpec = GADGET_SPECS[newGadgetId];
              $scope.customizationArgSpecs = (
                gadgetSpec.customization_arg_specs
              );
              $scope.tmpCustomizationArgs = [];
              for (var i = 0; i < $scope.customizationArgSpecs.length; i++) {
                $scope.tmpCustomizationArgs.push({
                  name: $scope.customizationArgSpecs[i].name,
                  value: angular.copy(
                    $scope.customizationArgSpecs[i].default_value
                  )
                });
              }
              $scope.$broadcast('schemaBasedFormsShown');
              $scope.form = {};
            };

            $scope.manageVisibilityInStates = function (stateName) {
              var index = $scope.visibleInStates.indexOf(stateName);
              // is currently selected
              if (index > -1) {
                $scope.visibleInStates.splice(index, 1);
              }
              // is newly selected
              else {
                $scope.visibleInStates.push(stateName);
              }
            };
            $scope.returnToGadgetSelector = function() {
              $scope.selectedGadgetId = null;
              $scope.tmpCustomizationArgs = [];
            };
            $scope.cancel = function() {
              $modalInstance.dismiss('cancel');
            };
            $scope.addGadget = function() {
              $modalInstance.close({
                gadgetId: $scope.selectedGadgetId,
                name: $scope.gadgetName,
                gadgetLayout: $scope.gadgetLayout,
                customizationArgs: $scope.tmpCustomizationArgs,
                visibleInStates: $scope.visibleInStates,
              });
            };
        }]
      }).result.then(function(result){
        console.log('result:');
        console.log(result);
        explorationGadgetsService.addGadget(result, result.gadgetLayout);
      }, function() {
        console.log('Gadget modal closed');
      });
    };

    $scope.deleteGadget = function(gadgetId) {
      explorationGadgetsService.deleteGadget(gadgetId);
    }
}]);