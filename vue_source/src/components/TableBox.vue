<template>
    <div class="table-box">
        <vxe-toolbar>
            <template #buttons>
                <vxe-input v-model="formData.searchContent" type="search" placeholder="全表搜索" @keyup="searchEvent1"></vxe-input>
            </template>
        </vxe-toolbar>

        <vxe-grid
            ref="xGrid" 
            v-bind="gridOptions"
            :row-config="rowConfig"
            :pager-config="gridOptions.pagerConfig"
            @sort-change="handleSortChange"
            @page-change="handlePageChange"
            @edit-closed="handleEditClose"
            @edit-actived="handleEditActive"
            style="height:67vh;"
        >
        <template #operate="{ row }">
            <template v-if="$refs.xGrid.isActiveByRow(row)">
              <el-button type="success" @click="saveRowEvent(row)">保存</el-button>
            </template>
            <template v-else>
              <el-button type="primary" @click="editRowEvent(row)">编辑</el-button>
            </template>
            <el-button type="danger" @click="removeRowEvent(row)">删除/取消</el-button>
          </template>
          <!-- 封面渲染 -->
          <template #cover_path_default="{ row }">
            <a class="my-link" :href="row.book_url" target="_blank">
                <img class="cover_img" :src="row.cover_path" />
            </a>
          </template>
          <!-- 封面编辑 -->
          <template #cover_path_edit>
            <vxe-input id="cover_path_input" type="file"  @change="handleFileChange($event)" ></vxe-input>
          </template>
          <!-- 标题渲染 -->
          <template #title_default="{ row }">
            <a class="my-link" :href="row.book_url" target="_blank">
                {{ row.title }}
            </a>
          </template>
          <!-- 标题编辑 -->
          <template #title_edit="{ row }">
            <vxe-input type="text" v-model="row.title"></vxe-input>
          </template>
          <!-- DOUBAN ID编辑 -->
          <template #douban_id_edit="{ row }">
            <vxe-input type="text" v-model="row.douban_id"></vxe-input>
          </template>
          <!-- 辅助书名编辑 -->
          <template #title_2_edit="{ row }">
            <vxe-input type="text" v-model="row.title_2"></vxe-input>
          </template>
          <!-- 作者编辑 -->
          <template #author_edit="{ row }">
            <vxe-input type="text" v-model="row.author"></vxe-input>
          </template>
          <!-- 出版商编辑 -->
          <template #publisher_edit="{ row }">
            <vxe-input type="text" v-model="row.publisher"></vxe-input>
          </template>
          <!-- 日期编辑 -->
          <template #publish_date_edit="{ row }">
            <vxe-input type="text" v-model="row.publish_date"></vxe-input>
          </template>
          <!-- 价格编辑 -->
          <template #price_edit="{ row }">
            <vxe-input type="number" v-model="row.price"></vxe-input>
          </template>
          <!-- 评分编辑 -->
          <template #rating_edit="{ row }">
            <vxe-input type="number" min="1" max="10" v-model="row.rating"></vxe-input>
          </template>
          <!-- 评论人数编辑 -->
          <template #review_count_edit="{ row }">
            <vxe-input type="number" v-model="row.review_count"></vxe-input>
          </template>
          <!-- 简介编辑 -->
          <template #summary_edit="{ row }">
            <vxe-input type="text" v-model="row.summary"></vxe-input>
          </template>
        </vxe-grid>

    </div>
</template>
  
