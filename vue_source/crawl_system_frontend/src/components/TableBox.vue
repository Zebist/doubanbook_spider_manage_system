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
        </vxe-grid>
         <!-- 分页 -->
        <!-- <vxe-pager 
            :total="total" 
            :currentPage.sync="currentPage" 
            :pageSize.sync="pageSize"
            :pageSizes="pageSizes"
            @page-change="handlePageChange"
        ></vxe-pager> -->

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
            gridOptions: {
                border: true,
                resizable: true,
                align: 'left',
                columns: [],
                sortConfig: {
                  trigger: 'cell',
                  remote: true
                },
                pagerConfig: {
                    pageSizes: [10, 20, 50, 100, 200],  // 留意limitPageSizes函数，超过maxPageSize的会被过滤掉
                    maxPageSize: 10,
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
    mounted() {
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
            return null;
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
                        this.gridOptions.columns = columns;
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
        }
    }
}
</script>
<style scoped>
</style>