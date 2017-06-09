function Singleton(){
	if(Singleton.prototype.instance){
		return Singleton.prototype.instance;
	}

	Singleton.prototype.instance = this;

	var name = "";

	this.setInstance = function(username) {
		this.name = username;
	}
	this.getInstance = function() {
		return this.name;
	}
}