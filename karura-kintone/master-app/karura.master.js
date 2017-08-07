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
        record.field_settings.value = []  // todo: do not clear if same app, existing setting

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
                record.field_settings.value.push(newRow);
            }

            //set app name
            kintone.api("/k/v1/app", "GET", {"id": app_id}).then(function(resp){
                record.app_name.value = resp.name;
                kintone.app.record.set({record: record});
            });

        })
    }

    _karura.begin_train = function(app_id, record){
        var view = record.view.value;
        var payload = {"app_id": app_id, "fields": {}, "view": view};
        var table = record.field_settings.value;
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
            kintone.proxy(Karura.KARURA_HOST + "/train", "POST", {"Origin": location.origin}, payload).then(function(args){
                var body = args[0];
                var result = {};
                try {
                    result = JSON.parse(body)
                } catch (e) {
                    Karura.show_notification("学習中に時間がかかりすぎてしまいました。対象データ、また予測に使う項目を減らしてみてください。", true);
                }
                if("error" in result){
                    Karura.show_notification("学習中にエラーが発生しました。詳細は、コンソールを参照してください。", true);
                    console.log(result["error"]);
                }else{
                    Karura.show_result(result, record);
                    Karura.show_notification("学習が完了しました！", false);
                }
            });
        }else{
            Karura.show_notification("少なくとも一つの予測に使用するフィールド、予測するフィールが必要です", true);
        }

    }

    _karura.download = function(app_id, record){
        var view = record.view.value;
        var payload = {"app_id": app_id, "fields": {}, "view": view};

        kintone.proxy(Karura.KARURA_HOST + "/download", "POST", {"Origin": location.origin}, payload).then(function(args){
            var content = args[0];
            var status = args[1];
            var header = args[2];

            if(status == 200){
                var fileName = "download.csv";
                var disposition = header["Content-Disposition"];
                if(disposition && disposition.indexOf("attachment") !== -1) {
                    var fileNameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                    var matches = fileNameRegex.exec(disposition);
                    if (matches != null && matches[1]) fileName = matches[1].replace(/['"]/g, "");
                }
                var link = document.createElement("a");
                link.setAttribute("download", fileName);
                var blob = new Blob([content], {type: header["Content-Type"]});
                link.href = window.URL.createObjectURL(blob);
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }else{
                Karura.show_notification("ダウンロード処理でエラーが発生しました", true);
                console.log(content);
            }

        });
    }
    
    _karura.upload = function(app_id, file, record){
        var payload = {
            "format": "RAW",
            "value": file
        }
        Karura.show_notification("ファイルから学習を開始しました．．．");
        kintone.proxy.upload(Karura.KARURA_HOST + "/upload?app_id=" + app_id, "POST", {"Origin": location.origin}, payload).then(function(args){
            var body = args[0];
            var result = {};
            try {
                result = JSON.parse(body)
            } catch (e) {
                Karura.show_notification("学習中に時間がかかりすぎてしまいました。対象データ、また予測に使う項目を減らしてみてください。", true);
            }
            if("error" in result){
                Karura.show_notification("学習中にエラーが発生しました。詳細は、コンソールを参照してください。", true);
                console.log(result["error"]);
            }else{
                Karura.show_result(result, record);
                Karura.show_notification("学習が完了しました！", false);
            }
        });
    }

    _karura.show_result = function(result, record){
        var score = result["score"];
        score = Math.round(score * 1000) / 1000;
        var messages = result["messages"];
        record.message_table.value = []
        record.accuracy.value = score;

        for(var i = 0; i < messages.length; i++){
            var m = messages[i];
            var newRow = {
                value: {
                    "message_code":{
                        type: "DROP_DOWN",
                        value: m.error == 1 ? "エラー" : "作業記録"
                    },
                    "message":{
                        type: "SINGLE_LINE_TEXT",
                        value: m.message
                    }
                }
            }
            record.message_table.value.push(newRow);
        }
        record.image_cache.value = result.image;
        kintone.app.record.set({record: record});
        Karura.show_image(result.image);
    }

    _karura.show_image = function(imageStr){
        var canvas = document.createElement("canvas");
        canvas.width = 1600;
        canvas.height = 700;

        var ctx = canvas.getContext("2d");
        var image = new Image();
        image.onload = function() {
            ctx.drawImage(image, 0, 0);
        }
        image.src = "data:image/png;base64," + imageStr;
        var resultArea = kintone.app.record.getSpaceElement("result");
        while (resultArea.firstChild) {
            resultArea.removeChild(resultArea.firstChild);
        }
        resultArea.appendChild(canvas);
    }

    return _karura

})();

