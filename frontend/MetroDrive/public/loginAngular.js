var app = angular.module('login', []);

app.controller('MainController', function($scope, $http) {
	$scope.utente = {
		'email': '',
		'password': ''
	};

	$scope.validate = function() {
		$http.get("/api/login?n=" + $scope.utente.email + "&p=" + $scope.utente.password)
		.then(function(response) {
			if (response.data) {
				location.href = "http://localhost:3000/userpage";
			} else {
				// advert the error and reset input fields
				alert("Attenzione!Username e/o password errati");
				$scope.utente.username = '';
				$scope.utente.password = '';
			}
		});
	};
});
