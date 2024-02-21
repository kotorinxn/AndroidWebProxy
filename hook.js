
    Java.perform(function(){
    var target = Java.use("okhttp3.Request$Builder");
    console.log("okhttp3.Request$Builder");
    target.url.overload('java.lang.String').implementation = function(url){
        console.log(url);
        send("trigger");
        var op_payload = null;
        var value_payload = null;
        var ret = null;
        const op_listener = recv('op', function(op){
            op_payload = op['payload'];
        });
        op_listener.wait();
        if(op_payload == "forward"){
                ret = target.url.overload('java.lang.String').call(this, url);
        }
        else if(op_payload == "interceptor"){
            const value_listener = recv('value', value => {
                value_payload = value['payload'];
            });
            value_listener.wait();
            console.log("value: " + value_payload);
            ret = target.url.overload('java.lang.String').call(this, value_payload);
        }
        else{
            console.log("error");
        }
        return ret;
        };
    }
    );
    