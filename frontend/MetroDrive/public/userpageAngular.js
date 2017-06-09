var app = angular.module('userpage',[]);

app.controller('UserbarController', function($scope, $http) {
	$scope.user = {
		'name': '',
		'surname': '',
		'pic': ''
	};

	// gets info about logged user
	$http.get('/api/userpage/user')
	.then(function(response) {
		if (response.data.length != 0) {
			$scope.user.name = response.data.nome;
			$scope.user.surname = response.data.cognome;
			$scope.user.pic = response.data.pic;
			console.log('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ ' + $scope.user.pic);
		} else {
			alert("errore nel caricamento del profilo");
		}
	});

	$scope.logout = function() {
		location.href = "http://localhost:3000/logout";
	};
});

app.controller('ListController', function($scope, $http) {

	$scope.indexList = null;
	$scope.vehicleList = null;
	
	$scope.selectedVehicle = null;
	$scope.selectedIndex = null;

	$scope.kmtot;			// n of travelled km
	$scope.kmAboveLimits;	// n of km above speed limit
	$scope.breaks;			// n of breaks
	$scope.breaksHarsh;		// n of harsh breaks 
	$scope.acc;				// n of accelerations
	$scope.accHarsh;		// n of harsh accelerations
	

	// gets info about logged user's assured vehicles
	$http.get('/api/userpage/vehicles')
	.then(function(response) {
		if (response.data.length != 0) {
			$scope.vehicleList = response.data;
		} else {
			alert("Attenzione!Nessun veicolo registrato");
		}
	});
	
	$scope.selectVehicle = function(v) {
		$scope.selectedVehicle = v;
		$http.get('/api/indexes?v=' + v)
		.then(function(response) {
			if (response.data.length != 0) {
				$scope.indexList = response.data;

				$scope.selectedIndex = response.data[0].mese;

				$scope.kmtot = response.data[0].kmtot;
				$scope.kmAboveLimits = response.data[0].kmSopraLimiti;		
				$scope.breaks = response.data[0].frenate;
				$scope.breaksHarsh = response.data[0].frenateHarsh;	
				$scope.acc = response.data[0].accelerazioni;
				$scope.accHarsh = response.data[0].accelerazioniHarsh;
			} else {
				alert("Attenzione!Nessun indice disponibile");
			}
		});
	};

	$scope.selectIndex = function(i) {
		$scope.selectedIndex = i.mese;

		$scope.kmtot = i.kmtot;
		$scope.kmAboveLimits = i.kmSopraLimiti;		
		$scope.breaks = i.frenate;
		$scope.breaksHarsh = i.frenateHarsh;	
		$scope.acc = i.accelerazioni;
		$scope.accHarsh = i.accelerazioniHarsh;
	};		
});

//filtro per convertire i mesi espressi in numero con il loro nome
app.filter('monthName', function() {
	return function (monthNumber) {
		var monthNames = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
			'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'];
		return monthNames[monthNumber - 1];
	}
});

//filtro per convertire i mesi espressi in numero con il loro nome
app.filter('percentage', function() {
	return function (number) {
		if (/^-?[\d.]+(?:e-?\d+)?$/.test(number)) {
			return Number((number).toFixed(2)) + '%';		
		}
		return number;
	}
});

app.filter('distance', function() {
	return function (number) {
		if (/^-?[\d.]+(?:e-?\d+)?$/.test(number)) {
			return Number((number/1000).toFixed(2)) + 'km';
		}
		return number;
	}
});