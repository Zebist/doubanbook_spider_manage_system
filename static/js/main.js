var API_URL = '/api/';
var DOUBAN_BOOK_URL = API_URL + 'douban_books/';
//var MEDIA_PATH = '/media/images/douban_books/';

$(function () {
    var $table = $("#data_table");  // 获取表格
    var $table_ob = get_field_list($table);  // 获取接口提供的字段
    // 监听编辑按钮点击事件
    $table.on("click",".edit-btn", function(event){
        event.preventDefault();
        handle_edit($(this));
    });
    // 监听保存按钮点击事件
    $("#save").on("click", function(event){
        add_record();
    });
    $('#addForm').on('submit', function(event) {
        event.preventDefault(); // 阻止表单的默认提交行为
    });
});

function get_tip_message(msg_list) {
// 获取提示信息
    let tip_message = ''
    $.each(msg_list, function(key, value) {
        tip_message += value + '\n';
    });
    return tip_message
}

function create_post_params() {
// 构造POST请求参数
    var author = $("#author").val();
    var publisher = $("#publisher").val();
    var publish_date = $("#publish_date").val();
    var price = $("#price").val();

    var form_data = new FormData();
    var files = $("#cover_path").prop("files");
    var file = files.length > 0 ? files[0] : null;
    console.log(file);
    form_data.append('title', $("#title").val());
    form_data.append('title_2', $("#title_2").val());
    form_data.append('douban_id', $("#douban_id").val());
    form_data.append('cover_path', file);
    form_data.append('book_url', $("#book_url").val());
    form_data.append('base_info', [author, publisher, publish_date, price].join("/"));
    form_data.append('author', $("#author").val());
    form_data.append('publisher', $("#publisher").val());
    form_data.append('publish_date', $("#publish_date").val());
    form_data.append('price', $("#price").val());
    form_data.append('rating', $("#rating").val());
    form_data.append('review_count', $("#review_count").val());
    form_data.append('summary', $("#summary").val());
    form_data.append('is_readability', $("#is_readability").val());
    return form_data
}

function add_record() {
// 向服务器发起POST请求，添加记录
    $.ajax({
      url: DOUBAN_BOOK_URL, // 替换为你的API端点URL
      type: 'POST', // 请求类型为POST
      data: create_post_params(),
      processData: false,
      contentType: false,
      success: function (data, textStatus, jqXHR) {
        // 请求成功时的处理逻辑
        if (jqXHR.status == 201)
            alert('提交成功');
        else
            alert(get_tip_message(data));
      },
      error: function (xhr, status, error) {
        // 异常时的处理逻辑
        alert('服务异常，请稍候再试！');
        console.error('异常：', error);
      }
    });
}

// 图片字段处理
function handle_img_field(ob) {
    ob.render = function(data, type, row) {
//        console.log(row);
        // 按数据类型返回不同的内容
        if (type === "display") {
            // 在显示模式下，返回包含图像的<img>标签
//            console.log(MEDIA_PATH, data);
            return '<a target="_blank" href=' + row['book_url'] + '><img src="' + data + '" width="100" height="130"></a>';
        }
        // 其他模式返回原始数据
        return data;
    }
}
// 处理可试读字段
function handle_is_readability(ob) {
    ob.render = function(data, type, row) {
        if (type == "display") {
            return data ? "是" : "否"
        }
        return data;
    }
}
// 处理书本链接字段
function handle_book_url(ob) {
    ob.render = function(data, type, row) {
        // 按数据类型返回不同的内容
        if (type === "display") {
            // 在显示模式下，返回<a>标签
            return '<a href='+ data +'>' + data + '</a>';
        }
        // 其他模式返回原始数据
        return data;
    }
}
// 处理标题字段
function handle_title(ob) {
    ob.render = function(data, type, row) {
//        console.log(row);
        // 按数据类型返回不同的内容
        if (type === "display") {
            // 将标题放进a标签
            return '<a target="_blank" href=' + row['book_url'] + '>' + data + '</a>';
        }
        // 其他模式返回原始数据
        return data;
    }
}

