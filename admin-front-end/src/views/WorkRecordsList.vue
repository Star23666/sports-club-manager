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
            <lay-breadcrumb-item title="Records"></lay-breadcrumb-item>
            <lay-breadcrumb-item title="Duties"></lay-breadcrumb-item>
          </lay-breadcrumb>
        </lay-col>
        <lay-col md="24" style="margin-top: 4pt">
          <lay-input v-model="preQuery.name" size="sm" type="text" style="width: 120pt" placeholder="Stuff Name" prefix-icon="layui-icon-user"></lay-input>
          <lay-input v-model="preQuery.student_id" size="sm" type="text" style="width: 180pt; margin-left: 10pt" placeholder="Action Name" prefix-icon="layui-icon-flag"></lay-input>
          <lay-button type="primary" size="sm" style="margin-left: 10pt" prefix-icon="layui-icon-search" @click="queryData(-1)" :disabled="loading">Query</lay-button>
        </lay-col>
      </lay-row>
    </template>
    <template #empty>
      <lay-empty description="No Records"></lay-empty>
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
        { title:"Stuff Name", width:"120px", resize:true, key:"staff_name" },
        { title:"Stuff Username", width:"120px", resize:true, key:"staff_username" },
        { title:"Action Name", width:"220px", resize:true, key:"action_title"},
        { title:"No. of Rackets", width:"100px", resize:true, key:"borrow_num" },
        { title:"Location", width:"160px", resize:true, key:"action_place" },
        { title:"Date", width:"160px", resize:true, key:"action_date"},
        { title:"Time", width:"160px", resize:true, key:"action_time_range"},
        { title:"Action Status", width:"160px", resize:true, key:"action_state_name" },],
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
              layer.msg('System Error', {icon: 2, time: 1500});
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
            layer.msg('Internet Error!', {icon: 2, time: 1500});
            this.loading = false;
          })
    },
    computedStatusName(obj){
      obj.status_name = '';
      switch(obj.action_state){
        case 1:
          obj.action_state_name = 'In Preparation'; break;
        case 2:
          obj.action_state_name = 'In Participating'; break;
        case 3:
          obj.action_state_name = 'Entry Closed'; break;
        case 4:
          obj.action_state_name = 'In Process'; break;
        case 5:
          obj.action_state_name = 'Terminated'; break;
      }

    }
  }
}

</script>

<style>

</style>
