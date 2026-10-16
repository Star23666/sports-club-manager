<template>
  <lay-container>
    <lay-panel style="width: 750pt; margin-top: max(calc(50vh - 280pt), 20px);">
        <h2 style="text-align: center; margin-bottom: 25px">Create an Action</h2>
      <lay-form :model="actionInf" required style="width: 500px; margin-left: calc(375pt - 300px)">
        <lay-form-item label="Name" style="margin-top: 15pt">
          <lay-input v-model="actionInf.name"></lay-input>
        </lay-form-item>
        <lay-form-item label="Location">
          <lay-input v-model="actionInf.place"></lay-input>
        </lay-form-item>
        <lay-form-item label="Date">
          <lay-input v-model="actionInf.date"></lay-input>
        </lay-form-item>
        <lay-form-item label="Time">
          <lay-input v-model="actionInf.time_range"></lay-input>
        </lay-form-item>
        <lay-form-item label="Maximum">
          <lay-input-number v-model="actionInf.max_num" min="1" max="40"></lay-input-number>
        </lay-form-item>
        <lay-form-item label="Duty Stuff">
          <lay-select v-model="actionInf.staff_user_id" placeholder="Select..." style="width: 210pt">
            <template #header>
              <div style="padding: 10px">
                <lay-input placeholder="Name" prefix-icon="layui-icon-search" v-model="search_name" @input="onQueryNameChange"></lay-input>
              </div>
            </template>
            <lay-select-option v-if="actionInf.staff_user_id === -1" :value="-1" label="Select"></lay-select-option>
            <lay-select-option v-for="item in queryUserList" :value="item.id">{{item.name}}({{item.student_id}}, {{item.unsigned_num}} on Duty)</lay-select-option>
            <template #footer>
              <center v-if="queryUserList.length >= 5" style="font-size: 8pt">Display up to 5 records, please search for rest.</center>
            </template>
          </lay-select>
        </lay-form-item>
        <lay-form-item label="Wechat Group">
          <div class="file-upload-wrapper">
            <input type="file" id="file-upload" class="file-upload" @change="onFileChange" accept="image/*"/>
            <label for="file-upload" class="file-upload-label"><lay-icon type="layui-icon-link"/> Upload QR Code</label>
          </div>
          &nbsp;&nbsp;<p style="font-size: 9pt; color: gray; margin-left: 130pt; margin-top: -18pt">*with automatic recognition</p>
          <div v-if="decodedResult">
            <div v-if="decodedResult !== '未識別到信息'" style="font-size: 10pt; margin-top: 8pt">QR Code is Uploaded:
              <lay-button v-if="!qrcodeShow" size="xs" type="primary" @click="this.qrcodeShow = 1" prefix-icon="layui-icon-show">Preview</lay-button>
              <lay-button v-else size="xs" type="danger" @click="this.qrcodeShow = 0" prefix-icon="layui-icon-reduce-circle" >Hide</lay-button>
              <br/>
              <lay-qrcode v-show="qrcodeShow" :text="actionInf.wechat_url"></lay-qrcode>
            </div>
            <div v-else style="font-size: 10pt; margin-top: 5pt">The QR code does not exist or is not recognized!</div>
          </div>
        </lay-form-item>
        <lay-form-item label="Start Time">
          <lay-date-picker type="datetime" v-model="actionInf.open_time" placeholder="Allowable-Verification Time" readonly allowClear></lay-date-picker>
        </lay-form-item>
        <lay-form-item label="Closed Time">
          <lay-date-picker type="datetime" v-model="actionInf.close_time" placeholder="Allowable-Terminate Time" readonly allowClear></lay-date-picker>
        </lay-form-item>
        <div style="text-align: right; margin-top: 4px; margin-right: -18px">
          <lay-button @click="onReset"><lay-icon type="layui-icon-refresh-one"/> Re-Enter</lay-button>&nbsp;
          <lay-button type="primary" style="margin-right: 20px" @click="onSubmit" :disabled="disabled"><lay-icon type="layui-icon-add-circle-fine"/> Create</lay-button>
        </div>
      </lay-form>
    </lay-panel>

  </lay-container>
