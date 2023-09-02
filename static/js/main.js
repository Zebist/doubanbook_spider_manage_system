
$(function () {
    var $table = $("#data_table");  // 获取表格    
    var data = [
         {
             "name": "Tiger Nixon",
             "position": "System Architect",
             "salary": "18000"
         }
     ];
    var $table_ob = $table.DataTable({
        data: data,
       "columns": [
           { "data": "name", "title":"序号","defaultContent":""},
           { "data": "position", "title":"用户名","defaultContent":""},
           { "data": "salary", "title":"姓名","defaultContent":""},
           { "data": null, "title":"操作","defaultContent": "<button class='edit-btn' type='button'>编辑</button>"},
           { "data": null, "title":"操作","defaultContent": "<button class='edit-btn' type='button'>删除</button>"}
       ],
    });
    // 监听编辑按钮点击事件
    $table.find("tbody").on("click",".edit-btn",function(){
        handle_edit($(this));
    });
    // 监听保存按钮点击事件
    $table.find("tbody").on("click",".save-btn",function(){
        handle_save($(this), $table_ob);
    });

});// 处理编辑
function handle_edit(node) {
    var tds = node.parents("tr").children();
    // 遍历本行所有列
    $.each(tds, function(i,val){
        var jqob = $(val);
        if(i < 1 || jqob.has('button').length ){return true;}  // 跳过第1项 和 按钮
        var txt = jqob.text();
        var put = $("<input type='text'>");
        put.val(txt);
        jqob.html(put);  // 放入input框
    });
    node.html("保存");  // 更改当前按钮为保存
    // 切换样式s
    node.toggleClass("edit-btn");
    node.toggleClass("save-btn");
}

// 处理保存
function handle_save(node, $table_ob) {
    alert("保存成功");
    var row = $table_ob.row(node.parents("tr"));
    var tds = node.parents("tr").children();
    $.each(tds, function(i,val){
        var jqob=$(val);
        //把input变为字符串
        if(!jqob.has('button').length) {
            var txt = jqob.children("input").val();
            jqob.html(txt);
            $table_ob.cell(jqob).data(txt);  // 修改DataTables对象的数据
        }
    });
    // var data=row.data();
    // $.ajax({
    //     "url":"/example/resources/user_share/inline_edit_no_plugin/edit.php",
    //     "data":data,
    //     "type":"post",
    //     "error":function(){
    //         alert("服务器未正常响应，请重试");
    //     },
    //     "success":function(response){
    //         alert(response);
    //     }
    // });
    node.html("编辑");
    node.toggleClass("edit-btn");
    node.toggleClass("save-btn");
}