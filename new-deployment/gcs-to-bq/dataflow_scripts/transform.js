function transform(line) {
var values = line.split(',');

var obj = new Object();
obj.location = values[0];
obj.GMT_time = values[2];
obj.ip_address = values[1];
obj.request = values[3];
var jsonString = JSON.stringify(obj);

return jsonString;
}