<template xmlns="http://www.w3.org/1999/html">
  <lay-layer v-model="loading" type="3" shade-close="false"/>
  <lay-layer v-model="disabled" type="3" shade-close="false"/>
  <lay-layer v-model="editActionShow" :title="editActionTitle" :area="[area_width, area_height]"  z-index="1000">
    <lay-form :model="actionInf" required>
      <lay-quote>基本信息（发布后不可修改）</lay-quote>
      <lay-form-item label="活动名称" style="margin-top: 15pt" :key="area_key">
        <lay-input :disabled="actionInf.state > 1" v-model="actionInf.title" style="width: 400px"></lay-input>
      </lay-form-item>
      <lay-form-item label="地点">
        <lay-input :disabled="actionInf.state > 1" v-model="actionInf.place" style="width: 400px"></lay-input>
      </lay-form-item>
      <lay-form-item label="日期">
        <lay-input :disabled="actionInf.state > 1" v-model="actionInf.date" style="width: 400px"></lay-input>
      </lay-form-item>
      <lay-form-item label="时间">
        <lay-input :disabled="actionInf.state > 1" v-model="actionInf.time_range" style="width: 400px"></lay-input>
      </lay-form-item>
      <lay-form-item label="人数上限">
        <lay-input-number :disabled="actionInf.state > 1" v-model="actionInf.max_num" min="1" max="40"></lay-input-number>
      </lay-form-item>
      <lay-quote>值班信息（活动开始后不可修改）</lay-quote>
      <lay-form-item label="负责工作人员">
        <lay-select :disabled="actionInf.state > 3" v-model="actionInf.staff_user_id" placeholder="请选择" style="width: 210pt">
          <template #header>
            <div style="padding: 10px">
              <lay-input placeholder="搜索姓名" prefix-icon="layui-icon-search" v-model="search_name" @input="onQueryNameChange"></lay-input>
            </div>
          </template>
          <lay-select-option v-if="actionInf.staff_user_id === -1" :value="-1" label="请选择"></lay-select-option>
          <lay-select-option v-for="item in queryUserList" :value="item.id">{{item.name}}（{{item.student_id}}，值班 {{item.unsigned_num}} 次）</lay-select-option>
          <template #footer>
            <center v-if="queryUserList.length >= 5" style="font-size: 8pt">最多显示 5 条，请搜索其他人员。</center>
          </template>
        </lay-select>
      </lay-form-item>
      <lay-form-item label="活动微信群">
        <div class="file-upload-wrapper" >
          <input :disabled="actionInf.state > 3" type="file" id="file-upload" class="file-upload" @change="onFileChange" accept="image/*"/>
          <label for="file-upload" :class="actionInf.state > 3 ? 'file-upload-label-disabled' : 'file-upload-label'"><lay-icon type="layui-icon-link"/> 上传二维码</label>
        </div>
        &nbsp;&nbsp;<p style="font-size: 9pt; color: gray; margin-left: 130pt; margin-top: -18pt">自动识别二维码内容</p>
        <div v-if="decodedResult" style="font-size: 10pt; margin-top: 8pt">二维码已上传：
          <lay-button v-if="!qrcodeShow" size="xs" type="warm" @click="this.qrcodeShow = 1" prefix-icon="layui-icon-show">预览</lay-button>
          <lay-button v-else size="xs" type="danger" @click="this.qrcodeShow = 0" prefix-icon="layui-icon-reduce-circle" >隐藏</lay-button>
          <br/>
          <lay-qrcode v-show="qrcodeShow" :text="actionInf.wechat_url"></lay-qrcode>
        </div>
        <div v-else style="font-size: 10pt; margin-top: 5pt">未识别到二维码，请重新上传。</div>
      </lay-form-item>
      <lay-form-item label="开放签到时间">
        <lay-date-picker :disabled="actionInf.state > 3" type="datetime" v-model="actionInf.open_time" placeholder="选择开放签到时间" readonly allowClear></lay-date-picker>
      </lay-form-item>
      <lay-form-item label="允许结束时间">
        <lay-date-picker :disabled="actionInf.state > 3" type="datetime" v-model="actionInf.close_time" placeholder="选择允许结束时间" readonly allowClear></lay-date-picker>
      </lay-form-item>
    </lay-form>
    <template #footer>
      <div style="text-align: left; margin-top: 10px; margin-left: 20px" v-if="actionInf.state <= 3">
        <lay-button type="warm" @click="onReleaseSubmit()" v-if="actionInf.state === 1" prefix-icon="layui-icon-release"> 发布活动</lay-button>
        <lay-button type="danger" @click="onStopRegisterSubmit()" v-if="actionInf.state === 2" prefix-icon="layui-icon-lock"> 截止报名</lay-button>
        <lay-button style="background-color: forestgreen; color: white" @click="onContinueReleaseAction()" v-if="actionInf.state === 3" prefix-icon="layui-icon-play"> 重新开放报名</lay-button>
      </div>
      <div style="text-align: right; margin-top: -37px;" v-if="actionInf.state < 4">
        <lay-button @click="this.editActionShow = false"><lay-icon type="layui-icon-close"/> 关闭</lay-button>
        <lay-button type="primary" style="margin-right: 20px" @click="onEditSubmit" :disabled="disabled"><lay-icon type="layui-icon-list"/> 保存</lay-button>
      </div>
      <div style="text-align: right; margin-top: 5px;" v-if="actionInf.state === 4">
        活动已开始。如需结束，请<a style="cursor: pointer; text-decoration: underline" @click="onStopAction">点击此处</a>。&nbsp;&nbsp;&nbsp;
      </div>
      <div style="text-align: right; margin-top: 5px;" v-if="actionInf.state === 5">
        活动已结束，信息仅供查看。&nbsp;&nbsp;&nbsp;
      </div>
      <br/>
    </template>
  </lay-layer>

  <lay-layer v-model="queryMembersShow" :title="queryMemberTitle" :area="['700px', '500px']"  z-index="1000">
    <lay-table :columns="memberColumns" :data-source="memberDataSource" even height="433px" style="margin: 5px;">
      <template #empty>
        <lay-empty description="暂无记录"></lay-empty>
      </template>
    </lay-table>
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
            <lay-breadcrumb-item title="活动"></lay-breadcrumb-item>
            <lay-breadcrumb-item title="活动管理"></lay-breadcrumb-item>
          </lay-breadcrumb>
        </lay-col>
        <lay-col md="24" style="margin-top: 4pt">
          <lay-input v-model="preQueryName" size="sm" type="text" style="width: 180pt; margin-left: 10pt" placeholder="活动名称" prefix-icon="layui-icon-flag"></lay-input>
          <lay-dropdown updateAtScroll>
            <lay-button :disabled="loading" size="sm" style="margin-left: 10pt" prefix-icon="layui-icon-cols" >状态</lay-button>
            <template #content>
              <lay-dropdown-menu>
                <lay-dropdown-menu-item @click="queryData(0)"><span v-if="query.state===0"><lay-icon type="layui-icon-ok"/></span> 全部状态</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(1)"><span v-if="query.state===1"><lay-icon type="layui-icon-ok"/></span> 准备中</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(2)"><span v-if="query.state===2"><lay-icon type="layui-icon-ok"/></span> 报名中</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(3)"><span v-if="query.state===3"><lay-icon type="layui-icon-ok"/></span> 报名已截止</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(4)"><span v-if="query.state===4"><lay-icon type="layui-icon-ok"/></span> 进行中</lay-dropdown-menu-item>
                <lay-dropdown-menu-item @click="queryData(5)"><span v-if="query.state===5"><lay-icon type="layui-icon-ok"/></span> 已结束</lay-dropdown-menu-item>
              </lay-dropdown-menu>
            </template>
          </lay-dropdown>
          <lay-button type="primary" size="sm" style="margin-left: 10pt" prefix-icon="layui-icon-search" @click="queryData(-1)" :disabled="loading">查询</lay-button>
        </lay-col>
      </lay-row>
    </template>
    <template #empty>
      <lay-empty description="暂无记录"></lay-empty>
    </template>
    <template v-slot:operator="{ row, rowIndex }">
      <lay-button size="xs" type="normal" :disabled="this.loading" @click="onEditShow(rowIndex)" v-if="row.state < 4"><lay-icon type="layui-icon-edit"/> 编辑</lay-button>
      <lay-button size="xs" type="primary" :disabled="this.loading" @click="onEditShow(rowIndex)" v-if="row.state > 3"><lay-icon type="layui-icon-eye"/> 查看</lay-button>
      <lay-button size="xs" :disabled="this.loading" style="background: deeppink; color: white" @click="queryMemberData(rowIndex)"><lay-icon type="layui-icon-form"/> 查看参加者 </lay-button>
      <lay-button size="xs" type="danger" :disabled="this.loading" @click="onDeleteSubmit(rowIndex)"><lay-icon type="layui-icon-delete"/> 删除</lay-button>
    </template>
  </lay-table>
