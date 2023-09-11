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
        >
        <template #operate="{ row }">
            <template v-if="$refs.xGrid.isActiveByRow(row)">
              <el-button type="success" @click="saveRowEvent(row)">保存</el-button>
            </template>
            <template v-else>
              <el-button type="primary" @click="editRowEvent(row)">编辑</el-button>
            </template>
            <el-button type="danger" @click="removeRowEvent(row)">删除</el-button>
          </template>
        </vxe-grid>

    </div>
</template>
  
<script>
import VXETable from 'vxe-table'
VXETable.renderer.add('renderCoverPath', {
    // 渲染封面
    renderDefault (h, renderOpts, params) {
        let { row, column } = params;
        // let { events } = renderOpts
        return <a class="my-link" href={row['book_url']} target='_blank'>
            <img src={row[column.field]} />
        </a>
    }
})
export default {
    data () {
        return {
            default_timezone: "Asia/Shanghai",  // 默认时间戳
            formData: {
                searchContent: ''
            },
            seqColumn: [],
            gridOptions: {
                border: true,
                resizable: true,
                align: 'left',
                loading: false,
                keepSource: true,
                showOverflow: true,
                sortConfig: {
                  trigger: 'cell',
                  remote: true
                },
                pagerConfig: {
                    total: 0,
                    currentPage: 1,
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
                    icon: 'vxe-icon-question-circle-fill'
                },
                columns: [{ title: '操作', width: 180, slots: { default: 'operate' } }],
                data: [],
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
        this.refreshField();
        // this.fetchData();
    },
    methods: {
        getCellRender(key) {
            // 获取数据的方法，可以发起服务端请求
            if (key == 'cover_path') {
                // 处理字段render
                return {'name': 'renderCoverPath'};
            }
            return {};
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
            var user_timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || this.default_timezone;
            var utc_time = new Date(data.cellValue);
            var user_time = new Date(utc_time.toLocaleString("en-US", { timeZone: user_timezone }));
            var formatted_user_time = user_time.toLocaleString(undefined, { timeZone: user_timezone });

            return formatted_user_time;
        },
        handleColumns(response) {
            // 处理字段，生成字段信息info
            let columns = [];
            let columns_ob = response.data.actions.POST;
            const no_show_fileds = ['id', 'douban_id'];
            for (const key in columns_ob) {
                if (no_show_fileds.indexOf(key) == -1 ) {
                    let info = {
                        'field': key,
                        'title': columns_ob[key].label,
                        'cellRender': this.getCellRender(key),
                        'editRender': {},
                        'formatter': this.getFormatter(key),
                        'sortable': true,
                    };
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
            const formattedFields = sorts.map(obj => (obj.order === 'desc' ? `-${obj.field}` : obj.field));
            // 使用 join 方法将字段拼接成逗号分隔的字符串
            return formattedFields.join(',');
        },
        fetchData(page, sorts) {
            // 发起服务端请求，获取数据
            return this.$axios.get("api/douban_books/", {
                'params': {
                    page: page.currentPage,
                    size: page.pageSize,
                    ordering: this.getOrdering(sorts),
                    search: this.formData.searchContent,
                }
            })
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
        editRowEvent (row) {
            // 单击编辑按钮
            const $grid = this.$refs.xGrid;
            $grid.setActiveRow(row);
        },
        saveRowEvent () {
            // 单击保存按钮
            const $grid = this.$refs.xGrid;
            $grid.clearActived().then(() => {
                this.gridOptions.loading = true;
                setTimeout(() => {
                        this.gridOptions.loading = false;
                        VXETable.modal.message({ content: '保存成功！', status: 'success' });
                    }, 300)
                });
        },
        async removeRowEvent (row) {
            // 单击删除按钮
            const type = await VXETable.modal.confirm('您确定要删除该数据?');
            const $grid = this.$refs.xGrid;
            if (type === 'confirm') {
                $grid.remove(row);
            }
        }
    }
}
</script>
<style scoped>
</style>