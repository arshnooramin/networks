function searchArt() {
	var url = "https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=True&q="
	var query = document.getElementById("artSearch").value

	console.log("making fetch to", url + query)
	
	fetch(url + query)
		.then(resp=>{return resp.json()})
		.then(json=>{
			console.log(json)
			
			if (json.total > 0) {
				document.getElementById("infoMsg2").style.display = "block"
				document.getElementById("infoMsg1").style.display = "None"
				document.getElementById("infoMsg2").innerHTML = "Searched MET Art database found — " + json.total + " Results"

				objId = json.objectIDs[0]
				
				artUrl = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"
				fetch(artUrl + objId)
				.then(resp2=>{return resp2.json()})
				.then(json2=>{
					console.log(json2)

					document.getElementById("artImage").style.display = "block"
					document.getElementById("artImage").src = json2.primaryImageSmall
				})
			}
			
			else {
				document.getElementById("infoMsg2").style.display = "None"
				document.getElementById("artImage").style.display = "None"
				document.getElementById("infoMsg1").style.display = "block"
			}
		})
}

document.addEventListener("DOMContentLoaded", () => {
  
});