</template>

<script>
import {layer} from "@layui/layui-vue";
import Cookies from "js-cookie";
import jsQR from "jsqr";

export default {
  beforeRouteLeave (to, from, next) {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
    next();
  },
  created() {
    this.intervalId = setInterval(this.queryData, 10000);
    this.loading = true;
    this.queryData();
    this.area_width = '600px';
    this.area_height = '810px';
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
    const vh = 0.90 * (viewportHeight);
    if(vh < 810)
      this.area_height = '90vh';
    this.area_key++;
  },
  beforeDestroy() {
    // 销毁计时器
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  },
  data(){
    return{
      preQueryName:'',
      query:{
        name: '',
        state: 0
      },
      loading: false,
      page:{
        current: 1,
        limit: 10,
        total: 0
      },
      columns:[
        { title:"活动名称", width:"220px", resize:true, key:"title" },
        { title:"地点", width:"200px", resize:true, key:"place" },
        { title:"日期", width:"160px", resize:true, key:"date" },
        { title:"时间", width:"160px", resize:true, key:"time_range"},
        { title:"人数上限", width:"160px", resize:true, key:"max_num" },
        { title:"状态", width:"160px", resize:true, key:"status_name" },
        { title:"操作" , width: "300px" , fixed: "right", customSlot:"operator", key:"operator", ignoreExport: true }
      ],
      dataSource:[],
      memberDataSource:[],
      memberColumns:[
        { title:"姓名", width:"22%", resize:true, key:"name" },
        { title:"学号", width:"22%", resize:true, key:"student_id" },
        { title:"手机号", width:"22%", resize:true, key:"phone" },
        { title:"微信号", width:"22%", resize:true, key:"wechat_id"},
        { title:"球拍", width:"12%", resize:true, key:"borrow_name" }],
      editActionShow: false,
      queryMembersShow: false,
      disabled: false,
      currentIndex: -1,
      actionInf: {
        name: '',
        place: '',
        date: '',
        time_range: '',
        max_num: 1,
        wechat_url: '',
        staff_user_id: -1,
        open_time: '',
        close_time: ''
      },
      decodedResult: '',
      search_name: '',
      queryUserList: [],
      queryMemberTitle: '',
      editActionTitle: '',
      area_width: '',
      area_height: '',
      area_key: 0,
      intervalId: null,
      qrcodeShow: 0
    };
  },
  methods: {
    change() {
      this.queryData();
    },
    queryMemberData(val){
      this.loading = true;
      this.queryMemberTitle = this.dataSource[val].title + ' — 参与者'
      this.$http.post(`/action/queryActionMembers?token=${Cookies.get('token')}&action_id=${this.dataSource[val].id}`)
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
              this.computedMemberStatusName(res.data.data[i]);
            this.memberDataSource = res.data.data;
            this.queryMembersShow = true;
            this.loading = false;
          })
          .catch(error => {
            layer.msg('网络异常，请稍后重试', {icon: 2, time: 1500});
            this.loading = false;
          })

    },
    queryData(val){
      if(typeof val === 'number'){
        if(val === -1){
          this.query.name = this.preQueryName;
        }
        else{
          this.query.state = val;
          this.page.current = 1;
        }
        this.loading = true;
      }
      this.$http.post(`/action/queryActions?token=${Cookies.get('token')}&name=${encodeURIComponent(this.query.name)}&state=${this.query.state}
&page_size=${this.page.limit}&page_number=${this.page.current}`)
          .then(res => {
            if(res.status !== 200){
              layer.msg('网络异常，请稍后重试', {icon: 2, time: 1500});
              this.loading = false;
              return;
            }
            // console.log(res.data.data);
            if(res.data.status < 0){
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
        case 1:
          obj.status_name = '准备中'; break;
        case 2:
          obj.status_name = '报名中'; break;
        case 3:
          obj.status_name = '报名已截止'; break;
        case 4:
          obj.status_name = '进行中'; break;
        case 5:
          obj.status_name = '已结束';
      }
    },
    computedMemberStatusName(obj){
      if(obj.borrow === 1)
        obj.borrow_name = "需要";
      else
        obj.borrow_name = "不需要";
    },
    onQueryNameChange(){
      this.$http.post(`/member/queryStaffMembers?token=${Cookies.get('token')}&select_id=${this.actionInf.staff_user_id}`, { name: this.search_name })
          .then(res => {
            if(res.status !== 200){
              layer.msg('系统异常，请稍后重试', {icon: 2, time: 1500});
              this.loading = false;
              return;
            }
            // console.log(res.data.data);
            if(res.data.status < 0){
              this.$clear();
              this.loading = false;
              return;
            }
            this.queryUserList = res.data.data;
          })
          .catch(error => {
            layer.msg('网络异常，请稍后重试', {icon: 2, time: 1500});
            this.loading = false;
          })
    },
    onFileChange(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const image = new Image();
          image.src = e.target.result;
          image.onload = () => {
            this.decodeQRCode(image);
          };
        };
        reader.readAsDataURL(file);
      }
    },
    decodeQRCode(image) {
      this.qrcodeShow = false;
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.width = image.width;
      canvas.height = image.height;
      context.drawImage(image, 0, 0, canvas.width, canvas.height);
      const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
      const decodedResult = jsQR(imageData.data, imageData.width, imageData.height, {
        inversionAttempts: 'dontInvert',
      });
      if (decodedResult) {
        this.decodedResult = decodedResult.data;
        this.actionInf.wechat_url = decodedResult.data;
      } else {
        this.decodedResult = '';
        this.actionInf.wechat_url = '';
      }
    },
    onEditShow(id){
      this.currentIndex = id;
      this.actionInf = JSON.parse(JSON.stringify(this.dataSource[id]));
      if(this.dataSource[id].staff_user_id === 0)
        this.queryUserList = [{id: 0, name: "Unknown", student_id: "Unknown", unsigned_num: "Unknown"}];
      else
        this.onQueryNameChange();
      this.decodedResult = this.actionInf.wechat_url;
      this.qrcodeShow = 0;
      if(this.actionInf.state > 3)
        this.editActionTitle = "查看活动";
      else
        this.editActionTitle = "编辑活动";
      this.editActionShow = true;
    },
    onEditSubmit(){
      const iso8601Regex = /^(?:(?:1[6-9]|[2-9]\d)\d{2}-\d{2}-\d{2}(?:[Tt]\d{2}:\d{2}(?::\d{2}(\.\d+)?)?(Z|[\+\-]\d{2}:\d{2})?)?)$/;
      if(iso8601Regex.test(this.actionInf.open_time)){
        const date = new Date(this.actionInf.open_time);
        this.actionInf.submit_open_time = date.toLocaleDateString().replace(/\//g, '-') + ' ' + date.toLocaleTimeString();
      }
      else
        this.actionInf.submit_open_time = this.actionInf.open_time;
      if(iso8601Regex.test(this.actionInf.close_time)){
        const date = new Date(this.actionInf.close_time);
        this.actionInf.submit_close_time = date.toLocaleDateString().replace(/\//g, '-') + ' ' + date.toLocaleTimeString();
      }
      else
        this.actionInf.submit_close_time = this.actionInf.close_time;
      if(this.actionInf.name === '' || this.actionInf.place === '' || this.actionInf.time_range === '' || this.actionInf.date === ''){
        layer.msg('请填写完整的活动基本信息', {icon: 7, time: 1500});
        return;
      }
      if(this.actionInf.wechat_url === ''){
        layer.msg('请设置活动联系群', {icon: 7, time: 1500});
        return;
      }
      if(this.actionInf.staff_user_id === -1){
        layer.msg('请指定活动值班人员。', {icon: 7, time: 1500});
        return;
      }
      if(this.actionInf.open_time === '' || this.actionInf.close_time === ''){
        layer.msg('请设置签到开放和结束时间。', {icon: 7, time: 1500});
        return;
      }
      this.disabled = true;
      this.$http.post(`/action/update?token=${Cookies.get('token')}&id=${this.actionInf.id}&title=${encodeURIComponent(this.actionInf.title)}&place=${encodeURIComponent(this.actionInf.place)}
&time_range=${encodeURIComponent(this.actionInf.time_range)}&date=${encodeURIComponent(this.actionInf.date)}&max_num=${encodeURIComponent(this.actionInf.max_num)}&close_time=${encodeURIComponent(this.actionInf.submit_close_time)}
&wechat_url=${encodeURIComponent(this.actionInf.wechat_url)}&staff_user_id=${encodeURIComponent(this.actionInf.staff_user_id)}&open_time=${encodeURIComponent(this.actionInf.submit_open_time)}`)
          .then(res => {
            this.disabled = false;
            if(res.status === 200){
              if(res.data.status === -2) {
                this.$clear();
                return;
              }
              if(res.data.status === -1){
                this.disabled = false;
                this.editActionShow = false;
                layer.msg('活动已删除，请刷新后重试。',{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 0){
                this.editActionShow = false;
                layer.msg('活动已发布，不能修改基本信息。',{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 1){
                this.editActionShow = false;
                layer.msg('活动已开始或结束，不能修改活动信息。',{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 2){
                this.editActionShow = false;
                layer.msg('值班人员账号已删除，请重新指定。',{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 3){
                this.editActionShow = false;
                layer.msg('值班人员账号已变化，请重新指定。',{icon: 7, time: 1500});
                return;
              }
              this.dataSource[this.currentIndex] = JSON.parse(JSON.stringify(this.actionInf));
              this.computedStatusName(this.dataSource[this.currentIndex]);
              layer.msg('保存成功！',{icon: 1, time: 1500});
            }else{
              layer.msg('系统异常，请稍后重试',{icon: 1, time: 1500});
            }
          })
          .catch(res => {
            layer.msg('网络异常，请稍后重试', {icon: 2, time: 1500});
            this.disabled = false;
          })
    },
    onDeleteSubmit(index){
      layer.confirm(`确定删除活动“${this.dataSource[index].title}”吗？相关记录也会一并删除，且无法恢复。`,
          {
            title:"确认删除",
            icon: 3,
            btn: [
              {text:'删除', callback: (id) => {
                  this.disabled = true;
                  layer.close(id);
                  this.$http.post(`/action/deleteAction?token=${Cookies.get('token')}&action_id=${this.dataSource[index].id}`)
                      .then(res => {
                        if(res.status === 200){
                          if(res.data.status === -2) {
                            this.$clear();
                            return;
                          }
                          if(res.data.status === -1){
                            this.disabled = false;
                            this.changePasswordShow = false;
                            layer.msg('活动已删除，请刷新后重试。',{icon: 7, time: 1500});
                            return;
                          }
                          this.disabled = false;
                          layer.msg('删除成功！',{icon: 1, time: 1500});
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
              {
                text:'取消', callback: (id) => {
                  layer.close(id);
                }
              }
            ]
          }
      );
    },
    onReleaseSubmit(){
      layer.confirm(`确定发布活动“${this.actionInf.title}”吗？发布后会员可以报名，活动基本信息将不能修改。`,
          {
            title:"确认发布",
            icon: 3,
            btn: [
              {text:'发布', callback: (id) => {
                  this.onContinueReleaseAction();
                  layer.close(id);
                }
              },
              {
                text:'取消', callback: (id) => {
                  layer.close(id);
                }
              }
            ]
          }
      );
    },
    onContinueReleaseAction(){
      this.disabled = true;
      this.$http.post(`/action/releaseAction?token=${Cookies.get('token')}&action_id=${this.actionInf.id}`)
          .then(res => {
            if(res.status === 200){
              if(res.data.status === -2) {
                this.$clear();
                return;
              }
              if(res.data.status === -1){
                this.disabled = false;
                this.editActionShow = false;
                layer.msg('活动已删除，请刷新后重试。',{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 0){
                this.disabled = false;
                this.editActionShow = false;
                layer.msg('活动状态已由工作人员更改，请刷新页面。',{icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 1){
                this.disabled = false;
                this.editActionShow = false;
                layer.msg('活动已开放，请刷新后重试。',{icon: 7, time: 1500});
                return;
              }
              this.disabled = false;
              this.editActionShow = false;
              layer.msg('活动已成功发布',{icon: 1, time: 1500});
              this.queryData();
            }else{
              layer.msg('系统异常，请稍后重试',{icon: 1, time: 1500});
            }
          })
          .catch(res => {
            layer.msg('网络异常，请稍后重试', {icon: 2, time: 1500})
          });
    },
    onStopRegisterSubmit(){
      layer.confirm(`确定截止活动“${this.actionInf.title}”的报名吗？候补记录会被清除，请先核对。`,
          {
            title:"确认截止报名",
            icon: 3,
            btn: [
              {text:'截止报名', callback: (id) => {
                  this.disabled = true;
                  layer.close(id);
                  this.$http.post(`/action/stopRegisterAction?token=${Cookies.get('token')}&action_id=${this.actionInf.id}`)
                      .then(res => {
                        if(res.status === 200){
                          if(res.data.status === -2) {
                            this.$clear();
                            return;
                          }
                          if(res.data.status === -1){
                            this.disabled = false;
                            this.editActionShow = false;
                            layer.msg('活动已删除，请刷新后重试。',{icon: 7, time: 1500});
                            return;
                          }
                          if(res.data.status === 0){
                            this.disabled = false;
                            this.editActionShow = false;
                            layer.msg('活动状态已变化，请刷新后重试。',{icon: 7, time: 1500});
                            return;
                          }
                          this.disabled = false;
                          this.editActionShow = false;
                          layer.msg('已截止报名',{icon: 1, time: 1500});
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
              {
                text:'取消', callback: (id) => {
                  layer.close(id);
                }
              }
            ]
          }
      );
    },
    onStopAction(){
      layer.confirm(`确定结束活动“${this.actionInf.title}”吗？结束后工作人员将不能继续核验签到码。`,
          {
            title:"确认结束活动",
            icon: 3,
            btn: [
              {text:'结束活动', callback: (id) => {
                  this.disabled = true;
                  layer.close(id);
                  this.$http.post(`/action/stopAction?token=${Cookies.get('token')}&action_id=${this.actionInf.id}`)
                      .then(res => {
                        if(res.status === 200){
                          if(res.data.status === -2) {
                            this.$clear();
                            return;
                          }
                          if(res.data.status === -1){
                            this.disabled = false;
                            this.editActionShow = false;
                            layer.msg('活动已删除，请刷新后重试。',{icon: 7, time: 1500});
                            return;
                          }
                          if(res.data.status === 0){
                            this.disabled = false;
                            this.editActionShow = false;
                            layer.msg('活动状态已变化，请刷新后重试。',{icon: 7, time: 1500});
                            return;
                          }
                          this.disabled = false;
                          this.editActionShow = false;
                          layer.msg('活动已结束！',{icon: 1, time: 1500});
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
              {
                text:'取消', callback: (id) => {
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
.file-upload-wrapper {
  position: relative;
  overflow: hidden;
  display: inline-block;
}

.file-upload {
  position: absolute;
  font-size: 100px;
  opacity: 0;
  right: 0;
  top: 0;
}

.file-upload-label {
  background-color: dodgerblue;
  color: white;
  padding: 10px 20px;
  display: inline-block;
  cursor: pointer;
}

.file-upload-label:hover {
  background-color: black;
}

.file-upload-label-disabled {
  background-color: #e0e0e0;
  color: #a0a0a0;
  padding: 10px 20px;
  display: inline-block;
  cursor: not-allowed;
  opacity: 0.7;
}
</style>
