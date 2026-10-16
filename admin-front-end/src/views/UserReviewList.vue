<template>
  <lay-layer v-model="loading" type="3" shade-close="false"/>
  <lay-layer v-model="disabled" type="3" shade-close="false"/>
  <lay-layer v-model="editUserShow" title="Account Edit" :area="['600px', '620px']" z-index="1000">
    <lay-form :model="editUserInf">
      <lay-quote>Account Information</lay-quote>
      <lay-row space="10" style="margin-top: 10pt; width: 590px">
        <lay-col md="14">
          <lay-form-item label="Username" prop="text" style="text-align: left"  label-width="100px" required>
            <lay-input v-model="editUserInf.username" type="test" style="width: 222px"></lay-input>
          </lay-form-item>
        </lay-col>
        <lay-col md="10">
          <lay-form-item label="Status" prop="text">
            <lay-select v-model="editUserInf.state" placeholder="Select..." style="width: 150px" >
              <lay-select-option :value="-1" label="Pending"></lay-select-option>
            </lay-select>
          </lay-form-item>
        </lay-col>
      </lay-row>
      <lay-quote>Personal Information</lay-quote>
      <lay-row space="4" style="margin-top: 10pt; width: 590px">
        <lay-col md="12">
          <lay-form-item label="Name" prop="text" style="text-align: left" required>
            <lay-input v-model="editUserInf.name" type="text" style="width: 200px"></lay-input>
          </lay-form-item>
        </lay-col>
        <lay-col md="12">
          <lay-form-item label="Card ID" prop="text" style="text-align: left" required>
            <lay-input v-model="editUserInf.card_id" type="text" style="width: 200px"></lay-input>
          </lay-form-item>
        </lay-col>
        <lay-col md="24">
          <lay-form-item label="Student ID" prop="text" style="text-align: left;" label-width="104px" required>
            <lay-input v-model="editUserInf.student_id" type="text" style="width: 466px"></lay-input>
          </lay-form-item>
        </lay-col>
      </lay-row>
      <lay-quote>Contact information</lay-quote>
      <lay-row space="4" style="margin-top: 10pt; width: 590px">
        <lay-col md="12">
          <lay-form-item label="Phone" prop="text" style="text-align: left" required>
            <lay-input v-model="editUserInf.phone" type="text" style="width: 200px"></lay-input>
          </lay-form-item>
        </lay-col>
        <lay-col md="12">
          <lay-form-item label="Wechat ID" prop="text" style="text-align: left" required>
            <lay-input v-model="editUserInf.wechat_id" type="text" style="width: 200px"></lay-input>
          </lay-form-item>
        </lay-col>
        <lay-col md="24">
          <lay-form-item label="Email" prop="text" style="text-align: left">
            <lay-input v-model="editUserInf.email" type="text" style="width: 496px"></lay-input>
          </lay-form-item>
        </lay-col>
      </lay-row>
      <div style="text-align: right; margin-top: -3px;">
        <lay-button @click="this.editUserShow = false"><lay-icon type="layui-icon-close"/> Cancel</lay-button>
        <lay-button type="primary" style="margin-right: 20px" @click="onEditSubmit" :disabled="disabled"><lay-icon type="layui-icon-release"/> Submit</lay-button>
      </div>
    </lay-form>
  </lay-layer>

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
            <lay-breadcrumb-item title="Accounts"></lay-breadcrumb-item>
            <lay-breadcrumb-item title="Verification"></lay-breadcrumb-item>
          </lay-breadcrumb>
        </lay-col>
        <lay-col md="24" style="margin-top: 4pt">
          <lay-input v-model="preQuery.name" size="sm" type="text" style="width: 120pt" placeholder="Name" prefix-icon="layui-icon-user"></lay-input>
          <lay-input v-model="preQuery.student_id" size="sm" type="text" style="width: 180pt; margin-left: 10pt" placeholder="Student ID" prefix-icon="layui-icon-read"></lay-input>
          <lay-button type="primary" size="sm" style="margin-left: 10pt" prefix-icon="layui-icon-search" @click="queryData(-1)" :disabled="loading">Query</lay-button>
        </lay-col>
      </lay-row>
    </template>
    <template #empty>
      <lay-empty description="No Records"></lay-empty>
    </template>
    <template v-slot:operator="{ rowIndex }">
      <lay-button size="xs" type="normal" :disabled="this.loading" @click="onEditShow(rowIndex)"><lay-icon type="layui-icon-tabs"/> Edit</lay-button>
      <lay-button size="xs" type="primary" :disabled="this.loading" @click="onPassSubmit(rowIndex)" style="background: green"><lay-icon type="layui-icon-ok"/> Approval</lay-button>
      <lay-button size="xs" type="danger" :disabled="this.loading" @click="onDeleteSubmit(rowIndex)"><lay-icon type="layui-icon-delete"/> Delete</lay-button>
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
        { title:"Username", minWidth:"320px", resize:true, key:"username"},
        { title:"Name", minWidth:"160px", resize:true, key:"name" },
        { title:"Student ID", minWidth:"240px", resize:true, key:"student_id" },
        { title:"Card ID", minWidth:"160px", resize:true, key:"card_id" },
        { title:"Wechat ID", minWidth:"200px", resize:true, key:"wechat_id"},
        { title:"Phone", minWidth:"200px", resize:true, key:"phone" },
        { title:"State", minWidth:"160px", resize:true, key:"status_name" },
        { title:"Operation" , width: "260px", customSlot:"operator", key:"operator", fixed: "right", ignoreExport: true }
      ],
      dataSource:[],
      editUserInf:{
        id: -1,
        username: '',
        name: '',
        phone: '',
        state: -1,
        student_id: '',
        wechat_id: '',
        email: '',
        card_id: '',
      },
      editUserShow: false,
      disabled: false,
      currentIndex: -1
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
      this.$http.post(`/member/queryReviewMembers?token=${Cookies.get('token')}&page_size=${this.page.limit}&page_number=${this.page.current}`, {
        name: this.query.name, student_id: this.query.student_id
      })
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
            layer.msg('Internet Error！', {icon: 2, time: 1500});
            this.loading = false;
          })
    },
    computedStatusName(obj){
      obj.status_name = '';
      switch(obj.state){
        case -1:
          obj.status_name = 'Pending'; break;
        case 0:
          obj.status_name = 'Blocked'; break;
        case 1:
          obj.status_name = 'Dishonesty'; break;
        case 2:
          obj.status_name = 'Normal'; break;
        case 3:
          obj.status_name = 'Duty Stuff'; break;
        case 4:
          obj.status_name = 'Administrator';
      }
    },
    onEditShow(id){
      this.currentIndex = id;
      this.editUserInf = JSON.parse(JSON.stringify(this.dataSource[id]));
      this.editUserShow = true;
    },
    onEditSubmit(){
      if(this.editUserInf.username === '' || this.editUserInf.name === '' || this.editUserInf.card_id === '' ||
      this.editUserInf.phone === '' || this.editUserInf.wechat_id === '' || this.editUserInf.student_id === ''){
        layer.msg('Required fields cannot be blank', {icon: 7, time: 1500});
        return;
      }
      this.disabled = true;
      this.$http.post(`/member/updateUserInf?token=${Cookies.get('token')}&id=${this.editUserInf.id}`, {
        username: this.editUserInf.username, name: this.editUserInf.name,
        card_id: this.editUserInf.card_id, phone: this.editUserInf.phone,
        state: this.editUserInf.state, wechat_id: this.editUserInf.wechat_id,
        email: this.editUserInf.email, student_id: this.editUserInf.student_id
      })
          .then(res => {
            if(res.status === 200){
              if(res.data.status === -2) {
                this.$clear();
                return;
              }
              if(res.data.status === -1){
                this.disabled = false;
                this.editUserShow = false;
                layer.msg('It is not allowed to edit the information of the currently registered user.',{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 0){
                this.disabled = false;
                layer.msg('Currently modified username duplicates with other accounts',{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 1){
                this.disabled = false;
                this.editUserShow = false;
                layer.msg('The current account has been deleted, please refresh the page and try again',{icon: 7, time: 1500});
                return;
              }
              this.dataSource[this.currentIndex] = JSON.parse(JSON.stringify(this.editUserInf));
              this.computedStatusName(this.dataSource[this.currentIndex]);
              this.disabled = false;
              this.editUserShow = false;
              layer.msg('Update successfully!',{icon: 1, time: 1500});
            }else{
              layer.msg('System Error',{icon: 1, time: 1500});
            }
          })
          .catch(res => {
            layer.msg('Internet Error', {icon: 2, time: 1500})
          })
    },
    onDeleteSubmit(index){
      layer.confirm(`Whether to confirm the deletion of the account “${this.dataSource[index].username}”, the information won't be recoverable, should I continue?`,
          {
            title:"Query",
            icon: 3,
            btn: [
              {text:'Confirm', callback: (id) => {
                  layer.close(id);
                  this.$http.post(`/member/deleteUser?token=${Cookies.get('token')}&user_id=${this.dataSource[index].id}`)
                      .then(res => {
                        if(res.status === 200){
                          if(res.data.status === -2) {
                            this.$clear();
                            return;
                          }
                          if(res.data.status === -1){
                            this.disabled = false;
                            this.changePasswordShow = false;
                            layer.msg('Deletion of currently logged in account is not allowed',{icon: 7, time: 1500});
                            return;
                          }
                          if(res.data.status === 0){
                            this.disabled = false;
                            this.changePasswordShow = false;
                            layer.msg('The current account has been deleted, please refresh the page and try again',{icon: 7, time: 1500});
                            return;
                          }
                          this.dataSource[this.currentIndex] = JSON.parse(JSON.stringify(this.editUserInf));
                          this.computedStatusName(this.dataSource[this.currentIndex]);
                          this.disabled = false;
                          this.changePasswordShow = false;
                          layer.msg('Current account deleted successfully',{icon: 1, time: 1500});
                          if(this.dataSource.length === 1 && this.page.current > 1){
                            this.page.current = this.page.current - 1;
                          }
                          this.queryData();
                        }else{
                          layer.msg('System Error',{icon: 1, time: 1500});
                        }
                      })
                      .catch(res => {
                        layer.msg('Internet Error', {icon: 2, time: 1500})
                      })

                }
              },
              {text:'Cancel', callback: (id) => {
                  layer.close(id);
              }
              }
            ]
          }
      );
    },
    onPassSubmit(index){
      this.$http.post(`/member/passUser?token=${Cookies.get('token')}&user_id=${this.dataSource[index].id}`)
          .then(res => {
            if(res.status === 200){
              if(res.data.status === -2) {
                this.$clear();
                return;
              }
              if(res.data.status === 0){
                this.disabled = false;
                this.changePasswordShow = false;
                layer.msg('The current account has been deleted, please refresh the page and try again.',{icon: 7, time: 1500});
                return;
              }
              this.dataSource[this.currentIndex] = JSON.parse(JSON.stringify(this.editUserInf));
              this.computedStatusName(this.dataSource[this.currentIndex]);
              this.disabled = false;
              this.changePasswordShow = false;
              layer.msg('Current Account Approved',{icon: 1, time: 1500});
              if(this.dataSource.length === 1 && this.page.current > 1){
                this.page.current = this.page.current - 1;
              }
              this.queryData();
            }else{
              layer.msg('System Error',{icon: 1, time: 1500});
            }
          })
          .catch(res => {
            layer.msg('Internet Error', {icon: 2, time: 1500})
          });
    }
  }
}

</script>

<style>

</style>
