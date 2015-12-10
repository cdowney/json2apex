from argparse import ArgumentParser, FileType
from json import load
from operator import itemgetter
from os import access, linesep, makedirs, path as os_path, W_OK


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


def class_name(k):
    return 'T' + k.capitalize()


def apex_type(k, v):
    if v is None or isinstance(v, str):
        return 'String'
    elif isinstance(v, int):
        return 'Integer'
    elif isinstance(v, float):
        return 'Double'
    elif isinstance(v, list):
        return 'List<{0]>'.format(apex_type(k, v[0]))
    elif isinstance(v, dict):
        return class_name(k)


def process(obj, parent):
    class_defs.append(parent)
    class_props[parent] = {}
    for k, v in obj.items():
        if v is None or isinstance(v, str):
            class_props[parent][k] = 'String'
        elif isinstance(v, int):
            class_props[parent][k] = 'Integer'
        elif isinstance(v, float):
            class_props[parent][k] = 'Double'
        elif isinstance(v, list):
            # Assumes list of the type of the first element
            class_props[parent][k] = 'List<{0}>'.format(apex_type(k, v[0]))
        elif isinstance(v, dict):
            class_props[parent][k] = class_name(k)
            process(v, class_name(k))


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
    args = parser.parse_args()

    result = load(args.input_json)
    process(result, parent=args.class_name)

    output_filename = os_path.join(os_path.abspath(args.output_dir), args.class_name + '.apxc')
    with open(output_filename, 'w') as out:
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
        write_class_close(out, 0)

if __name__ == '__main__':
    main()