// 获取字段列表
function get_field_list($table) {
    $.ajax({
        "url": DOUBAN_BOOK_URL,
        "type": "OPTIONS",
        "error": function(xhr, status, error) {
            // 错误处理
            console.error("请求失败：" + error);
        },
        "success": function (response) {
            var field_list = [];

            // 更新 field_list
            $.each(response["actions"]["POST"], function(name, value) {
                let ob = {
                    "data": name,
                    "title": value["label"]
                }
                if (name == "cover_path") {
                    handle_img_field(ob);  // 图片字段处理
                } else if (name == "is_readability") {
                    handle_is_readability(ob);  // 可试读字段处理
                } else if (name == "title") {
                    handle_title(ob);  // 标题字段处理
                }
//                else if (name == "book_url") {
//                    handle_book_url(ob);  // 书本链接字段处理
//                }
                field_list.push(ob);
            });
            init_fields($table, field_list);  // 将字段更新到表中
        }
    });
}

function create_req_params(data) {
// 封装请求参数
    // 提取排序字段
    order = data.order[0].dir=="asc" ? data.columns[data.order[0].column].data : "-" + data.columns[data.order[0].column].data
    return {
        "size": data.length,// 页面显示记录条数
        "page": (data.start / data.length) + 1,  // 当前页码
        "ordering": order,  // 排序字段
        "search": data.search.value,  // 搜索字段
    };
}

function update_table($table, field_list, data) {
//更新表格
    var default_list = [
       { "data": null, "title":"操作","defaultContent": "<button class='btn edit-btn btn-info' type='button'>编辑</button>"},
       { "data": null, "title":"操作","defaultContent": "<button class='btn edit-btn btn-danger' type='button'>删除</button>"}
    ]  // 默认按钮字段

    $table.DataTable({
        ajax: function (data, callback, settings) {
            //封装请求参数
            param = create_req_params(data);
            console.log(data);
            //请求数据
            $.ajax({
                type: "GET",
                url: DOUBAN_BOOK_URL,  // API地址
                cache: false,  //禁用缓存
                data: param,  //传入组装的参数
                dataType: "json",
                success: function (result) {
                    //封装返回数据
                    var returnData = {};
                    returnData.draw = data.draw;  // 这里直接自行返回了draw计数器,应该由后台返回
                    returnData.recordsTotal = result.count;  // 返回数据全部记录
                    returnData.recordsFiltered = result.count;
                    returnData.data = result.results;  // 返回的数据列表
                    //调用DataTables提供的callback方法，代表数据已封装完成并传回DataTables进行渲染
                    //此时的数据需确保正确无误，异常判断应在执行此回调前自行处理完毕
                    callback(returnData);
                },
                error: function(xhr, status, error) {
                    // 处理错误情况
                    console.error("请求失败：" + error);
                }
            });
        },
        order: [
            [2, 'asc'] // 第3列ID（索引为2）升序排序
        ],
        responsive: true, // 启用响应式选项
        pagingType: "full_numbers", // 分页样式
        ordering: true, // 启用排序
        info: true, // 显示信息
        searching: true, // 启用搜索,
        columns: [...default_list, ...field_list],  // 字段列
        scrollCollapse: true,  // 滚动折叠
        scrollX: true,  // 水平滚动
        fixedHeader: {  // 固定表头
            headerOffset: 240
        },
        fixedColumns: {
            left: 4,  // 左侧固定4列
        },
        paging: true, // 启用分页
        pageLength: 10, // 每页显示的行数
        serverSide: true, // 启用服务器端分页
        bPaginate: true, // 是否显示分页器
        columnDefs: [
            {
                targets: [2], // ID列设置
                visible: false, // 不在表格中显示
                searchable: false // 不可搜索
            },
            {
                targets: [8], // 书籍链接列设置
                visible: false, // 不在表格中显示
                searchable: false // 不可搜索
            },
            {
                targets: [3], // 豆瓣ID列设置
                visible: false, // 不在表格中显示
                searchable: false // 不可搜索
            },
        ]
    });
}

function init_fields($table, field_list) {
// 初始化字段
    return update_table($table, field_list, []);
}

function handle_edit(node) {
    // 处理编辑
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
function handle_save2(node, $table_ob) {
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
    node.html("编辑");
    node.toggleClass("edit-btn");
    node.toggleClass("save-btn");
}