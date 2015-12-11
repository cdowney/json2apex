from argparse import ArgumentParser, FileType
from json import load, dumps
from operator import itemgetter
from os import access, linesep, makedirs, path as os_path, W_OK

# pip install iso8601
from iso8601 import parse_date

class_defs = []  # List of generated class names
class_props = {}  # Map of generated class name to class property name and Apex type


def writeable_dir(prospective_dir):
    if not os_path.exists(prospective_dir):
        makedirs(prospective_dir)
    if not os_path.isdir(prospective_dir):
        raise Exception('{0} is not a valid path'.format(prospective_dir))
    if access(prospective_dir, W_OK):
        return prospective_dir
    else:
        raise Exception('{0} is not a writable dir'.format(prospective_dir))


def create_class_def(k):
    name = 'T' + k.capitalize()
    if name in class_defs:
        i = 2
        while name + str(i) in class_defs:
            i += 1
        name += str(i)
    class_defs.append(name)
    class_props[name] = {}
    return name


def apex_type(k, v):
    if v is None:
        return 'String'
    elif isinstance(v, str):
        try:
            parse_date(v)
            return 'DateTime'
        except:
            return 'String'
    elif isinstance(v, int):
        return 'Integer'
    elif isinstance(v, float):
        return 'Double'
    elif isinstance(v, list):
        return 'List<{0}>'.format(apex_type(k, v[0]))
    elif isinstance(v, dict):
        class_name = create_class_def(k)
        process(v, class_name)
        return class_name


def process(obj, parent):
    for k, v in obj.items():
        if v is None:
            class_props[parent][k] = 'String'
        elif isinstance(v, str):
            try:
                parse_date(v)
                class_props[parent][k] = 'DateTime'
            except:
                class_props[parent][k] = 'String'
        elif isinstance(v, int):
            class_props[parent][k] = 'Integer'
        elif isinstance(v, float):
            class_props[parent][k] = 'Double'
        elif isinstance(v, list):
            # Assumes list of the type of the first element
            list_type = apex_type(k, v[0])
            class_props[parent][k] = 'List<{0}>'.format(list_type)
        elif isinstance(v, dict):
            class_name = create_class_def(k)
            class_props[parent][k] = class_name
            process(v, class_name)


def write_class_open(out, cls, num_spaces):
    indent = ' ' * num_spaces
    out.write('{0}public class {1} {{{2}'.format(indent, cls, linesep))


def write_class_close(out, num_spaces):
    indent = ' ' * num_spaces
    out.write('{0}}}{1}'.format(indent, linesep))


def write_class_props(out, props, num_spaces):
    indent = ' ' * num_spaces
    for k, v in props:
        out.write('{0}public {1} {2};{3}'.format(indent, v, k, linesep))


def write_parse_method(out, cls, num_spaces):
    indent = ' ' * num_spaces
    out.write('{0}public static {1} parse(String json) {{{2}'.format(indent, cls, linesep))
    out.write('{0}return ({1})System.JSON.deserialize(json, {2}.class);{3}'.format(indent * 2, cls, cls, linesep))
    out.write('{0}}}{1}'.format(indent, linesep))


def write_test_class(out, cls, json_dict, num_spaces):
    indent = ' ' * num_spaces
    json_str = dumps(json_dict, indent=' ' * num_spaces)
    json_str = (' + ' + linesep).join(["{0}'{1}'".format(indent * 2, line) for line in json_str.split(linesep)])
    out.write('@isTest{0}'.format(linesep))
    out.write('public class Test{0} {{{1}'.format(cls, linesep))
    out.write('{0}@isTest{1}'.format(indent, linesep))
    out.write('{0}public static void testParse() {{{1}'.format(indent, linesep))
    out.write('{0}String json = {1};{2}'.format(indent * 2, json_str, linesep))
    out.write('{0}{1} obj = {2}.parse(json);{3}'.format(indent * 2, cls, cls, linesep))
    out.write('{0}System.assertNotEquals(null, obj);{1}'.format(indent * 2, linesep))
    out.write('{0}}}{1}'.format(indent, linesep))
    out.write('}}{0}'.format(linesep))


def main():
    description = """
    This script will generate an Apex class from a JSON input file.
    """
    parser = ArgumentParser(description=description)
    parser.add_argument('input_json', type=FileType('rU'),
                        help='JSON input file')
    #TODO: implement
    #parser.add_argument('--add-comments', action='store_true',
    #                    help='Add a comment in Apex class with sample value from JSON file')
    parser.add_argument('--output-dir', type=writeable_dir, default='.',
                        help='Directory where Apex class files are written')
    parser.add_argument('--class-name', type=str, default='TRoot',
                        help='The name of the top level class to generate')
    parser.add_argument('--indent-spaces', type=int, default=3,
                        help='The number of spaces to indent Apex class')
    parser.add_argument('--generate-test', action='store_true',
                        help='Generate an Apex test class')
    args = parser.parse_args()

    json_dict = load(args.input_json)
    class_defs.append(args.class_name)
    class_props[args.class_name] = {}
    process(json_dict, parent=args.class_name)
    print(sorted(class_defs))

    output_filename = '{0}.cls'.format(args.class_name)
    output_path = os_path.join(os_path.abspath(args.output_dir), output_filename)
    with open(output_path, 'w') as out:
        write_class_open(out, args.class_name, 0)
        sorted_props = sorted(class_props[args.class_name].items(), key=itemgetter(0))
        write_class_props(out, sorted_props, args.indent_spaces)
        for cls in sorted(class_defs):
            if cls == args.class_name:
                continue
            write_class_open(out, cls, args.indent_spaces)
            sorted_props = sorted(class_props[cls].items(), key=itemgetter(0))
            write_class_props(out, sorted_props, args.indent_spaces * 2)
            write_class_close(out, args.indent_spaces)
        write_parse_method(out, args.class_name, args.indent_spaces)
        write_class_close(out, 0)

    if args.generate_test:
        output_filename = 'Test{0}.cls'.format(args.class_name)
        output_path = os_path.join(os_path.abspath(args.output_dir), output_filename)
        with open(output_path, 'w') as out:
            write_test_class(out, args.class_name, json_dict, args.indent_spaces)

if __name__ == '__main__':
    main()
