"use strict";

function send_movement(movement) {
    let data = new FormData();

    data.append("movement", movement);

    fetch("/set_movement", {
        method: "POST",
        header: {
            "Content-Type": "application/json;charset=UTF-8"
        },
        body: data
    }).then(response => {
        return response.json();
    }).then(json => {
        if(json["state"] == "error") {
            console.error("We are experiencing some errors. Please try again later!");
        }
    }).catch(error => {
        console.error(error);
    });
}