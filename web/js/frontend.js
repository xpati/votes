// the URL of the WAMP Router (Crossbar.io)
//
var wsuri;
if (document.location.origin == "file://") {
   wsuri = "ws://127.0.0.1:8080/ws";

} else {
   wsuri = (document.location.protocol === "http:" ? "ws:" : "wss:") + "//" +
               document.location.host + "/ws";
}


// the WAMP connection to the Router
//
var connection = new autobahn.Connection({
   url: wsuri,
   realm: "crossbardemo"
});


// fired when connection is established and session attached
//
connection.onopen = function (session, details) {

   main(session);


};

function main (session) {
   // subscribe to future vote event
   session.subscribe("io.crossbar.demo.vote.onvote",
      function(args) {
         var event = args[0];
         document.getElementById("votes" + event.subject).value = event.votes;

	var winner=document.getElementById("votesWinner").value;
	var vote=document.getElementById("votes" + event.subject).value;
	
	if(winner=="No Winner"){
			
		var different="";
		if (event.subject!="Chocolate") {
		  different="Chocolate";
		} else if (event.subject!="Banana") {
		     different="Banana";
		} else {
		     different="Lemon";
		}
		
		var otherVote = document.getElementById("votes"+different).value;

		if(vote>otherVote){
			winner=event.subject;
		}else{	
			winner="No Winner";
		}
		
	}else{
		var voteWining=  document.getElementById("votes" + winner).value;

		if(vote>voteWining){
			winner=event.subject;
		}
		if(vote==voteWining && winner!=event.subject){
			winner="No Winner";
		}
	}

	document.getElementById("votesWinner").value=winner;

      });


   // get the current vote count
   session.call("io.crossbar.demo.vote.get").then(
      function(res){
	var items = [0,0,0,0];	
	var winner="No Winner"; // 1 lemon    2 banana 3chcocolate

	for(var i = 1; i < res.length; i++) {
            document.getElementById("votes" + res[i].subject).value =res[i].votes;    
 	   items[i]=document.getElementById("votes" + res[i].subject).value;
         }
		
	if(items[1]>items[2] && items[1]>items[3]){
		winner="Lemon";
	}
	if(items[2]>items[1] && items[2]>items[3]){
		winner="Banana";
	}
	if(items[3]>items[1] && items[3]>items[2]){
		winner="Chocolate";
	}

	document.getElementById("votesWinner").value =winner;

   }, session.log);


   // wire up vote buttons
   var voteButtons = document.getElementById("voteContainer").getElementsByTagName("button");
   for (var i = 0; i < voteButtons.length; i++) {
      voteButtons[i].onclick = function(evt) {
         session.call("io.crossbar.demo.vote.vote",[evt.target.id]).then(session.log, session.log);
      };
   }


   // subscribe to vote reset event
   session.subscribe("io.crossbar.demo.vote.onreset", function() {
         var voteCounters = document.getElementById("voteContainer").
                                     getElementsByTagName("input");
         for(var i = 0; i < voteCounters.length; i++) {
            voteCounters[i].value = 0;
         }
      });

   // wire up reset button
   document.getElementById("resetVotes").onclick = function() {
      session.call("io.crossbar.demo.vote.reset").
         then(session.log, session.log);
   };
}


// fired when connection was lost (or could not be established)
//
connection.onclose = function (reason, details) {

   console.log("Connection lost: " + reason);

}


// now actually open the connection
//
connection.open();

