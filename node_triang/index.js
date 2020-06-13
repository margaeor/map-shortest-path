
var earcut = require('earcut');
var fs = require('fs');

let rawdata = fs.readFileSync('../data.json');

let data = JSON.parse(rawdata);

var dt = data[data.length-5];


var c = earcut(dt);
var d = earcut.deviation(dt,null,2, c);

console.log(dt.length);
console.log(c);
console.log(d);

console.log(earcut([1,1,2,4,3,6,5,2]));

data.forEach((e,i) => {
     console.log(i);
     earcut(e);
 });


//console.log(data);