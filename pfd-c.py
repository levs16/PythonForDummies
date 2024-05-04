import argparse
import subprocess
import sys

def parse_line(line, indent_level):
    tokens = line.strip().split()
    if not tokens:
        return "", indent_level  # Return empty string for blank lines

    command = tokens[0]
    indent = "    " * indent_level  # 4 spaces per indent level

    try:
        if command == "store":
            expression = " ".join(tokens[1:tokens.index("in")]).replace("call ", "")
            var_names = tokens[tokens.index("in") + 1]
            # Handle unpacking syntax
            if "," in var_names:
                var_list = var_names.split(",")
                return f'{indent}{", ".join(var_list)} = {expression}', indent_level
            else:
                return f'{indent}{var_names} = {expression}', indent_level
        elif command == "print":
            message = " ".join(tokens[1:]).replace("call ", "")
            return f'{indent}print({message})', indent_level
        elif command == "return":
            expression = " ".join(tokens[1:]).replace("call ", "")
            return f'{indent}return {expression}', indent_level
        elif command == "call":
            func_call = " ".join(tokens[1:])
            if func_call.endswith(")"):
                return f'{indent}{func_call}', indent_level
            else:
                return f'{indent}{func_call}()', indent_level
        elif command == "if":
            condition = " ".join(tokens[1:tokens.index("then")]).replace("is like", "==")
            return f'{indent}if {condition}:', indent_level + 1
        elif command == "else":
            if tokens[1] == "then":
                return f'{indent}else:', indent_level + 1
            else:
                return f"{indent}else:  # Error: Expected 'then' after 'else'", indent_level
        elif command == "elseif":
            condition = " ".join(tokens[1:tokens.index("then")]).replace("is like", "==")
            return f'{indent}elif {condition}:', indent_level + 1
        elif command == "for":
            var = tokens[1]
            if "up to" in line:
                stop = line.split("up to")[1].strip()
                return f'{indent}for {var} in range({stop}):', indent_level + 1
            elif "from" in line and "to" in line:
                parts = line.split()
                start = parts[parts.index("from") + 1]
                stop = parts[parts.index("to") + 1]
                return f'{indent}for {var} in range({start}, {stop}):', indent_level + 1
        elif command == "while":
            condition = " ".join(tokens[1:])
            return f'{indent}while {condition}:', indent_level + 1
        elif command == "function":
            func_name = tokens[1]
            args_index = tokens.index("args")
            args = " ".join(tokens[args_index + 1:])
            return f'{indent}def {func_name}({args}):', indent_level + 1
        elif command == "try":
            return f'{indent}try:', indent_level + 1
        elif command == "except":
            exception = tokens[1]
            return f'{indent}except {exception}:', indent_level + 1
        elif command == "import":
            module = tokens[1]
            return f'{indent}import {module}', indent_level
        elif command == "end":
            return "", indent_level - 1
        else:
            # Handle not directly translatable code by inserting it as is
            return f"{indent}{line}", indent_level
    except IndexError as e:
        return f"{indent}# Error: Malformed line - {str(e)}", indent_level
    except SyntaxError as e:
        return f"{indent}# Error: {str(e)}", indent_level
    except Exception as e:
        return f"{indent}# Error: Unexpected error - {str(e)}", indent_level
    

def translate_to_python(custom_code):
    python_code = []
    indent_level = 0
    for line in custom_code.strip().split("\n"):
        python_line, new_indent_level = parse_line(line, indent_level)
        python_code.append(python_line)
        indent_level = new_indent_level
    return "\n".join(python_code)

def main():
    parser = argparse.ArgumentParser(description="Translate PythonForDummies (.pfd) files to Python (.py) and optionally execute them.")
    parser.add_argument("-c", "--compile", help="Compile the .pfd file into a .py file", action="store_true")
    parser.add_argument("-e", "--compile-and-execute", help="Compile the .pfd file into a .py file and execute it", action="store_true")
    parser.add_argument("input_file", help="Input file name with .pfd extension")
    parser.add_argument("output_file", help="Output file name with .py extension")
    args = parser.parse_args()

    if not args.input_file.endswith(".pfd"):
        print("Input file must have a .pfd extension")
        sys.exit(1)
    if not args.output_file.endswith(".py"):
        print("Output file must have a .py extension")
        sys.exit(1)

    with open(args.input_file, "r") as file:
        custom_code = file.read()

    python_code = translate_to_python(custom_code)

    with open(args.output_file, "w") as file:
        file.write(python_code)

    if args.compile_and_execute:
        subprocess.run(["python3", args.output_file])

if __name__ == "__main__":
    main()
