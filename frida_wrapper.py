import time
import frida
import sys
import os
import json




def interactive():
    print("1.forward\n2.interceptor")
    op = input("op:")
    if(op == "1"):
        script.post({"type":"op", "payload":"forward"})
    elif(op == "2"):
        script.post({"type":"op", "payload":"interceptor"})
        new_url = input("input new url:\n")
        script.post({"type":"value", "payload":new_url})
    else:
        pass
    pass

def on_message(message, data):
    if message['type'] == 'send':
        print("[*] {0}".format(message['payload']))
        if(message['payload'] == 'trigger'):
            interactive()
    else:
        print(message)


def ret_json(json_path):
    json = ""
    with open(json_path, "r") as f:
        json = f.read()
    return json


def generate_hook_js(js_path, json):
    jscode = '''
    Java.perform(function(){{
    var target = Java.use(\"{component_name}\");
    console.log(\"{component_name}\");
    target.{func_name}.overload({args_fmt}).implementation = function({args_name}){{
        console.log({args_name});
        send("trigger");
        var op_payload = null;
        var value_payload = null;
        var ret = null;
        const op_listener = recv('op', function(op){{
            op_payload = op['payload'];
        }});
        op_listener.wait();
        if(op_payload == "forward"){{
                ret = target.{func_name}.overload({args_fmt}).call(this, {args_name});
        }}
        else if(op_payload == "interceptor"){{
            const value_listener = recv('value', value => {{
                value_payload = value['payload'];
            }});
            value_listener.wait();
            console.log("value: " + value_payload);
            ret = target.{func_name}.overload({args_fmt}).call(this, value_payload);
        }}
        else{{
            console.log("error");
        }}
        return ret;
        }};
    }}
    );
    '''
    with open(js_path, "w") as f:
        for data in json['web_api']:
            f.write(jscode.format(component_name=data['component_name'],
                                  func_name=data['func_name'], args_fmt=data['args_fmt'], args_name=data['args_name']))


def run(json_path, js_path, package_name):
    global script
    api_json = json.loads(ret_json(json_path))
    generate_hook_js(js_path, api_json)
    jscode = ""
    with open(js_path, "r") as f:
        jscode = f.read()

    devices = frida.get_usb_device()
    pid = devices.spawn(package_name)
    # devices.resume(pid)
    process = devices.attach(pid)
    script = process.create_script(jscode)
    script.on('message', on_message)
    print('[*] Running')
    script.load()
    # time.sleep()
    devices.resume(pid)
    # os.system("pause")
    # print("unpause in py")
    # script.post({"type" : "unpause"})
    # sys.stdin.read()
    while(1):
        pass


if __name__ == "__main__":
    run("api.json", "hook.js", "org.wikipedia")
