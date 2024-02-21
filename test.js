/// <reference path="frida-gum.d.ts" />

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