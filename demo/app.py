from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
import random
import duckdb
from flask_socketio import SocketIO, emit
import os
from exps.generate_tests import *
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app)


query_plan_data = {
    "name": "Query Root",
    "children": [
        {"name": "Table Scan (Employees)"},
        {
            "name": "Index Scan (Departments)",
            "children": [{"name": "Filter: DepartmentID > 10"}],
        },
        {"name": "Hash Join"},
    ],
}

query_plan_data2= {
  "name": "Query Root",
  "children": [
    {
      "name": "Table Scan (Table1)",
      "children": [
        {
          "name": "Filter: table1.k = table2"
        },
        {
          "name": "Filter: table1.v = 333"
        }
      ]
    },
    {
      "name": "Table Scan (Table2)",
      "children": [
        {
          "name": "Filter: table2.v > 445"
        }
      ]
    },
    {
      "name": "Hash Join",
      "children": [
        {
          "name": "Join Condition: table2.v > 445"
        }
      ]
    }
  ],
}


@app.route('/',methods=['GET','POST'])
def index():
    # Sample Python code to generate data (replace with your actual logic)
    if request.method == 'GET':
        import random
        data = {
            'labels': ['100', '200', '300', '400', '500', '600', '700','800','900','1000'],
            'datasets': [
                {
                'label': 'Fully Oblivious',
                'data': [random.randint(0, 30) for _ in range(10)],
                'borderColor': 'rgba(255, 99, 132, 1)',
                'fill': False
            },
                {
                'label': 'Sorting Based',
                'data': [random.randint(0, 30) for _ in range(10)],
                'borderColor': 'rgba(100, 33, 112, 1)',
                'fill': False
            },
                {
                'label': 'Reflex',
                'data': [random.randint(0, 30) for _ in range(10)],
                'borderColor': 'rgba(100, 33, 112, 1)',
                'fill': False
            }

            ]
        }

        options = {
            'scales': {
                'x': {
                    'title': {
                        'display': True,
                        'text': 'Input Size' 
                    }
                },
                'y': {
                    'title': {
                        'display': True,
                        'text': 'Execution Time (s)' 
                    }
                }
            }
        }
        return render_template('reflextest.html', chart_data=data, chart_options=options, data=query_plan_data)
        
    if request.method == 'POST':
        selected_dataset = request.form.get('dataset')
        eagermode = request.form.get('eagermode')
        os.chdir('/home/lgu/mp-spdz-0.3.9/demo/exps')
        file_list = gen_tests(100,1100,100,'threejoin_reflex_')
        compile_tests(file_list)
        timepoint = run_test(file_list)
        print(timepoint)

        data = {
            'labels': ['100', '200', '300', '400', '500', '600', '700','800','900','1000'],
            'datasets': [
                {
                'label': 'Fully Oblivious',
                'data': [1,1,1,1,1,1,1,1,1,1],
                'borderColor': 'rgba(255, 99, 132, 1)',
                'fill': False
            },
                {
                'label': 'Sorting Based',
                'data': [1,1,1,1,1,1,1,1,1,1],
                'borderColor': 'rgba(100, 33, 112, 1)',
                'fill': False
            },
                {
                'label': 'Reflex',
                'data': timepoint,
                'borderColor': 'rgba(100, 33, 112, 1)',
                'fill': False
            }

            ]
        }

        options = {
            'scales': {
                'x': {
                    'title': {
                        'display': True,
                        'text': 'Input Size' 
                    }
                },
                'y': {
                    'title': {
                        'display': True,
                        'text': 'Execution Time (s)' 
                    }
                }
            }
        }

        print(selected_dataset)
        print(eagermode)

        return render_template('index.html', chart_data=data, chart_options=options)

    