var KaruraElement = (function(){
    _karuraElement = {}
    _karuraElement.showImage = function(event){
        //show image
        var imageCache = event.record.image_cache.value;
        if(imageCache){
            Karura.show_image(imageCache)
        }
    }

    _karuraElement.addButton = function(buttonId, title, callback, inline){
        var button = document.createElement("button");
        button.id = buttonId;
        button.innerHTML = title;
        button.className = "btn-karura";
        if(inline){
            button.className += " btn-inline";
        }
        button.onclick = callback;
        kintone.app.record.getSpaceElement(buttonId).appendChild(button);
    }

    _karuraElement.addDownloadButton = function(event){
        KaruraElement.addButton("exe_download", "予測データのダウンロード", function(){
            var record = event ? event.record : kintone.app.record.get()["record"];
            var app_id = record["app_id"]["value"];
            var image_cache = record["image_cache"]["value"];
            if(app_id && image_cache){
                Karura.download(app_id, record);
            }else{
                if(!app_id){
                    Karura.show_notification("アプリ番号がまだ入力されていません", true);
                }else{
                    Karura.show_notification("モデルがまだ作成されていません", true);
                }
            }
        }, true)
    }

    return _karuraElement;
})();

(function(){

    kintone.events.on(["app.record.edit.show", "app.record.create.show"], function(event){
        KaruraElement.addButton("read_fields", "アプリ情報の読み込み", function(){
            var record = kintone.app.record.get();
            var app_id = record["record"]["app_id"]["value"];
            if(app_id){
                Karura.read_fields(app_id, record.record);
            }else{
                Karura.show_notification("アプリ番号がまだ入力されていません", true);
            }
        }, true)

        KaruraElement.addButton("begin_train", "学習を開始する", function(){
            var record = kintone.app.record.get();
            var app_id = record["record"]["app_id"]["value"];
            if(app_id){
                Karura.begin_train(app_id, record.record);
            }else{
                Karura.show_notification("アプリ番号がまだ入力されていません", true);
            }
        })
        
        //add file upload field
        var uploadArea = document.createElement("div");
        uploadArea.id = "karura-upload"
        var fileSelection = document.createElement("label");
        var fileUpload = document.createElement("button");
        fileSelection.innerHTML = "<input id='fileSelection' type='file' />"
        fileUpload.id = "fileUpload"
        fileUpload.innerHTML = "ファイルから学習を開始";
        fileUpload.className = "btn-karura";
        fileUpload.onclick = function(){
            var record = kintone.app.record.get();
            var app_id = record["record"]["app_id"]["value"];
            if(app_id){
                var selected = document.getElementById("fileSelection");
                if(selected.files.length > 0){
                    var file = selected.files[0];
                    Karura.upload(app_id, file, record.record);
                }else{
                    Karura.show_notification("ファイルが選択されていません", true);
                }
            }else{
                Karura.show_notification("アプリ番号がまだ入力されていません", true);
            }
        };
        uploadArea.appendChild(fileSelection);
        uploadArea.appendChild(fileUpload);
        kintone.app.record.getSpaceElement("train_by_file").appendChild(uploadArea);

        //set download button
        KaruraElement.addDownloadButton(event);
        KaruraElement.showImage(event);

    });

    kintone.events.on(["app.record.detail.show"], function(event){
        KaruraElement.addDownloadButton(event);
        KaruraElement.showImage(event);
    });

})();