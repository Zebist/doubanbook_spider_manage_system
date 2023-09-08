<template>
    <div class="table-box">
        <vxe-toolbar>
        <template #buttons>
            <vxe-button @click="allAlign = 'left'">居左</vxe-button>
            <vxe-button @click="allAlign = 'center'">居中</vxe-button>
            <vxe-button @click="allAlign = 'right'">居右</vxe-button>
        </template>
        </vxe-toolbar>

        <vxe-table
            border
            :align="allAlign"
            :data="tableData"
            :columns="columns"
        >
            <vxe-column
                v-for="column in columns"
                :key="column.field"
                :field="column.field"
                :title="column.title"
                :cell-render="column.cell_render"
                :formatter="column.formatter"
            ></vxe-column>
        </vxe-table>
         <!-- 分页 -->
        <vxe-pager 
            :total="total" 
            :currentPage.sync="currentPage" 
            :pageSize.sync="pageSize"
            :pageSizes="pageSizes"
        ></vxe-pager>

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
            allAlign: 'center',
            columns: [],
            tableData: [],
            total: 0, // 数据总数
            default_timezone: "Asia/Shanghai",  // 默认时间戳
            currentPage: 1, // 当前页码
            pageSize: 10, // 每页显示的记录数
            pageSizes: [10, 20, 50]
        }
    },
    // watch: {
    //     currentPage: 'fetchData', // 当 currentPage 改变时触发 fetchData 方法
    //     pageSize: 'fetchData', // 当 pageSize 改变时触发 fetchData 方法
    // },
    mounted () {
        this.refreshField();
        this.fetchData();
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
            for (const key in columns_ob) {
                let info = {
                    'field': key,
                    'title': columns_ob[key].label,
                    'cell_render': this.getCellRender(key),
                    'formatter': this.getFormatter(key),
                };
                columns.push(info);
            }
            
            return columns;
        },
        refreshField() {
            // 发起服务端请求，获取数据
            this.$axios.options("api/douban_books/")
                .then(response => {
                        // 请求成功处理逻辑
                        let columns = this.handleColumns(response);
                        this.columns = columns;
                    })
                .catch(error => {
                    // 请求失败处理逻辑
                    console.error(error);
                });
        },
        fetchData() {
            // 发起服务端请求，获取数据
            this.$axios.get("api/douban_books/")
                .then(response => {
                        // 请求成功处理逻辑
                        let data = response.data;
                        // 更新 this.tableData 和 this.total
                        this.tableData = data.results;
                        this.total = data.count;
                    })
                .catch(error => {
                    // 请求失败处理逻辑
                    console.error(error);
                });
        }
    }
}
</script>
<style scoped>
</style>