@app.route('/update_data', methods=['POST'])
def update_data():

    q1 = 'threejoin_reflex_' #Fully Oblivious vs. Sorting Based vs. Reflex
    q2 = ''                  # Sequential vs. Parallel
    q3 = ''                  # beta distribution vs. TLap.
    selected_dataset = request.form.get('dataset')
    eagermode = request.form.get('eagermode')
    os.chdir('/home/lgu/mp-spdz-0.3.9/demo/exps')
    file_list = gen_tests(100,1100,100,'threejoin_reflex_')
    compile_tests(file_list)
    timepoint = run_test(file_list)
    print(timepoint)

    data = {
        'labels': ['100', '200', '300', '400', '500', '600', '700','800','900','1000'],
        'datasets': [
            {
            'label': 'Fully Oblivious',
            'data': [5,15,30,80,190,400,900,4000,9000,25000],
            'borderColor': 'rgba(255, 99, 132, 1)',
            'fill': False
        },
            {
            'label': 'Sorting Based',
            'data': [2,5,7,9,12,15,17,19,21,24],
            'borderColor': 'rgba(100, 33, 112, 1)',
            'fill': False
        },
            {
            'label': 'Reflex',
            'data': timepoint,#[1,1,1,1,1,1,1,1,1,1]
            'borderColor': 'rgba(100, 33, 112, 1)',
            'fill': False
        }

        ]
    }

    options = {
        'scales': {
            'x': {
                'title': {
                    'display': True,
                    'text': 'Input Size' 
                }
            },
            'y': {
                'type': 'logarithmic',
                'title': {
                    'display': True,
                    'text': 'Execution Time (s)' 
                }
            }
        }
    }
    ## img adding
    # query_id = request.form.get('dataset') # Or however you identify the query
    # image_paths_for_this_query = ['threejoin-full','threejoin-sorting','threejoin-reflex']#image_paths.get(query_id)

    # if image_paths_for_this_query:
    #     html = "<h2>Query Plan Trees</h2><div class='pdf-container'>" # Start the container
    #     for path in image_paths_for_this_query:
    #         html += f"<img src='./assets/{path}.svg' alt='Query Plan'>" # Generate the image tag
    #     html += "</div>" # Close the container
    # else:
    #     html = "<p>No query plan available.</p>"

    # print(html)
    return jsonify({'chartData': data,'chart_options': options, 'data':query_plan_data})  # Return JSON data 'query_plan_html': html

@app.route('/show_query')
def show_query():

    import random
    data = {
        'labels': ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        'datasets': [{
            'label': 'Dataset 1',
            'data': [random.randint(0, 30) for _ in range(7)],
            'borderColor': 'rgba(255, 99, 132, 1)',
            'fill': False
        }]
    }

    conn = duckdb.connect()
    query = "EXPLAIN SELECT * FROM range(10)" 
    result = conn.execute(query).fetchall() 
    conn.close()

    plan_str = "\n".join([str(row) for row in result])
    #print(result)
    #print(plan_str)
    return render_template('index.html', plan=result, chart_data=data)

@app.route('/assets/<filename>')
def serve_png(filename):
    print(os.path.join(app.root_path, 'assets',filename))
    return send_from_directory(os.path.join(app.root_path, 'assets'), filename)


@app.route('/query-plan')
def get_query_plan():
    return jsonify(query_plan_data2)



@socketio.on('execute_query')
def execute_query(query):
    query_plan = {
    "name": "Query Root",
    "children": [
        {
            "name": "Join Tables (Table1 and Table2)",
            "execution_time": 2,
            "children": [
                {
                    "name": "Scan and Filter Table1",
                    "execution_time": 1.5,
                },
                {
                    "name": "Scan and Filter Table2",
                    "execution_time": 1.5,
                }
            ]
        }
    ]
}

    #Simulate execution times
    def simulate_execution(node, depth=0):
        if "children" in node:
            for child in node["children"]:
                simulate_execution(child, depth + 1)
        node["execution_time"] = random.uniform(0.1, 1.0)  # Simulated time
        time.sleep(node["execution_time"])
        emit('query_plan_update', node)


    def custom_execution_time(node):
        if "Filter" in node["name"]:
            return 4.5  # Filters take 0.5 seconds
        elif "Join" in node["name"]:
            return 2.0  # Joins take 1.0 seconds
        else:
            return 3.8  # Default time for other operations


    def calculate_execution_time_each_operator(node, depth=0, execution_time_func=None):

        if "children" in node:
            for child in node["children"]:
                calculate_execution_time_each_operator(child, depth + 1, execution_time_func)

        # Use the provided function to determine execution time
        if execution_time_func:
            node["execution_time"] = execution_time_func(node)
        else:
            node["execution_time"] = 2  # Default execution time

        time.sleep(node["execution_time"])
        emit('query_plan_update', node)



    #simulate_execution(query_plan)
    calculate_execution_time_each_operator(query_plan,execution_time_func=custom_execution_time)

QUERY_TYPE_TO_GIF = {
    "fullyoblivious": "fullyoblivious.gif",
    "sortingbased": "shrinkwrap.gif",
    "reflex-sequential": "reflex-parallel.gif",
    "reflex-parallel": "reflex-sequential.gif",
    "aggregate-query": "aggregate.gif",
}


@app.route('/backend-endpoint', methods=['POST'])
def generate_query_plan_tree():
    # Parse the JSON request body
    data = request.get_json()
    param1 = data.get('queryname')
    param2 = data.get('querymode')
    print(param2)

    if param1 == 'Threejoin' and param2 == '50':
        return send_from_directory('assets', 'threejoin-6.png', as_attachment=False)
    if param1 == 'Threejoin' and param2 == '75':
        return send_from_directory('assets', 'threejoin-6.png', as_attachment=False)



