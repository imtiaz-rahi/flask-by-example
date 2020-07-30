(function () {
  'use strict';

  angular.module('WordcountApp', [])
    .controller('WordcountController', ['$scope', '$log', '$http', '$timeout', function($scope, $log, $http, $timeout) {

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
    }])

    .directive('wordCountChart', ['$parse', function($parse) {
      return {
        restrict: 'E',
        replace: true,
        template: '<div id="chart"></div>',
        link: function(scope) {

          scope.$watch('wordcount', function() {

            d3.select('#chart').selectAll('*').remove();
            var data = scope.wordcount;

            for (var word in data) {
              //console.log(word + " :: " + word[0] + " :: " + data[word]);
              var key = data[word][0];
              var val = data[word][1];

              d3.select('#chart').append('div')
                .selectAll('div')
                .data(word[0])
                .enter().append('div')
                  .style('width', _ => (val * 3) + 'px')
                  //.style('width', function() { return (val * 3) + 'px'; })
                  .text(function(d) { return key; })
                ;
            }
          }, true);
        }
      };
    }]);

}());
