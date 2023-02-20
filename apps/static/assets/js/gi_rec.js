"use strict";

var lat = 0;
var lon = 0;
function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  }
}

function showPosition(position) {
    lat = position.coords.latitude;
    lon = position.coords.longitude;
    $("#main_panel").append(lat);
}

$(document).ready(function(){
    getLocation();

});