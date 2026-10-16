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
            <lay-select v-model="editUserInf.state" placeholder="Select..." style="width: 150px">
              <lay-select-option :value="0" label="Blocked"></lay-select-option>
              <lay-select-option :value="1" label="Dishonest"></lay-select-option>
              <lay-select-option :value="2" label="Normal"></lay-select-option>
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
            <lay-breadcrumb-item title="Dishonesty"></lay-breadcrumb-item>
          </lay-breadcrumb>
          <lay-col md="24" style="margin-top: 4pt">
            <lay-input v-model="preQuery.name" size="sm" type="text" style="width: 120pt" placeholder="Name" prefix-icon="layui-icon-user"></lay-input>
            <lay-input v-model="preQuery.student_id" size="sm" type="text" style="width: 180pt; margin-left: 10pt" placeholder="Student ID" prefix-icon="layui-icon-read"></lay-input>
            <lay-button type="primary" size="sm" style="margin-left: 10pt" prefix-icon="layui-icon-search" @click="queryData(-1)" :disabled="loading">Query</lay-button>
          </lay-col>
        </lay-col>
      </lay-row>
    </template>
    <template #empty>
      <lay-empty description="No Records"></lay-empty>
    </template>
    <template v-slot:operator="{ rowIndex }">
      <lay-button size="xs" type="normal" :disabled="this.loading" @click="onEditShow(rowIndex)"><lay-icon type="layui-icon-tabs"/> Edit</lay-button>
      <lay-button size="xs" type="primary" :disabled="this.loading" @click="onClearSubmit(rowIndex)"><lay-icon type="layui-icon-fonts-clear"/>Dishonesty Clear</lay-button>
      <lay-button size="xs" type="warm" :disabled="this.loading" @click="onResetSubmit(rowIndex)"><lay-icon type="layui-icon-refresh"/>Dishonesty Reset</lay-button>
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
        { title:"Username", width:"160px", resize:true, key:"username"},
        { title:"Name", width:"160px", resize:true, key:"name" },
        { title:"Student ID", width:"200px", resize:true, key:"student_id" },
        { title:"Wechat ID", width:"160px", resize:true, key:"wechat_id"},
        { title:"Phone", width:"160px", resize:true, key:"phone" },
        { title:"Dishonest Points", width:"160px", resize:true, key:"unsigned_num" },
        { title:"Status", width:"150px", resize:true, key:"status_name" },
        { title:"Operation" , width: "320px" , fixed: "right", customSlot:"operator", key:"operator", ignoreExport: true }
      ],
      dataSource:[],
      editUserInf:{
        id: -1,
        username: '',
        name: '',
        phone: '',
        state: 0,
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
      this.$http.post(`/member/queryUnsignedMembers?token=${Cookies.get('token')}&page_size=${this.page.limit}&page_number=${this.page.current}`, {
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
            if(this.dataSource.length === 0 && this.page.current > 1){
              this.page.current = this.page.current - 1;
              this.queryData();
            }
            this.loading = false;
          })
          .catch(error => {
            layer.msg('Internet Error!', {icon: 2, time: 1500});
            this.loading = false;
          })
    },
    computedStatusName(obj){
      obj.status_name = '';
      switch(obj.state){
        case 0:
          obj.status_name = 'Blocked'; break;
        case 1:
          obj.status_name = 'Dishonest'; break;
        case 2:
          obj.status_name = 'Normal'; break;
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
        layer.msg('Necessary Information can\'t be null!', {icon: 7, time: 1500});
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
                layer.msg('It is not allowed to modify the administrator privileges of the currently logged-in account.',{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 0){
                this.disabled = false;
                layer.msg('The username of the currently modified account is duplicated with that of another account.',{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 1){
                this.disabled = false;
                this.editUserShow = false;
                layer.msg('The current account has been deleted, please refresh the page and try again.',{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 2){
                this.disabled = false;
                this.editUserShow = false;
                layer.msg('The current account is a Duty Stuff and is still scheduled, please assign another Duty Stuff to it or wait until it is finished before changing it!',{icon: 7, time: 1500});
                return;
              }
              this.dataSource[this.currentIndex] = JSON.parse(JSON.stringify(this.editUserInf));
              this.computedStatusName(this.dataSource[this.currentIndex]);
              this.disabled = false;
              this.editUserShow = false;
              layer.msg('Update Successfully',{icon: 1, time: 1500});
            }else{
              layer.msg('System Error',{icon: 1, time: 1500});
            }
          })
          .catch(res => {
            layer.msg('Internet Error', {icon: 2, time: 1500})
          });
    },
    onClearSubmit(index){
      layer.confirm(`Whether or not to confirm the clearing dishonest points of account “${this.dataSource[index].username}”. This operation will not delete the relative records, do you want to continue?`,
          {
            title:"Query",
            icon: 3,
            btn: [
              {text:'Confirm', callback: (id) => {
                  layer.close(id);
                  this.disabled = true;
                  this.$http.post(`/member/clearUserUnsigned?token=${Cookies.get('token')}&user_id=${this.dataSource[index].id}`)
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
                          if(res.data.status === 1){
                            this.disabled = false;
                            this.changePasswordShow = false;
                            layer.msg('The current account has been modified. Please refresh the page and try again.',{icon: 7, time: 1500});
                            return;
                          }
                          this.dataSource[this.currentIndex] = JSON.parse(JSON.stringify(this.editUserInf));
                          this.computedStatusName(this.dataSource[this.currentIndex]);
                          this.disabled = false;
                          this.changePasswordShow = false;
                          layer.msg('Current account has been cleared and can be restored through “Dishonesty Reset”.',{icon: 1, time: 1500});
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
    onResetSubmit(index){
      layer.confirm(`Whether or not to confirm the reset of dishonest points of account “${this.dataSource[index].username}”. The reset will calculate all relevant records, should I continue?`,
          {
            title:"Query",
            icon: 3,
            btn: [
              {text:'Confirm', callback: (id) => {
                  layer.close(id);
                  this.disabled = true;
                  this.$http.post(`/member/resetUserUnsigned?token=${Cookies.get('token')}&user_id=${this.dataSource[index].id}`)
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
                          if(res.data.status === 1){
                            this.disabled = false;
                            this.changePasswordShow = false;
                            layer.msg('The current account has been modified. Please refresh the page and try again.',{icon: 7, time: 1500});
                            return;
                          }
                          this.dataSource[this.currentIndex] = JSON.parse(JSON.stringify(this.editUserInf));
                          this.computedStatusName(this.dataSource[this.currentIndex]);
                          this.disabled = false;
                          this.changePasswordShow = false;
                          layer.msg('The current account has been reset successfully',{icon: 1, time: 1500});
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
    }
  }
}

</script>

<style>

</style>
