"use strict";

function send_movement(movement) {
    let data = new FormData();

    data.append("movement", movement);

    fetch("/controller", {
        method: "POST",
        header: {
            "Content-Type": "application/json;charset=UTF-8"
        },
        body: data
    }).then(response => {
        return response.json();
    }).then(json => {
        if(json["state"] == "ERROR") {
            console.error("Error");
        }
    }).catch(error => {
        console.error(error);
    });
}
