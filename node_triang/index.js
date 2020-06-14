
var earcut = require('earcut');
var fs = require('fs');

let rawdata = fs.readFileSync('../data.json');

let data = JSON.parse(rawdata);

var testPoints = [[]];

for (let i = 0,j=0; i < data[0].length; i+=2,j++) {
    //const element = array[i];
    testPoints[0].push([data[0][i],data[0][i+1]]);
}

// var dt = data[data.length-5];

var flat = earcut.flatten(testPoints);
var c = earcut(flat.vertices, flat.holes, flat.dimensions);
console.log(c);

fs.writeFileSync('../data_out.json',c)

// var d = earcut.deviation(dt,null,2, c);

// console.log(dt.length);
// console.log(c);
// console.log(d);

//console.log(earcut([1,1,2,4,3,6,5,2]));

// data.forEach((e,i) => {
//      console.log(i);
//      ee = earcut(e);
//      var d = earcut.deviation(e,null,2, ee);
//      fs.writeFileSync('../data_out.json',ee)
//      console.log(ee);
//      console.log(d);
//  });


//console.log(data);