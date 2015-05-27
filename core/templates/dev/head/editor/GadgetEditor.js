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
  '$scope', '$http', '$rootScope', '$modal', '$filter',
  'explorationGadgetsService', 'editorContextService', 'GADGET_SPECS',
  function($scope, $http, $rootScope, $modal, $filter,
    explorationGadgetsService, editorContextService, GADGET_SPECS) {
    $scope.gadgetId = '';

    $scope.openAddGadgetModal = function() {
      $modal.open({
        templateUrl: 'modals/addGadget',
        backdrop: 'static',
        resolve: {},
        controller: [
          '$scope', '$modalInstance', 'GADGET_SPECS',
          function($scope, $modalInstance, GADGET_SPECS) {
            $scope.ALLOWED_GADGETS = GLOBALS.ALLOWED_GADGETS;
            $scope.GADGET_SPECS = GADGET_SPECS;
            $scope.onChangeGadgetId = function(newGadgetId) {
              $scope.selectedGadgetId = newGadgetId;
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
                customizationArgs: $scope.tmpCustomizationArgs
              });
            };
        }]
      }).result.then(function(result){
        $scope.gadgetId = result.selectedGadgetId;
        $scope.$parent.gadgetId = result.selectedGadgetId;
        //TODO(anuzis/vjoisar): Add logic for multiple state visibility.
        // visibleInStates is an array of strings.
        var visibleInStates = [];
        visibleInStates.push(editorContextService.getActiveStateName());
        result['visibleInStates'] = visibleInStates;
        //TODO(anuzis/vjoisar): Add logic to select position from the form.
        var panelName = 'left';
        explorationGadgetsService.addGadget(result, panelName);
      }, function() {
        console.log('Gadget modal closed');
      });
    };

    $scope.deleteGadget = function(gadgetId) {
      explorationGadgetsService.deleteGadget(gadgetId);
    }
}]);