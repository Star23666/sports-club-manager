<template>
  <lay-layer v-model="loading" type="3" shade-close="false"/>
  <lay-table
      :page="page"
      :columns="columns"
      :data-source="dataSource"
      style="margin: 10pt; height: calc(100vh - 70pt);"
      :default-toolbar="true"
      @change="change">
    <template #toolbar>
      <lay-row>
        <lay-col md="24">
          <lay-breadcrumb style="margin-left: 6pt">
            <lay-breadcrumb-item title="记录"></lay-breadcrumb-item>
            <lay-breadcrumb-item title="值班"></lay-breadcrumb-item>
          </lay-breadcrumb>
        </lay-col>
        <lay-col md="24" style="margin-top: 4pt">
          <lay-input v-model="preQuery.name" size="sm" type="text" style="width: 120pt" placeholder="值班人员姓名" prefix-icon="layui-icon-user"></lay-input>
          <lay-input v-model="preQuery.student_id" size="sm" type="text" style="width: 180pt; margin-left: 10pt" placeholder="活动名称" prefix-icon="layui-icon-flag"></lay-input>
          <lay-button type="primary" size="sm" style="margin-left: 10pt" prefix-icon="layui-icon-search" @click="queryData(-1)" :disabled="loading">查询</lay-button>
        </lay-col>
      </lay-row>
    </template>
    <template #empty>
      <lay-empty description="暂无记录"></lay-empty>
    </template>
  </lay-table>
</template>

<script>
import {layer} from "@layui/layui-vue";
import Cookies from "js-cookie";

export default {
  beforeRouteLeave (to, from, next) {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
    next();
  },
  created() {
    this.loading = true;
    this.queryData();
    this.intervalId = setInterval(this.queryData, 10000);
  },
  beforeDestroy() {
    // 销毁计时器
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  },
  data(){
    return{
      preQuery:{
        name: '',
        student_id: ''
      },
      query:{
        name: '',
        student_id: ''
      },
      loading: false,
      page:{
        current: 1,
        limit: 10,
        total: 0
      },
      columns:[
        { title:"值班人员姓名", width:"120px", resize:true, key:"staff_name" },
        { title:"值班人员用户名", width:"120px", resize:true, key:"staff_username" },
        { title:"活动名称", width:"220px", resize:true, key:"action_title"},
        { title:"借用球拍数", width:"100px", resize:true, key:"borrow_num" },
        { title:"地点", width:"160px", resize:true, key:"action_place" },
        { title:"日期", width:"160px", resize:true, key:"action_date"},
        { title:"时间", width:"160px", resize:true, key:"action_time_range"},
        { title:"活动状态", width:"160px", resize:true, key:"action_state_name" },],
      dataSource:[],
      disabled: false,
      currentIndex: -1
    };
  },
  methods: {
    change() {
      this.loading = true;
      this.queryData();
    },
    queryData(val){
      if(val != null){
        this.query.name = this.preQuery.name;
        this.query.student_id = this.preQuery.student_id;
        this.loading = true;
      }
      this.$http.post(`/action/queryWorkRecords?token=${Cookies.get('token')}&name=${encodeURIComponent(this.query.name)}
&title=${encodeURIComponent(this.query.student_id)}&page_size=${this.page.limit}&page_number=${this.page.current}`)
          .then(res => {
            if(res.status !== 200){
              layer.msg('系统异常，请稍后重试', {icon: 2, time: 1500});
              this.loading = false;
              return;
            }
            // console.log(res.data.data);
            if(res.data.status < 0){
              if (this.intervalId) {
                clearInterval(this.intervalId);
              }
              this.$clear();
              this.loading = false;
              return;
            }
            for(var i in res.data.data)
              this.computedStatusName(res.data.data[i]);
            this.dataSource = res.data.data;
            this.page.total = res.data.status;
            this.loading = false;
          })
          .catch(error => {
            layer.msg('网络异常，请稍后重试', {icon: 2, time: 1500});
            this.loading = false;
          })
    },
    computedStatusName(obj){
      obj.status_name = '';
      switch(obj.action_state){
        case 1:
          obj.action_state_name = '筹备中'; break;
        case 2:
          obj.action_state_name = '报名中'; break;
        case 3:
          obj.action_state_name = '报名已截止'; break;
        case 4:
          obj.action_state_name = '进行中'; break;
        case 5:
          obj.action_state_name = '已结束'; break;
      }

    }
  }
}

</script>

<style>

</style>