@app.route('/get-query-plan', methods=['GET'])
def get_animation():
    # Get query_type parameter from the request
    querymode = request.args.get('querymode', default='fullyoblivious')
    print(f'this is querymode:{querymode}')
    
    # Validate query_type
    if querymode not in QUERY_TYPE_TO_GIF:
        return jsonify({
            'error': 'Invalid query type',
            'valid_query_types': list(QUERY_TYPE_TO_GIF.keys())
        }), 400
    
    # Simulate some processing time
    import time
    time.sleep(2)  # Simulate a 2-second delay
    
    # Return JSON response with the appropriate GIF
    return jsonify({
        'title': f'Query Plan for {querymode}',
        'description': f'Here is your optimized query plan for {querymode}...',
        'gif_url': f'/assets/{QUERY_TYPE_TO_GIF[querymode]}',
    })




@app.route('/assets/<path:filename>')
def serve_static(filename):
    return send_from_directory('assets', filename)




@app.route('/return_cmd')
def stream_command_output(query_name,size,execution_mode):

    os.chdir('/home/lgu/mp-spdz-0.3.9/demo/exps')
    file_list = gen_tests(size,size+100,100,f'{query_name}_',execution_mode)
    socketio.emit('output', {'data': f"Generating the tests for {query_name}....\n"})
    #file_list = gen_tests(100,1100,100,'threejoin_reflex_')
    # input size out put size exeuction time of the operator 
    compile_tests(file_list)
    socketio.emit('output', {'data': f"Compling the test, test name: {query_name}....\n"})

    for file in file_list:   
        lines = run_test_return_cmd(file)
        for line in lines.stdout:
            print(line)
            out = beautify_output(query_name,size,line)
            socketio.emit('output', {'data': out})
        lines.wait()


def beautify_output(queryname,inputsize,input_str):


    if queryname == "threejoin":
        if "Running" in input_str:
            return input_str
        if "n is" in input_str:
            return input_str
        # if "original noise" in input_str:
        #     return input_str
        elif "Stopped timer 100" in input_str:
            response = f'''***Filter 1 started***\ninput size N1: {inputsize}\nExecution time: {get_time(input_str)} s\noutput size Filtered N1: {int(inputsize)}\n'''
            return response
        elif "Stopped timer 200" in input_str:
            response = f'''***Filter 2*** started***\ninput size N2: {inputsize}\nExecution time: {get_time(input_str)} s\noutput size Filtered N2: {int(inputsize)}\n'''
            return response
        elif "Stopped timer 300" in input_str:
            response = f'''***First Join + Parallel Resizer started***\ninput size N1*N2: {int(inputsize*inputsize)}\nExecution time: {get_time(input_str)} s\noutput size S1: {int(inputsize*inputsize*0.2)}\n'''
            return response
        elif "Stopped timer 400" in input_str:
            response = f'''***Second Join + Parallel Resizer started***\ninput size S1*N3: {int(inputsize*inputsize*0.2*inputsize)}\nExecution time: {get_time(input_str)} s\noutput size S2: {int(inputsize*inputsize*0.2*inputsize*0.2)}\n'''
            return response
        elif "Stopped timer 500" in input_str:
            response = f'''***Third Join + Parallel Resizer started***\ninput size S2*N3: {int(inputsize*inputsize*0.2*inputsize*0.2)}\nExecution time: {get_time(input_str)} s\noutput size S2*N3: {int(inputsize*inputsize*0.2*inputsize*0.2*inputsize)}\n'''
            return response
        elif "Time =" in input_str:
            response = f'''####### Whole Query takes: {get_time(input_str)} s\n'''
            #response = 'Execute the query over secret-shares...'
            return response
        else:
            return ""
        
def get_time(inputstr):
    pattern = r'(\d+\.\d+)\s*'
    time = re.findall(pattern, inputstr)
    print(time)
    return time[0]



@socketio.on('start')
def handle_start(data):
    #print(data)
    query = data['query_name']
    #print(query)
    size = data['datasize']
    #print(f'query and size are:{size}')
    execution_mode = ''
    print(f"xxxxxxxxxx{ data['execution_mode']}")
    if data['execution_mode'] == '0':
        execution_mode = "Fully_Oblivious"
    elif data['execution_mode'] == '25':
        execution_mode = "Sorting_based"
    elif data['execution_mode'] == '50':
        execution_mode = "Reflex_sequential"
    elif data['execution_mode'] == '75':
        execution_mode = "Reflex_parallel"
    elif data['execution_mode'] == '100':
        execution_mode = "Fully_Revealed"

    threading.Thread(target=stream_command_output, args=(query,size,execution_mode)).start()

if __name__ == '__main__':
    socketio.run(app,debug=True,host="0.0.0.0")