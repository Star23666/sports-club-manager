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
            <lay-breadcrumb-item title="报名"></lay-breadcrumb-item>
          </lay-breadcrumb>
        </lay-col>
        <lay-col md="24" style="margin-top: 4pt">
          <lay-input v-model="preQuery.name" size="sm" type="text" style="width: 120pt" placeholder="参与者姓名" prefix-icon="layui-icon-user"></lay-input>
          <lay-input v-model="preQuery.student_id" size="sm" type="text" style="width: 180pt; margin-left: 10pt" placeholder="活动名称" prefix-icon="layui-icon-flag"></lay-input>
          <lay-button type="primary" size="sm" style="margin-left: 10pt" prefix-icon="layui-icon-search" @click="queryData(-1)" :disabled="loading">查询</lay-button>
        </lay-col>
      </lay-row>
    </template>
    <template #empty>
      <lay-empty description="暂无记录"></lay-empty>
    </template>
    <template #resign="{ row }">
      <div v-if="row.state == 0">
        Unsigned&nbsp; <lay-button v-if="row.action_state > 3" type="warm" size="xs" prefix-icon="layui-icon-survey" @click="onResignClick(row.id)">补签</lay-button>
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
        { title:"参与者姓名", width:"120px", resize:true, key:"account_name" },
        { title:"学号", width:"140px", resize:true, key:"account_student_id" },
        { title:"活动", width:"160px", resize:true, key:"action_title"},
        { title:"地点", width:"120px", resize:true, key:"action_place" },
        { title:"活动状态", width:"120px", resize:true, key:"action_state_name" },
        { title:"球拍", width:"80px", resize:true, key:"borrow_name" },
        { title:"签到状态", width:"120px", resize:true, customSlot: "resign"},
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
      switch(obj.borrow){
        case 0:
          obj.borrow_name = '否'; break;
        case 1:
          obj.borrow_name = '是'; break;
      }
      switch(obj.action_state){
        case 2:
          obj.action_state_name = '报名中'; break;
        case 3:
          obj.action_state_name = '报名已截止'; break;
        case 4:
          obj.action_state_name = '进行中'; break;
        case 5:
          obj.action_state_name = '已结束'; break;
      }
    },
    onResignClick(id){
      layer.prompt({
        title: "请输入签到验证码",
        formType: "text",
        placeholder: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxxx",
        shadeClose: true,
        btn: [
          {
            text: "补签", callback: (layero, data) => {
              if(data === ""){
                layer.msg('请输入签到验证码后重试。',{icon: 7, time: 1500});
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
                        layer.msg('验证码无效，补签失败。',{icon: 2, time: 1500});
                        layer.close(layero);
                        return;
                      }
                      if(res.data.status === 0){
                        this.disabled = false;
                        this.editActionShow = false;
                        layer.msg('该记录已经签到，请刷新页面。',{icon: 7, time: 1500});
                        layer.close(layero);
                        return;
                      }
                      if(res.data.status === 1){
                        this.disabled = false;
                        this.editActionShow = false;
                        layer.msg('活动尚未开始，目前不能补签。',{icon: 7, time: 1500});
                        layer.close(layero);
                        return;
                      }
                      this.disabled = false;
                      this.editActionShow = false;
                      layer.msg('补签成功！',{icon: 1, time: 1500});
                      layer.close(layero);
                      this.queryData();

                    }else{
                      layer.msg('系统异常，请稍后重试',{icon: 1, time: 1500});
                      layer.close(layero);
                    }
                  })
                  .catch(res => {
                    layer.msg('网络异常，请稍后重试', {icon: 2, time: 1500});
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