<script>
import VXETable from 'vxe-table';
export default {
    data () {
        return {
            default_timezone: "Asia/Shanghai",  // 默认时间戳
            formData: {
                searchContent: ''
            },
            coverPathImage: null,
            refreshDataTimer: null,
            refreshIntervalTime: 10000,  // 定时刷新时间
            seqColumn: [],
            sortInfo: [],
            pageInfo: null,
            rowConfig: {
                height: 100,
            },
            gridOptions: {
                border: true,
                resizable: true,
                align: 'left',
                loading: false,
                keepSource: true,
                showOverflow: true,
                columns: [{ title: '操作', width: 230, slots: { default: 'operate' } }],
                sortConfig: {
                  trigger: 'cell',
                  remote: true
                },
                pagerConfig: {
                    defaultPage: 1,
                    pageSize: 10,
                    pageSizes: [10, 20, 50, 100, 200],  // 留意limitPageSizes函数，超过maxPageSize的会被过滤掉
                    maxPageSize: 10,
                },
                editConfig: {
                    // 设置触发编辑为手动模式
                    trigger: 'manual',
                    // 设置为整行编辑模式
                    mode: 'row',
                    // 显示修改状态和新增状态
                    showStatus: true,
                    // 自定义可编辑列头的图标
                    icon: 'vxe-icon-question-circle-fill',
                },
                toolbarConfig: {
                    buttons: [
                        { code: 'insert_actived', name: '新增', icon: 'vxe-icon-square-plus' }
                    ],
                    zoom: true,
                    custom: true
                },
                proxyConfig: {
                    sort: true, // 启用排序代理，当点击排序时会自动触发 query 行为
                    props: {
                        result: 'data.results',
                        total: 'data.count'
                    },
                    ajax: {
                        query: ({page, sorts}) => {
                            return this.fetchData(page, sorts);
                        }
                    }
                },
            },
        }
    },
    created() {
        // 获取字段
        this.refreshField();
    },
    mounted() {
        // 启动定时刷新
        const $grid = this.$refs.xGrid;
        this.startRefreshInterval($grid);
    },
    methods: {
        getCellRender(key) {
            // 获取数据的方法，可以发起服务端请求
            let renderMap = {
                'cover_path': {  // 封面
                    'default': 'cover_path_default',
                    'edit': 'cover_path_edit',
                },
                'douban_id': {  // DOUBAN ID
                    'edit': 'douban_id_edit',
                },
                'title': {  // 书名
                    'default': 'title_default',
                    'edit': 'title_edit',
                },
                'title_2': {'edit': 'title_2_edit'},  // 辅助书名
                'author': {'edit': 'author_edit'},  // 作者
                'publisher': {'edit': 'publisher_edit'},  // 出版商
                'publish_date': {'edit': 'publish_date_edit'},  // 出版日期
                'price': {'edit': 'price_edit'},  // 价格
                'rating': {'edit': 'rating_edit'},  // 评分
                'review_count': {'edit': 'review_count_edit'},  // 评论人数
                'summary': {'edit': 'summary_edit'}  // 简介
            };
            return renderMap[key] || {};
        },
        getFormatter(key) {
            // 获取格式化信息
            if (key == 'create_date' || key == 'update_date') {
                return this.formatUtcToUserTime;
            }
            return null;
        },
        formatUtcToUserTime (data) {
            // 将UTC时间转为用户时间
            if (data.cellValue) {
                var user_timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || this.default_timezone;
                var utc_time = new Date(data.cellValue);
                var user_time = new Date(utc_time.toLocaleString("en-US", { timeZone: user_timezone }));
                var formatted_user_time = user_time.toLocaleString(undefined, { timeZone: user_timezone });
    
                return formatted_user_time;
            }
        },
        handleColumns(response) {
            // 处理字段，生成字段信息info
            let columns = [];
            let columns_ob = response.data.actions.POST;
            const no_show_fileds = ['id', 'book_url'];
            for (const key in columns_ob) {
                if (no_show_fileds.indexOf(key) == -1 ) {
                    let info = {
                        'field': key,
                        'title': columns_ob[key].label,
                        'slots': this.getCellRender(key),
                        
                        'formatter': this.getFormatter(key),
                        'sortable': true,
                    };
                    if (key != 'create_date' && key != 'update_date') {
                        info['editRender'] = {};
                    }
                    columns.push(info);
                }
            }
            
            return columns;
        },
        refreshField() {
            // 发起服务端请求，获取数据
            this.$axios.options("api/douban_books/")
                .then(response => {
                        // 请求成功处理逻辑
                        let columns = this.handleColumns(response);
                        this.gridOptions.columns = [...this.seqColumn, ...columns, ...this.gridOptions.columns];
                    })
                .catch(error => {
                    // 请求失败处理逻辑
                    console.error(error);
                });
        },
        getOrdering(sorts) {
            if (!sorts) return;
            const formattedFields = sorts.map(obj => (obj.order === 'desc' ? `-${obj.field}` : obj.field));
            // 使用 join 方法将字段拼接成逗号分隔的字符串
            return formattedFields.join(',');
        },
        requestData(page, sorts) {
            // 请求数据
            return this.$axios.get("api/douban_books/", {
                'params': {
                    page: page ? page.currentPage : this.gridOptions.pagerConfig.defaultPage,
                    size: page ? page.pageSize : this.gridOptions.pageSize,
                    ordering: this.getOrdering(sorts),
                    search: this.formData.searchContent,
                }
            })
        },
        fetchData(page, sorts) {
            // 发起服务端请求，获取数据
            return this.requestData(page, sorts)
            .then(response => {
                this.limitPageSizes(response);
                return response;
            })
            .catch(error => {
                console.error(error);
                return error;
            });
        },
        limitPageSizes(response) {
            // 限制每页条目数不超过最大条目数
            let pagerConfig = this.gridOptions.pagerConfig;
            pagerConfig.maxPageSize = response.data.max_size;
            pagerConfig.pageSizes = pagerConfig.pageSizes.filter(item => item <= pagerConfig.maxPageSize);
            return response;
        },
        searchEvent1() {
            // 搜索
            const $grid = this.$refs.xGrid;
            $grid.commitProxy('query');
        },
        handleEditActive(){
            // 编辑时暂停刷新定时器
            this.stopRefreshInterval();
        },
        handleEditClose({$grid}) {
            // 编辑结束时重启刷新定时器
            this.stopRefreshInterval();
            this.startRefreshInterval($grid);
        },
        editRowEvent (row) {
            // 单击编辑按钮
            const $grid = this.$refs.xGrid;
            $grid.setActiveRow(row);
        },
        getFormData(row) {
            // 构造并返回FormData
            let formData = new FormData();
            for (const key in row) {
                let res = row[key];
                if (key == 'cover_path') {
                    res = this.coverPathImage;
                    if (!res)  // 结果不存在不进行添加
                        continue;
                } else if (res === null) {
                    continue;
                }
                formData.append(key, res);
            }
            return formData;
        },
        handleSaveError(error) {
            // 处理保存异常
            let response = error.response;
            this.gridOptions.loading = false;
            if (response.status == 400) {
                this.handleTipMessage(response.data);
            } else {
                VXETable.modal.message({ content: '保存出错，请稍候再试！', status: 'error' });
                console.error(error);
            }

        },
        updateRow (row, formData) {
            this.$axios.put("api/douban_books/" + row.id + "/", formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data' // 设置请求头为 multipart/form-data
                    }
                })
                .then((response) => {
                        // 请求成功处理逻辑
                        VXETable.modal.message({ content: '保存成功！', status: 'success' });
                        this.gridOptions.loading = false;
                        row.cover_path = response.data.cover_path;  // 更新图片
                    })
                .catch(error => {
                    // 请求失败处理逻辑
                    this.handleSaveError(error);
                });
        },
        createRow (row, formData, $grid) {
            this.$axios.post("api/douban_books/", formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data' // 设置请求头为 multipart/form-data
                    }
                })
                .then((response) => {
                        // 请求成功处理逻辑
                        VXETable.modal.message({ content: '保存成功！', status: 'success' });
                        this.gridOptions.loading = false;
                        row.cover_path = response.data.cover_path;  // 更新图片
                        this.refreshData($grid);
                    })
                .catch(error => {
                    // 请求失败处理逻辑
                    this.handleSaveError(error);
                    $grid.remove(row);
                });
        },
        saveRowEvent (row) {
            // 单击保存按钮
            const $grid = this.$refs.xGrid;
            const formData = this.getFormData(row);
            $grid.clearActived().then(() => {
                this.gridOptions.loading = true;
                if (row.id) {  // 有id,更新行
                    this.updateRow(row, formData);
                } else {  // 没有id,创建行
                    this.createRow(row, formData, $grid);
                }
            });
        },
        async removeRowEvent (row) {
            // 单击删除/取消按钮
            const $grid = this.$refs.xGrid;
            // 重启定时器
            if (row.id) {  // 有id才是删除
                const type = await VXETable.modal.confirm('您确定要删除该数据?');
                if (type === 'confirm') {
                    $grid.remove(row);
                    console.log($grid);
                    this.gridOptions.loading = true;
                    this.$axios.delete("api/douban_books/" + row.id + "/")
                    .then(() => {
                            // 请求成功处理逻辑
                            this.gridOptions.loading = false;
                            this.refreshData($grid);
                            VXETable.modal.message({ content: '删除成功！', status: 'success' });
                        })
                    .catch(error => {
                        // 请求失败处理逻辑
                        this.gridOptions.loading = false;
                        VXETable.modal.message({ content: '删除出错，请稍候再试！', status: 'error' });
                        console.error(error);
                    });
                }
            } else {  // 没有id是取消,删除行即可
                $grid.remove(row);
            }
        },
        getTipMessage(msg) {
            // 获取提示信息
            let errorMessage = "保存失败!\r\n";
            if (typeof msg === "string") {
                errorMessage = msg;
            } else {
                for (const key in msg) {
                    errorMessage += key + ": " + msg[key].join(", ") + "\r\n";
                }
            }
            return errorMessage;
        },
        handleTipMessage(data) {
            // 处理提示信息
            if(data.code == "error") {
                const message = this.getTipMessage(data.errors || data.error);
                VXETable.modal.message({ content: message, status: 'error' });
            } else {
                VXETable.modal.message({ content: '删除出错，请稍候再试！', status: 'error' });
                console.error(data);
            }
        },
        handleFileChange(e) {
            // 处理选择图片
            const coverPathImage = e.$event.target.files[0]; // 获取选择的文件
                if (coverPathImage) {
                    // 在这里处理选定的文件
                    this.coverPathImage = coverPathImage;
                }
        },
        resetRequestInfo(){
            // 重置信息
            this.pageInfo = null;
        },
        refreshData($grid) {
            // 刷新数据
            this.requestData(this.pageInfo, this.sortInfo).then(response => {
                $grid.loadData(response.data.results);
                $grid.tablePage.total = response.data.count;
            })
            .catch(error => {
                if (error.response && error.response.status == 404) {
                    // 404说明未查到数据，可能是数据清空的情况，重置信息
                    this.resetRequestInfo();
                    // 同时重新获取数据
                    $grid.commitProxy('query');
                }
                console.error(error);
            });
        },
        handleSortChange(sortInfo) {
            this.sortInfo = sortInfo.sortList;
        },
        handlePageChange(pageInfo) {
            this.pageInfo = pageInfo;
        },
        startRefreshInterval($grid) {
            // 设置定时器，定期刷新数据
            this.refreshDataTimer = setInterval(() => {
                this.refreshData($grid);
            }, this.refreshIntervalTime);
        },
        stopRefreshInterval() {
        // 停止定时器
            clearInterval(this.refreshDataTimer);
        },
        beforeDestroy() {
            // 在组件销毁之前，停止定时刷新
            this.stopRefreshInterval();
        },
    }
}
</script>
<style scoped>
/* 链接 */
.my-link {
    text-decoration: none;
    color: #409EFF;
    font-weight: bold;
}
/* 封面图片 */
.cover_img {
    width: 100%;
    height: 100%;
}
</style>