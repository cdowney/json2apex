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

## Example

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
