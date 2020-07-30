(function() {
  'use strict';

  angular.module('WordcountApp', [])
  .controller('WordcountController', ['$scope', '$log', '$http', '$timeout', function($scope, $log, $http, $timeout) {

      $scope.isArray = angular.isArray;

      $scope.getResults = function() {
        var url = $scope.url;
        $http.post('/start', {'url': url})
            .success(function(data) {
                $log.log(data);
                getWordCount(data);
            })
            .error(function (err) {
                $log.error(err);
            });
      };

      function getWordCount(jobid) {

        var timeout = null;

        var poller = function() {
          $http.get('/results/' + jobid)
            .success(function(data, status, header, config) {
              if (status == 202) {
                $log.log(data, status);
              } else if (status == 200) {
                $log.log(data);
                $scope.wordcount = data;
                $timeout.cancel(timeout);
                return false;
              }
              // continue to call the poller() function every 2 seconds
              // until the timeout is cancelled
              timeout = $timeout(poller, 3000);
            });
        }

        poller();
      }
    }
  ]);

}());
