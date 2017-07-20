/*
 * karura.master.js
 * JavaScript customize for Karura Master Application
 * Licensed under the MIT License
 */

(function(){
    "use strict";

    kintone.events.on(["app.record.edit.show", "app.record.create.show"], function(event){
        var KARURA_HOST = "https://karura-server.herokuapp.com";
        var ignores = ["CREATED_TIME", "CREATOR", "RECORD_NUMBER", "SPACER", "STATUS_ASSIGNEE", "MODIFIER", "UPDATED_TIME", "STATUS", "CATEGORY"];

        var messageArea = document.createElement("span");
        messageArea.id = "messageArea";
        var setMessage = function(message, isError){
            var el = document.getElementById("messageArea");
            el.className = "label-prediction ";
            if(isError !== undefined){
                el.className += isError ? "type-error" : "type-success";
            }
            el.innerHTML = message;
        }

        var predictButton = document.createElement("button");
        predictButton.id = "predictButton";
        predictButton.innerHTML = "予測する";
        predictButton.className = "btn-karura-predict"
        predictButton.onclick = function(){
            var url = KARURA_HOST + "/predict";
            var appId = kintone.app.getId();
            var record = kintone.app.record.get();
            var values = {}
            for(var k in record.record){
                if(ignores.indexOf(record.record[k].type) > -1){
                    continue;
                }
                values[k] = record.record[k].value;
            }
            var body = {
                "app_id": appId,
                "values": values
            }
            kintone.proxy(url, "POST", {"Origin": location.origin}, body).then(function(args){
                    var body = args[0];
                    var result = JSON.parse(body);
                    if("prediction" in result){
                        setMessage("予測が完了しました！", false);
                        for(k in record.record){
                            if(k.indexOf("_prediction") > -1){
                                record.record[k].value = result.prediction;
                                break;
                            }
                        }
                    }else{
                        setMessage(result["error"], true);
                    }
                    kintone.app.record.set(record);
                });

        }

        var space = kintone.app.record.getHeaderMenuSpaceElement()
        space.appendChild(predictButton);
        space.appendChild(messageArea);

    })

})();
