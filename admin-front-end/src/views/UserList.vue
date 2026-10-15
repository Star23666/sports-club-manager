<template xmlns="http://www.w3.org/1999/html">
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
              <lay-select-option :value="3" label="Duty Staff"></lay-select-option>
              <lay-select-option :value="4" label="Administrator"></lay-select-option>
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

  <lay-layer v-model="changePasswordShow" title="Password Setting" :area="['500px', '320px']" z-index="1000">
    <lay-quote>Modify Password of Account “{{dataSource[currentIndex].username}}”</lay-quote>
    <div style="padding: 20px;">
      <lay-form :model="changeInf" required>
        <lay-form-item label="New Password" prop="password" label-width="130px">
          <lay-input v-model="changeInf.new_pass" type="password">></lay-input>
        </lay-form-item>
        <lay-form-item label="Password Confirm" prop="password" label-width="130px">
          <lay-input v-model="changeInf.cfm_pass" type="password">></lay-input>
        </lay-form-item>
        <div style="text-align: right">
          <lay-button style="margin-top: 10px;" @click="this.changePasswordShow = false"><lay-icon type="layui-icon-close"/> Cancel</lay-button>
          <lay-button type="primary" style="margin-top: 10px;" :disabled="disabled" @click="onPasswordSubmit"><lay-icon type="layui-icon-release"/> Submit</lay-button>
        </div>
      </lay-form>
    </div>
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
            <lay-breadcrumb-item title="Management"></lay-breadcrumb-item>
          </lay-breadcrumb>
        </lay-col>
        <lay-col md="24" style="margin-top: 4pt">
          <lay-input v-model="preQuery.name" size="sm" type="text" style="width: 120pt" placeholder="Name" prefix-icon="layui-icon-user"></lay-input>
          <lay-input v-model="preQuery.student_id" size="sm" type="text" style="width: 180pt; margin-left: 10pt" placeholder="Student ID" prefix-icon="layui-icon-read"></lay-input>
          <lay-dropdown updateAtScroll>
            <lay-button :disabled="loading" size="sm" style="margin-left: 10pt" prefix-icon="layui-icon-cols" >User Status</lay-button>
            <template #content>
              <lay-dropdown-menu>
                <lay-dropdown-menu-item @click="queryData(-1)"><span v-if="query.state===-1"><lay-icon type="layui-icon-ok"/></span> All Status</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(2)"><span v-if="query.state===2"><lay-icon type="layui-icon-ok"/></span> Normal</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(3)"><span v-if="query.state===3"><lay-icon type="layui-icon-ok"/></span> Duty Staffs</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(4)"><span v-if="query.state===4"><lay-icon type="layui-icon-ok"/></span> Administrators</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(1)"><span v-if="query.state===1"><lay-icon type="layui-icon-ok"/></span> Dishonest</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(0)"><span v-if="query.state===0"><lay-icon type="layui-icon-ok"/></span> Blocked</lay-dropdown-menu-item>
              </lay-dropdown-menu>
            </template>
          </lay-dropdown>
          <lay-button type="primary" size="sm" style="margin-left: 10pt" prefix-icon="layui-icon-search" @click="queryData(-2)" :disabled="loading">Query</lay-button>
        </lay-col>
      </lay-row>
    </template>
    <template #empty>
      <lay-empty description="No Records"></lay-empty>
    </template>
    <template v-slot:operator="{ rowIndex }">
      <lay-button size="xs" type="normal" :disabled="this.loading" @click="onEditShow(rowIndex)"><lay-icon type="layui-icon-tabs"/> Edit</lay-button>
      <lay-button size="xs" type="warm" :disabled="this.loading" @click="onPasswordShow(rowIndex)"><lay-icon type="layui-icon-password"/> Modify Password</lay-button>
      <lay-button size="xs" type="danger" :disabled="this.loading" @click="onDeleteSubmit(rowIndex)"><lay-icon type="layui-icon-delete"/> Delete</lay-button>
    </template>
  </lay-table>
</template>

<script>
import {layer} from "@layui/layui-vue";
import Cookies from "js-cookie";

