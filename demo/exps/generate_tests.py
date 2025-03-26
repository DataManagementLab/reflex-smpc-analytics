from jinja2 import Environment, FileSystemLoader
import subprocess
import os.path
import re

def gen_tests(range_lower,range_upper, step, query_name, execution_mode):
    print(type(range_lower))

    env = Environment(loader=FileSystemLoader('/home/lgu/mp-spdz-0.3.9/demo/templates/spdz-source/'))
    file_list = []

    for i in range(range_lower,range_upper,step):
        context = {
        'sizeOfinput': str(i),
        }
        print(i)
        query_name = 'threejoin'
        # Render the template
        template = env.get_template(f'{query_name}_{execution_mode}_template.mpc') 
        rendered_content = template.render(context) 

        # Save the rendered content to a new file
        file_list.append(f'{query_name}_{execution_mode}_{str(i)}.mpc')
        with open(f'{query_name}_{execution_mode}_{str(i)}.mpc', 'w') as f:
            f.write(rendered_content)

    print("template generated")
    print(file_list)

    return file_list



def compile_tests(file_list):
    for file in file_list:
        filename = file.split(".")[0]
        filesch = filename +'.sch'

        #print(filename)
        if os.path.isfile("/home/lgu/mp-spdz-0.3.9/demo/exps/Programs/Schedules/"+filesch) == True:
            print("used previous compiled file...")
        else:
            try:
                command = ["/home/lgu/mp-spdz-0.3.9/compile.py", "-R", "128", "-b", "100000", file]
                result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    print("Command executed successfully!")
                    #print(result.stdout)
                else:
                    print("Command execution failed:")
                    print(result.stderr)
            except subprocess.CalledProcessError as e:
                print(f"Command execution failed with error: {e}")
def run_test(file_list):
    timepoint= []
    for file in file_list:
        try:
            filename = file.split(".")[0]
            os.chdir("/home/lgu/mp-spdz-0.3.9/demo/exps")
            command = ["/home/lgu/mp-spdz-0.3.9/Scripts/ring.sh", filename]
            result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
            #print(result)
            if result.returncode == 0:
                #print(result.stdout)
                output = find_time_from_stdout(result.stdout)
                timepoint.append(float(output))
                print("Command executed successfully!")
            else:
                print("Command execution failed:")
                print(result.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Command execution failed with error: {e}")

    return timepoint

def run_test_return_cmd(file):
    try:
        filename = file.split(".")[0]
        os.chdir("/home/lgu/mp-spdz-0.3.9/demo/exps")
        command = ["/home/lgu/mp-spdz-0.3.9/Scripts/ring.sh", filename]
        result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        #print(result)
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed with error: {e}")

    return result


def find_time_from_stdout(stdout_output):
    """
    Finds the value associated with "Time =" in a string.

    Args:
        stdout_output: The string containing the standard output.

    Returns:
        The time value as a string, or None if "Time =" is not found.
        If multiple "Time =" entries exist, returns the *first* one found.
    """
    match = re.search(r"Time\s*=\s*([\d.]+)", stdout_output)  # Improved regex
    if match:
        return match.group(1)
    return None




# if __name__ == "__main__":
#     file_list = gen_tests(100,200,100,'threejoin','reflex')
#     compile_tests(file_list)
#     timepoint = run_test(file_list)

#     print(timepoint)