</template>

<script>
import jsQR from 'jsqr';
import Cookies from "js-cookie";
import {layer} from "@layui/layui-vue";

  export default {
    created() {
      this.onQueryNameChange();
    },
    data() {
      return {
        actionInf: {
          name: '',
          place: '',
          date: '',
          time_range: '',
          max_num: 4,
          wechat_url: '',
          staff_user_id: -1,
          open_time: '',
          close_time: ''
        },
        decodedResult: '',
        search_name: '',
        disabled: false,
        qrcodeShow: 0,
        queryUserList: []
      };
    },
    methods: {
      onQueryNameChange(){
        this.$http.post(`/member/queryStaffMembers?token=${Cookies.get('token')}&select_id=${this.actionInf.staff_user_id}`, { name: this.search_name })
            .then(res => {
              if(res.status !== 200){
                layer.msg('System Error', {icon: 2, time: 1500});
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
              layer.msg('Internet Error!', {icon: 2, time: 1500});
              this.loading = false;
            })
      },
      onReset(){
        this.actionInf.staff_user_id = -1;
        this.actionInf.open_time = '';
        this.actionInf.close_time = '';
        this.actionInf.name = '';
        this.actionInf.place = '';
        this.actionInf.time_range = '';
        this.actionInf.max_num = 4;
        this.actionInf.date = '';
        this.decodedResult = '';
        this.actionInf.wechat_url = '';
      },
      onSubmit(){
        if(this.actionInf.name === '' || this.actionInf.place === '' || this.actionInf.time_range === '' || this.actionInf.date === ''){
          layer.msg('Action information needs to be filled out completely', {icon: 7, time: 1500});
          return;
        }
        if(this.actionInf.wechat_url === ''){
          layer.msg('Please set up an wechat contact group', {icon: 7, time: 1500});
          return;
        }
        if(this.actionInf.staff_user_id === -1){
          layer.msg('Please designate a duty stuff for the action.', {icon: 7, time: 1500});
          return;
        }
        if(this.actionInf.open_time === '' || this.actionInf.close_time === ''){
          layer.msg('You need to specify the open and closed times.', {icon: 7, time: 1500});
          return;
        }
        this.disabled = true;
        this.$http.post(`/action/create?token=${Cookies.get('token')}&title=${encodeURIComponent(this.actionInf.name)}&place=${encodeURIComponent(this.actionInf.place)}
&time_range=${encodeURIComponent(this.actionInf.time_range)}&date=${encodeURIComponent(this.actionInf.date)}&max_num=${encodeURIComponent(this.actionInf.max_num)}&close_time=${encodeURIComponent(this.actionInf.close_time)}
&wechat_url=${encodeURIComponent(this.actionInf.wechat_url)}&staff_user_id=${encodeURIComponent(this.actionInf.staff_user_id)}&open_time=${encodeURIComponent(this.actionInf.open_time)}`)
            .then(res =>{
              if(res.status !== 200){
                this.disabled = false;
                layer.msg("System Error", {icon: 2, time: 1500});
                return;
              }
              if(res.data.status === -2)
                this.$clear();
              if(res.data.status === -1){
                this.disabled = false;
                layer.msg("The current Duty Stuff account has been deleted, please reassign it and try again.", {icon: 7, time: 1500});
                return;
              }
              if(res.data.status === 0){
                this.disabled = false;
                layer.msg("The current Duty Stuff account has been de-authorized, please reassign it and try again.", {icon: 7, time: 1500});
                return;
              }
              layer.msg("Successful Creation Action", {icon: 1, time: 1500});
              this.$router.push({path:'/main/action'});
            })
            .catch(res =>{
              this.disabled = false;
              layer.msg("Internet Error", {icon: 2, time: 1500});
            })
        this.disabled = true;
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
          this.decodedResult = '未識別到信息';
          this.actionInf.wechat_url = '';
        }
      },
    }
  };
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
</style>
