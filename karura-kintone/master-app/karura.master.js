/*
 * karura.master.js
 * JavaScript customize for Karura Master Application
 * Licensed under the MIT License
 */

 var Karura = (function() {
    "use strict";

    var _karura = {
        "KARURA_HOST": "https://karura-server.herokuapp.com"
    }

    _karura.show_notification = function(message, isError){
        var el_notification = kintone.app.record.getSpaceElement("notification");
        var el_msg = document.createElement("span");
        el_msg.innerHTML = message;
        el_msg.className = "label-karura";
        if(isError !== undefined){
            el_msg.className += (isError ? " type-error" : " type-success");
        }
        while (el_notification.firstChild) {
            el_notification.removeChild(el_notification.firstChild);
        }
        el_notification.appendChild(el_msg);
    }

    _karura.read_fields = function(app_id, record){
        var registered_code = [];
        var ignores = ["CREATED_TIME", "CREATOR", "RECORD_NUMBER", "SPACER", "STATUS_ASSIGNEE", "MODIFIER", "UPDATED_TIME", "STATUS", "CATEGORY"];
        record.record.field_settings.value = []  // todo: do not clear if same app, existing setting

        kintone.api("/k/v1/app/form/fields", "GET", {"app": app_id}).then(function(resp){
            var forms = resp.properties;
            // search prediction item
            var predict_target = "";
            var ignore_field = []
            for(var f in forms){
                if(f.indexOf("_prediction") > -1){
                    predict_target = f.replace("_prediction", "");
                    ignore_field.push(f);
                }
            }

            // set form
            for(var f in forms){
                if(ignores.indexOf(forms[f].type) > -1 || ignore_field.indexOf(f) > -1){
                    continue;
                }
                var usage = "予測に使わない";
                if(f == predict_target){
                    usage = "予測値";
                }else if(forms[f].type == "NUMBER" || forms[f].type == "DROP_DOWN" || forms[f].type == "RADIO_BUTTON"){
                    usage = "予測に使う";
                }

                var newRow = {
                    value: {
                        "field_name": {
                            type: "SINGLE_LINE_TEXT",
                            value: forms[f].label
                        },
                        "field_code": {
                            type: "SINGLE_LINE_TEXT",
                            value: f
                        },
                        "usage": {
                            type: "DROP_DOWN",
                            value: usage
                        }
                    }
                }
                record.record.field_settings.value.push(newRow);
            }

            //set app name
            kintone.api("/k/v1/app", "GET", {"id": app_id}).then(function(resp){
                record.record.app_name.value = resp.name;
                kintone.app.record.set(record);
            });

        })
    }

    _karura.begin_train = function(app_id, record){
        var view = record.record.view.value;
        var payload = {"app_id": app_id, "fields": {}, "view": view};
        var table = record.record.field_settings.value;
        var usages = ["予測に使う", "予測値"];
        var exist_target = false;
        var exist_feature = false;

        for(var i = 0; i < table.length; i++){
            var code = table[i].value["field_code"].value;
            var usage = table[i].value["usage"].value;
            var usage_id = usages.indexOf(usage);
            if(usage_id == 0){
                exist_feature = true;
            }
            if(usage_id == 1){
                exist_target = true;
            }
            payload.fields[code] = {"usage": usage_id};
        }

        //check
        if(exist_feature && exist_target){
            Karura.show_notification("学習を開始しました．．．");
            kintone.proxy(Karura.KARURA_HOST + "/train", "POST", {}, payload).then(function(args){
                var body = args[0];
                var result = JSON.parse(body)
                Karura.show_result(result, record);
                Karura.show_notification("学習が完了しました！", false);
            });
        }else{
            Karura.show_notification("少なくとも一つの予測に使用するフィールド、予測するフィールが必要です", true);
        }

    }

    _karura.show_result = function(result, record){
        var score = result["score"];
        var order = ["データについて", "予測に使用する項目について", "モデルについて", "システムエラー"];
        var messages = result["messages"];
        record.record.message_table.value = []
        record.record.accuracy.value = score;

        for(var i = 0; i < order.length; i++){
            var aspect = order[i];
            if(!(aspect in messages)){
                continue;
            }
            for(var m = 0; m < messages[aspect].length; m++){
                var newRow = {
                    value: {
                        "aspect":{
                            type: "SINGLE_LINE_TEXT",
                            value: aspect
                        },
                        "evaluation":{
                            type: "DROP_DOWN",
                            value: messages[aspect][m].evaluation
                        },
                        "message":{
                            type: "SINGLE_LINE_TEXT",
                            value: messages[aspect][m].message
                        }
                    }
                }
                record.record.message_table.value.push(newRow);
            }
        }
        kintone.app.record.set(record);

    }

    kintone.events.on(["app.record.edit.show", "app.record.create.show"], function(event){
        //set the form field setup button
        var read_fields = document.createElement("button");
        read_fields.id = "read_fields";
        read_fields.innerHTML = "アプリ情報の読み込み";
        read_fields.className = "btn-karura align-float";
        read_fields.onclick = function(){
            var record = kintone.app.record.get();
            var app_id = record["record"]["app_id"]["value"];
            if(app_id){
                Karura.read_fields(app_id, record);
            }else{
                Karura.show_notification("アプリ番号がまだ入力されていません", true);
            }
        }
        kintone.app.record.getSpaceElement("read_fields").appendChild(read_fields);

        //set the begin training button
        var begin_train = document.createElement("button");
        begin_train.id = "begin_train"
        begin_train.innerHTML = "学習を開始する"
        begin_train.className = "btn-karura";
        begin_train.onclick = function(){
            var record = kintone.app.record.get();
            var app_id = record["record"]["app_id"]["value"];
            if(app_id){
                Karura.begin_train(app_id, record);
            }else{
                Karura.show_notification("アプリ番号がまだ入力されていません", true);
            }
        }
        kintone.app.record.getSpaceElement("train_button").appendChild(begin_train);

    });

    return _karura

})();