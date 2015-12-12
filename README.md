# json2apex
Generate an Apex class to deserialize JSON from a JSON input file.

## Usage
```
usage: json2apex.py [-h] [--output-dir OUTPUT_DIR] [--class-name CLASS_NAME]
                    [--indent-spaces INDENT_SPACES] [--generate-test]
                    input_json

This script will generate an Apex class from a JSON input file.

positional arguments:
  input_json            JSON input file

optional arguments:
  -h, --help            show this help message and exit
  --output-dir OUTPUT_DIR
                        Directory where Apex class files are written
  --class-name CLASS_NAME
                        The name of the top level class to generate
  --indent-spaces INDENT_SPACES
                        The number of spaces to indent Apex class
  --generate-test       Generate an Apex test class
```

## Example 1 - Basic Example

### JSON input
```json
{
   "doubleProp": 3.14,
   "integerProp": 13,
   "booleanProp": false,
   "dateTimeProp": "2015-01-20T19:08:50.500-0500",
   "stringProp": "string value",
   "complexProp": { "subProp1": 1, "subProp2": true },
   "arrayProp": [1.0, 1.2, 1.4, 1.6]
}
```

### Apex output

#### Apex Class
```Apex
public class Example {
   public List<Double> arrayProp;
   public Boolean booleanProp;
   public TComplexprop complexProp;
   public DateTime dateTimeProp;
   public Double doubleProp;
   public Integer integerProp;
   public String stringProp;
   public class TComplexprop {
      public Integer subProp1;
      public Boolean subProp2;
   }
   public static Example parse(String json) {
      return (Example)System.JSON.deserialize(json, Example.class);
   }
}
```

#### Apex Test Class
```Apex
@isTest
public class TestExample {
   @isTest
   public static void testParse() {
      String json =       '{' +
      '   "doubleProp": 3.14,' +
      '   "booleanProp": false,' +
      '   "stringProp": "string value",' +
      '   "integerProp": 13,' +
      '   "complexProp": {' +
      '      "subProp1": 1,' +
      '      "subProp2": true' +
      '   },' +
      '   "dateTimeProp": "2015-01-20T19:08:50.500-0500",' +
      '   "arrayProp": [' +
      '      1.0,' +
      '      1.2,' +
      '      1.4,' +
      '      1.6' +
      '   ]' +
      '}';
      Example obj = Example.parse(json);
      System.assertNotEquals(null, obj);
   }
}
```
## Example 2 - Google Maps

The following JSON is returned by the Google Maps API. 
```json
{
   "results" : [
      {
         "address_components" : [
            {
               "long_name" : "277",
               "short_name" : "277",
               "types" : [ "street_number" ]
            },
            {
               "long_name" : "Bedford Ave",
               "short_name" : "Bedford Ave",
               "types" : [ "route" ]
            },
            {
               "long_name" : "Williamsburg",
               "short_name" : "Williamsburg",
               "types" : [ "neighborhood", "political" ]
            },
            {
               "long_name" : "Brooklyn",
               "short_name" : "Brooklyn",
               "types" : [ "sublocality_level_1", "sublocality", "political" ]
            },
            {
               "long_name" : "Kings County",
               "short_name" : "Kings County",
               "types" : [ "administrative_area_level_2", "political" ]
            },
            {
               "long_name" : "New York",
               "short_name" : "NY",
               "types" : [ "administrative_area_level_1", "political" ]
            },
            {
               "long_name" : "United States",
               "short_name" : "US",
               "types" : [ "country", "political" ]
            },
            {
               "long_name" : "11211",
               "short_name" : "11211",
               "types" : [ "postal_code" ]
            }
         ],
         "formatted_address" : "277 Bedford Ave, Brooklyn, NY 11211, USA",
         "geometry" : {
            "location" : {
               "lat" : 40.714232,
               "lng" : -73.9612889
            },
            "location_type" : "ROOFTOP",
            "viewport" : {
               "northeast" : {
                  "lat" : 40.7155809802915,
                  "lng" : -73.9599399197085
               },
               "southwest" : {
                  "lat" : 40.7128830197085,
                  "lng" : -73.96263788029151
               }
            }
         },
         "partial_match" : true,
         "place_id" : "ChIJd8BlQ2BZwokRAFUEcm_qrcA",
         "types" : [ "street_address" ]
      }
   ],
   "status" : "OK"
}
```

To easily consume the data in Apex using native data types, use json2apex to generate a parser. First save the JSON to maps.json, then run the generator.
```
python json2apex.py --class-name=GMap --generate-test maps.json
```

The output produced:
```Apex
public class GMap {
   public List<TResults> results;
   public String status;
   public class TAddress_components {
      public String long_name;
      public String short_name;
      public List<String> types;
   }
   public class TGeometry {
      public TLocation location;
      public String location_type;
      public TViewport viewport;
   }
   public class TLocation {
      public Double lat;
      public Double lng;
   }
   public class TNortheast {
      public Double lat;
      public Double lng;
   }
   public class TResults {
      public List<TAddress_components> address_components;
      public String formatted_address;
      public TGeometry geometry;
      public Boolean partial_match;
      public String place_id;
      public List<String> types;
   }
   public class TSouthwest {
      public Double lat;
      public Double lng;
   }
   public class TViewport {
      public TNortheast northeast;
      public TSouthwest southwest;
   }
   public static GMap parse(String json) {
      return (GMap)System.JSON.deserialize(json, GMap.class);
   }
}
```
Then to use the generated class:

```Apex
Http http = new Http();
HttpRequest request = new HTTPRequest();
request.setEndpoint(googleMapsApiUrl +'?api_key=' + apiKey + '&location=' + 
                    EncodingUtil.urlEncode(location, 'utf-8') + '&timestamp=' + EncodingUtil.urlEncode(timestamp, 'utf-8'));
request.setMethod('GET');
request.setHeader('Accept', 'application/json');

HttpResponse response = http.send(request);
if (response.getStatusCode() == 200) {
   GMap gMapResult = GMap.parse(response.getBody());  
} else {
   System.debug('Unsuccessfull GET: ' + response.getStatusCode());
}
```
