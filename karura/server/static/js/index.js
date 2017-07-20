var instance = new Vue({
    el: "#app",
    delimiters: ["[[", "]]"],
    data: {
        selected: "login"
    },
    methods: {
        isActive: function(kind){
            return kind == this.selected ? "is-active" : "";
        },
        activate: function(kind){
            return this.selected = kind;
        }
    }
})