export default {
  created() {
    this.loading = true;
    this.intervalId = setInterval(this.queryData, 10000);
    this.queryData();
  },
  beforeRouteLeave (to, from, next) {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
    next();
  },
  beforeDestroy() {
    // 销毁计时器
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  },
  data(){
    return{
      intervalId: null,
      preQuery:{
        name: '',
        student_id: ''
      },
      query:{
        name: '',
        student_id: '',
        state: -1
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
        { title:"Card ID", width:"160px", resize:true, key:"card_id" },
        { title:"Wechat ID", width:"160px", resize:true, key:"wechat_id"},
        { title:"Phone", width:"160px", resize:true, key:"phone" },
        { title:"Status", width:"160px", resize:true, key:"status_name" },
        { title:"Operation" , width: "260px" , fixed: "right", customSlot:"operator", key:"operator", ignoreExport: true }
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
      changeInf:{
        new_pass:'',
        cfm_pass:''
      },
      editUserShow: false,
      changePasswordShow: false,
      disabled: false,
      currentIndex: -1
    };
  },
  methods: {
    change() {
      this.queryData();
    },
    queryData(val){
      if(typeof val === 'number'){
        this.loading = true;
        if(val === -2){
          this.query.name = this.preQuery.name;
          this.query.student_id = this.preQuery.student_id;
        }
        else{
          this.query.state = val;
          this.page.current = 1;
        }
      }
      this.$http.post(`/member/queryMembers?token=${Cookies.get('token')}&name=${encodeURIComponent(this.query.name)}&state=${this.query.state}
&student_id=${encodeURIComponent(this.query.student_id)}&page_size=${this.page.limit}&page_number=${this.page.current}`)
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
        case 0:
          obj.status_name = 'Blocked'; break;
        case 1:
          obj.status_name = 'Dishonest'; break;
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
    onPasswordShow(id){
      this.currentIndex = id;
      this.changeInf.new_pass = '';
      this.changeInf.cfm_pass = '';
      this.changePasswordShow = true;
    },
    onEditSubmit(){
      if(this.editUserInf.username === '' || this.editUserInf.name === '' || this.editUserInf.card_id === '' ||
      this.editUserInf.phone === '' || this.editUserInf.wechat_id === '' || this.editUserInf.student_id === ''){
        layer.msg('Necessary Information can\'t be null!', {icon: 7, time: 1500});
        return;
      }
      if(this.editUserInf.state === 3 && this.dataSource[this.currentIndex].state !== 3){
        layer.confirm("If switching the current user to the Duty Stuff type empties his/her participation record, is it confirmed?",
            {
              btn: [
                {
                  text:'Confirm', callback: (id) => {
                    layer.close(id);
                    this.onConfirmUpdateUser();
                  }
                }, {
                  text:'Cancel', callback: (id) => {
                    layer.close(id);
                  }
                }
              ],
              icon: 7,
              title: "Alarm"
            }
        );
      }
      else{
        this.onConfirmUpdateUser();
      }
    },
    onConfirmUpdateUser(){
      this.disabled = true;
      this.$http.post(`/member/updateUserInf?token=${Cookies.get('token')}&id=${this.editUserInf.id}&username=${encodeURIComponent(this.editUserInf.username)}&name=${encodeURIComponent(this.editUserInf.name)}\
&card_id=${encodeURIComponent(this.editUserInf.card_id)}&phone=${encodeURIComponent(this.editUserInf.phone)}&state=${encodeURIComponent(this.editUserInf.state)}&wechat_id=${encodeURIComponent(this.editUserInf.wechat_id)}\
&email=${encodeURIComponent(this.editUserInf.email)}&student_id=${encodeURIComponent(this.editUserInf.student_id)}`)
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
    onPasswordSubmit(){
      if(this.changeInf.new_pass === '' || this.changeInf.cfm_pass === ''){
        layer.msg('The modified password cannot be empty.', {icon: 7, time: 1500});
        return;
      }
      if(this.changeInf.new_pass !== this.changeInf.cfm_pass){
        layer.msg('The password entered twice is not the same.', {icon: 7, time: 1500});
        return;
      }
      const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}/;
      if(pattern.test(this.changeInf.new_pass) === false){
        this.disabled = false;
        layer.msg("The currently set password does not meet the rules: The password must be at least 8 characters long and contain uppercase and lowercase letters, numbers, and special symbols"
            , {icon:7, time: 1500});
        return;
      }
      this.$http.post(`/member/updateUserPassword?token=${Cookies.get('token')}&user_id=${this.dataSource[this.currentIndex].id}`, { password: this.changeInf.new_pass })
          .then(res => {
            if(res.status === 200){
              if(res.data.status === -2) {
                this.$clear();
                return;
              }
              if(res.data.status === -1){
                this.disabled = false;
                this.changePasswordShow = false;
                layer.msg('To change the password of current registered user, please go to \'Password Setting\' in the upper right corner to change the password.'
                    ,{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 0){
                this.disabled = false;
                this.changePasswordShow = false;
                layer.msg('The current account has been deleted, please refresh the page and try again.'
                    ,{icon: 7, time: 1500});
                return;
              }
              this.disabled = false;
              this.changePasswordShow = false;
              layer.msg('Password modified successfully',{icon: 1, time: 1500});
            }else{
              layer.msg('System Error',{icon: 1, time: 1500});
            }
          })
          .catch(res => {
            layer.msg('Internet Error', {icon: 2, time: 1500})
          })
    },
    onDeleteSubmit(index){
      layer.confirm(`Are you confirming the deletion of the account “${this.dataSource[index].username}”, which will cause the data to be unrecoverable?`,
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
                            layer.msg('Deletion of currently signed up accounts is not allowed.',{icon: 7, time: 1500});
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
                            this.editUserShow = false;
                            layer.msg('The current account is a Duty Stuff and is still scheduled, please assign it to another Duty Stuff or wait until it is finished before deleting it!',{icon: 7, time: 1500});
                            return;
                          }
                          this.dataSource[this.currentIndex] = JSON.parse(JSON.stringify(this.editUserInf));
                          this.computedStatusName(this.dataSource[this.currentIndex]);
                          this.disabled = false;
                          this.changePasswordShow = false;
                          layer.msg('Delete Successful',{icon: 1, time: 1500});
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
    }
  }
}

</script>

<style>

</style>
