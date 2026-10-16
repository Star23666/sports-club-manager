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
            <lay-breadcrumb-item title="Participation"></lay-breadcrumb-item>
          </lay-breadcrumb>
        </lay-col>
        <lay-col md="24" style="margin-top: 4pt">
          <lay-input v-model="preQuery.name" size="sm" type="text" style="width: 120pt" placeholder="Participant Name" prefix-icon="layui-icon-user"></lay-input>
          <lay-input v-model="preQuery.student_id" size="sm" type="text" style="width: 180pt; margin-left: 10pt" placeholder="Action Name" prefix-icon="layui-icon-flag"></lay-input>
          <lay-button type="primary" size="sm" style="margin-left: 10pt" prefix-icon="layui-icon-search" @click="queryData(-1)" :disabled="loading">Query</lay-button>
        </lay-col>
      </lay-row>
    </template>
    <template #empty>
      <lay-empty description="No Records"></lay-empty>
    </template>
    <template #resign="{ row }">
      <div v-if="row.state == 0">
        Unsigned&nbsp; <lay-button v-if="row.action_state > 3" type="warm" size="xs" prefix-icon="layui-icon-survey" @click="onResignClick(row.id)">Re-Sign</lay-button>
      </div>
      <div v-else>
        Signed
      </div>
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
        { title:"Participant Name", width:"120px", resize:true, key:"account_name" },
        { title:"Student ID", width:"140px", resize:true, key:"account_student_id" },
        { title:"Action", width:"160px", resize:true, key:"action_title"},
        { title:"Location", width:"120px", resize:true, key:"action_place" },
        { title:"Action Status", width:"120px", resize:true, key:"action_state_name" },
        { title:"Racket", width:"80px", resize:true, key:"borrow_name" },
        { title:"Sign Status", width:"120px", resize:true, customSlot: "resign"},
      ],
      dataSource:[]
    };
  },
  methods: {
    change() {
      this.queryData();
    },
    queryData(val){
      if(val != null){
        this.query.name = this.preQuery.name;
        this.query.student_id = this.preQuery.student_id;
        this.loading = true;
      }
      this.$http.post(`/action/queryRecords?token=${Cookies.get('token')}&name=${encodeURIComponent(this.query.name)}
&title=${encodeURIComponent(this.query.student_id)}&page_size=${this.page.limit}&page_number=${this.page.current}`)
          .then(res => {
            if(res.status !== 200){
              layer.msg('系統錯誤', {icon: 2, time: 1500});
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
            layer.msg('網絡錯誤！', {icon: 2, time: 1500});
            this.loading = false;
          })
    },
    computedStatusName(obj){
      switch(obj.borrow){
        case 0:
          obj.borrow_name = 'No'; break;
        case 1:
          obj.borrow_name = 'Yes'; break;
      }
      switch(obj.action_state){
        case 2:
          obj.action_state_name = 'In Participating'; break;
        case 3:
          obj.action_state_name = 'Entry Closed'; break;
        case 4:
          obj.action_state_name = 'In Process'; break;
        case 5:
          obj.action_state_name = 'Terminated'; break;
      }
    },
    onResignClick(id){
      layer.prompt({
        title: "Need to check verification code",
        formType: "text",
        placeholder: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxxx",
        shadeClose: true,
        btn: [
          {
            text: "Re-Sign", callback: (layero, data) => {
              if(data === ""){
                layer.msg('Please enter the verification code and try again.',{icon: 7, time: 1500});
                return;
              }
              this.$http.post(`/action/reSign?token=${Cookies.get('token')}&record_id=${id}`, { sign_code: data })
                  .then(res => {
                    if(res.status === 200){
                      if(res.data.status === -2) {
                        this.$clear();
                        return;
                      }
                      if(res.data.status === -1){
                        this.disabled = false;
                        this.editActionShow = false;
                        layer.msg('Verification code fails to complete the re-sign!',{icon: 2, time: 1500});
                        layer.close(layero);
                        return;
                      }
                      if(res.data.status === 0){
                        this.disabled = false;
                        this.editActionShow = false;
                        layer.msg('The current record has been signed, please refresh the page to update this record!',{icon: 7, time: 1500});
                        layer.close(layero);
                        return;
                      }
                      if(res.data.status === 1){
                        this.disabled = false;
                        this.editActionShow = false;
                        layer.msg('Currently enrolled events are not yet started and cannot be completed at this time!',{icon: 7, time: 1500});
                        layer.close(layero);
                        return;
                      }
                      this.disabled = false;
                      this.editActionShow = false;
                      layer.msg('This entry has been re-signed!',{icon: 1, time: 1500});
                      layer.close(layero);
                      this.queryData();

                    }else{
                      layer.msg('System Error',{icon: 1, time: 1500});
                      layer.close(layero);
                    }
                  })
                  .catch(res => {
                    layer.msg('Internet Error', {icon: 2, time: 1500});
                    layer.close(layero);
                  });
            }
          }
        ]
      });
    }
  }
}

</script>

<style>

</style>
