(function () {
  'use strict';

  angular.module('WordcountApp', [])
    .controller('WordcountController', ['$scope', '$log', '$http', '$timeout', function ($scope, $log, $http, $timeout) {

      $scope.isArray = angular.isArray;
      $scope.submitButtonText = "Submit";
      $scope.loading = false;
      $scope.urlerror = false;

      $scope.getResults = function () {
        var url = $scope.url;
        $http.post('/start', { 'url': url })
          .success(function (data) {
            $log.log(data);
            getWordCount(data);
            $scope.wordcount = null;
            $scope.loading = true;
            $scope.submitButtonText = "Loading...";
            $scope.urlerror = false;
          })
          .error(function (err) {
            $log.log("Problem reaching URL " + url);
            $log.log(err);
            $log.urlerror = true;
          });
      };

      function getWordCount(jobid) {

        var timeout = null;

        var poller = function () {
          $http.get('/results/' + jobid)
            .success(function (data, status, header, config) {
              if (status == 202) {
                $log.log(data, status);
              } else if (status == 200) {
                $log.log(data);
                $scope.wordcount = data;
                $scope.loading = false;
                $scope.submitButtonText = "Submit";
                $timeout.cancel(timeout);
                return false;
              }
              // continue to call the poller() function every 2 seconds
              // until the timeout is cancelled
              timeout = $timeout(poller, 3000);
            }).error(function (err) {
              $log.error(err);
              $scope.loading = false;
              $scope.submitButtonText = "Submit";
              $scope.urlerror = true;
            });
        };

        poller();
      }
    }
    ]);

}());
