<template xmlns="http://www.w3.org/1999/html">
  <lay-layer v-model="loading" type="3" shade-close="false"/>
  <lay-layer v-model="disabled" type="3" shade-close="false"/>
  <lay-layer v-model="editUserShow" title="编辑账号" :area="['600px', '620px']" z-index="1000">
    <lay-form :model="editUserInf">
      <lay-quote>账号信息</lay-quote>
      <lay-row space="10" style="margin-top: 10pt; width: 590px">
        <lay-col md="14">
          <lay-form-item label="用户名" prop="text" style="text-align: left"  label-width="100px" required>
            <lay-input v-model="editUserInf.username" type="test" style="width: 222px"></lay-input>
          </lay-form-item>
        </lay-col>
        <lay-col md="10">
          <lay-form-item label="状态" prop="text">
            <lay-select v-model="editUserInf.state" placeholder="请选择" style="width: 150px">
              <lay-select-option :value="0" label="已停用"></lay-select-option>
              <lay-select-option :value="1" label="参加活动受限"></lay-select-option>
              <lay-select-option :value="2" label="正常"></lay-select-option>
              <lay-select-option :value="3" label="工作人员"></lay-select-option>
              <lay-select-option :value="4" label="管理员"></lay-select-option>
            </lay-select>
          </lay-form-item>
        </lay-col>
      </lay-row>
      <lay-quote>个人信息</lay-quote>
      <lay-row space="4" style="margin-top: 10pt; width: 590px">
        <lay-col md="12">
          <lay-form-item label="姓名" prop="text" style="text-align: left" required>
            <lay-input v-model="editUserInf.name" type="text" style="width: 200px"></lay-input>
          </lay-form-item>
        </lay-col>
        <lay-col md="12">
          <lay-form-item label="会员卡号" prop="text" style="text-align: left" required>
            <lay-input v-model="editUserInf.card_id" type="text" style="width: 200px"></lay-input>
          </lay-form-item>
        </lay-col>
        <lay-col md="24">
          <lay-form-item label="学号" prop="text" style="text-align: left;" label-width="104px" required>
            <lay-input v-model="editUserInf.student_id" type="text" style="width: 466px"></lay-input>
          </lay-form-item>
        </lay-col>
      </lay-row>
      <lay-quote>联系方式</lay-quote>
      <lay-row space="4" style="margin-top: 10pt; width: 590px">
        <lay-col md="12">
          <lay-form-item label="手机号" prop="text" style="text-align: left" required>
            <lay-input v-model="editUserInf.phone" type="text" style="width: 200px"></lay-input>
          </lay-form-item>
        </lay-col>
        <lay-col md="12">
          <lay-form-item label="微信号" prop="text" style="text-align: left" required>
            <lay-input v-model="editUserInf.wechat_id" type="text" style="width: 200px"></lay-input>
          </lay-form-item>
        </lay-col>
        <lay-col md="24">
          <lay-form-item label="邮箱" prop="text" style="text-align: left">
            <lay-input v-model="editUserInf.email" type="text" style="width: 496px"></lay-input>
          </lay-form-item>
        </lay-col>
      </lay-row>
      <div style="text-align: right; margin-top: -3px;">
        <lay-button @click="this.editUserShow = false"><lay-icon type="layui-icon-close"/> 取消</lay-button>
        <lay-button type="primary" style="margin-right: 20px" @click="onEditSubmit" :disabled="disabled"><lay-icon type="layui-icon-release"/> 提交</lay-button>
      </div>
    </lay-form>
  </lay-layer>

  <lay-layer v-model="changePasswordShow" title="修改密码" :area="['500px', '320px']" z-index="1000">
    <lay-quote>修改账号“{{dataSource[currentIndex].username}}”的密码</lay-quote>
    <div style="padding: 20px;">
      <lay-form :model="changeInf" required>
        <lay-form-item label="新密码" prop="password" label-width="130px">
          <lay-input v-model="changeInf.new_pass" type="password">></lay-input>
        </lay-form-item>
        <lay-form-item label="确认密码" prop="password" label-width="130px">
          <lay-input v-model="changeInf.cfm_pass" type="password">></lay-input>
        </lay-form-item>
        <div style="text-align: right">
          <lay-button style="margin-top: 10px;" @click="this.changePasswordShow = false"><lay-icon type="layui-icon-close"/> 取消</lay-button>
          <lay-button type="primary" style="margin-top: 10px;" :disabled="disabled" @click="onPasswordSubmit"><lay-icon type="layui-icon-release"/> 提交</lay-button>
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
            <lay-breadcrumb-item title="账号"></lay-breadcrumb-item>
            <lay-breadcrumb-item title="账号管理"></lay-breadcrumb-item>
          </lay-breadcrumb>
        </lay-col>
        <lay-col md="24" style="margin-top: 4pt">
          <lay-input v-model="preQuery.name" size="sm" type="text" style="width: 120pt" placeholder="姓名" prefix-icon="layui-icon-user"></lay-input>
          <lay-input v-model="preQuery.student_id" size="sm" type="text" style="width: 180pt; margin-left: 10pt" placeholder="学号" prefix-icon="layui-icon-read"></lay-input>
          <lay-dropdown updateAtScroll>
            <lay-button :disabled="loading" size="sm" style="margin-left: 10pt" prefix-icon="layui-icon-cols" >账号状态</lay-button>
            <template #content>
              <lay-dropdown-menu>
                <lay-dropdown-menu-item @click="queryData(-1)"><span v-if="query.state===-1"><lay-icon type="layui-icon-ok"/></span> 全部状态</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(2)"><span v-if="query.state===2"><lay-icon type="layui-icon-ok"/></span> 正常</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(3)"><span v-if="query.state===3"><lay-icon type="layui-icon-ok"/></span> 工作人员</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(4)"><span v-if="query.state===4"><lay-icon type="layui-icon-ok"/></span> 管理员</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(1)"><span v-if="query.state===1"><lay-icon type="layui-icon-ok"/></span> 参加活动受限</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(0)"><span v-if="query.state===0"><lay-icon type="layui-icon-ok"/></span> 已停用</lay-dropdown-menu-item>
              </lay-dropdown-menu>
            </template>
          </lay-dropdown>
          <lay-button type="primary" size="sm" style="margin-left: 10pt" prefix-icon="layui-icon-search" @click="queryData(-2)" :disabled="loading">查询</lay-button>
        </lay-col>
      </lay-row>
    </template>
    <template #empty>
      <lay-empty description="暂无记录"></lay-empty>
    </template>
    <template v-slot:operator="{ rowIndex }">
      <lay-button size="xs" type="normal" :disabled="this.loading" @click="onEditShow(rowIndex)"><lay-icon type="layui-icon-tabs"/> 编辑</lay-button>
      <lay-button size="xs" type="warm" :disabled="this.loading" @click="onPasswordShow(rowIndex)"><lay-icon type="layui-icon-password"/> 修改密码</lay-button>
      <lay-button size="xs" type="danger" :disabled="this.loading" @click="onDeleteSubmit(rowIndex)"><lay-icon type="layui-icon-delete"/> 删除</lay-button>
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
        { title:"用户名", width:"160px", resize:true, key:"username"},
        { title:"姓名", width:"160px", resize:true, key:"name" },
        { title:"学号", width:"200px", resize:true, key:"student_id" },
        { title:"会员卡号", width:"160px", resize:true, key:"card_id" },
        { title:"微信号", width:"160px", resize:true, key:"wechat_id"},
        { title:"手机号", width:"160px", resize:true, key:"phone" },
        { title:"状态", width:"160px", resize:true, key:"status_name" },
        { title:"操作" , width: "260px" , fixed: "right", customSlot:"operator", key:"operator", ignoreExport: true }
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
      this.$http.post(`/member/queryMembers?token=${Cookies.get('token')}&state=${this.query.state}&page_size=${this.page.limit}&page_number=${this.page.current}`, {
        name: this.query.name, student_id: this.query.student_id
      })
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
      switch(obj.state){
        case 0:
          obj.status_name = '已停用'; break;
        case 1:
          obj.status_name = '参加活动受限'; break;
        case 2:
          obj.status_name = '正常'; break;
        case 3:
          obj.status_name = '工作人员'; break;
        case 4:
          obj.status_name = '管理员';
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
        layer.confirm("将账号改为工作人员会清空其报名记录，确定继续吗？",
            {
              btn: [
                {
                  text:'确认', callback: (id) => {
                    layer.close(id);
                    this.onConfirmUpdateUser();
                  }
                }, {
                  text:'取消', callback: (id) => {
                    layer.close(id);
                  }
                }
              ],
              icon: 7,
              title: "请确认"
            }
        );
      }
      else{
        this.onConfirmUpdateUser();
      }
    },
    onConfirmUpdateUser(){
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
                layer.msg('不能修改当前登录管理员的权限。',{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 0){
                this.disabled = false;
                layer.msg('用户名已被其他账号使用。',{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 1){
                this.disabled = false;
                this.editUserShow = false;
                layer.msg('该账号已删除，请刷新页面后重试。',{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 2){
                this.disabled = false;
                this.editUserShow = false;
                layer.msg('该工作人员仍有排班，请先重新分配或等待活动结束。',{icon: 7, time: 1500});
                return;
              }
              this.dataSource[this.currentIndex] = JSON.parse(JSON.stringify(this.editUserInf));
              this.computedStatusName(this.dataSource[this.currentIndex]);
              this.disabled = false;
              this.editUserShow = false;
              layer.msg('更新成功',{icon: 1, time: 1500});
            }else{
              layer.msg('系统异常，请稍后重试',{icon: 1, time: 1500});
            }
          })
          .catch(res => {
            layer.msg('网络异常，请稍后重试', {icon: 2, time: 1500})
          });
    },
    onPasswordSubmit(){
      if(this.changeInf.new_pass === '' || this.changeInf.cfm_pass === ''){
        layer.msg('新密码不能为空。', {icon: 7, time: 1500});
        return;
      }
      if(this.changeInf.new_pass !== this.changeInf.cfm_pass){
        layer.msg('两次输入的密码不一致。', {icon: 7, time: 1500});
        return;
      }
      const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}/;
      if(pattern.test(this.changeInf.new_pass) === false){
        this.disabled = false;
        layer.msg("密码至少 8 位，且须包含大小写字母、数字和特殊符号"
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
                layer.msg('请在右上角的“密码设置”中修改当前账号的密码。'
                    ,{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 0){
                this.disabled = false;
                this.changePasswordShow = false;
                layer.msg('该账号已删除，请刷新页面后重试。'
                    ,{icon: 7, time: 1500});
                return;
              }
              this.disabled = false;
              this.changePasswordShow = false;
              layer.msg('密码修改成功，该用户需重新登录',{icon: 1, time: 1500});
            }else{
              layer.msg('系统异常，请稍后重试',{icon: 1, time: 1500});
            }
          })
          .catch(res => {
            layer.msg('网络异常，请稍后重试', {icon: 2, time: 1500})
          })
    },
    onDeleteSubmit(index){
      layer.confirm(`确定删除账号“${this.dataSource[index].username}”吗？账号数据无法恢复。`,
          {
            title:"确认删除",
            icon: 3,
            btn: [
              {text:'确认删除', callback: (id) => {
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
                            layer.msg('不能删除当前登录的账号。',{icon: 7, time: 1500});
                            return;
                          }
                          if(res.data.status === 0){
                            this.disabled = false;
                            this.changePasswordShow = false;
                            layer.msg('该账号已删除，请刷新页面后重试。',{icon: 7, time: 1500});
                            return;
                          }
                          if(res.data.status === 1){
                            this.disabled = false;
                            this.editUserShow = false;
                            layer.msg('该工作人员仍有排班，请先重新分配或等待活动结束后再删除。',{icon: 7, time: 1500});
                            return;
                          }
                          this.dataSource[this.currentIndex] = JSON.parse(JSON.stringify(this.editUserInf));
                          this.computedStatusName(this.dataSource[this.currentIndex]);
                          this.disabled = false;
                          this.changePasswordShow = false;
                          layer.msg('删除成功',{icon: 1, time: 1500});
                          if(this.dataSource.length === 1 && this.page.current > 1){
                            this.page.current = this.page.current - 1;
                          }
                          this.queryData();
                        }else{
                          layer.msg('系统异常，请稍后重试',{icon: 1, time: 1500});
                        }
                      })
                      .catch(res => {
                        layer.msg('网络异常，请稍后重试', {icon: 2, time: 1500})
                      })

                }
              },
              {text:'取消', callback: (id) => {
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
