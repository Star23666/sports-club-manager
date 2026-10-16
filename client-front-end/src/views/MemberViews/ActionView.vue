<template>
  <van-toast v-model:show="loading" type="loading" overlay="true" duration="0"
             forbid_click="true" message="加载中..."></van-toast>
  <Vcode :show="isShow"
         slider-text="拖动滑块完成验证"
         fail-text="验证失败，请重试"
         success-text="验证通过"
         :range="5"
         @success="onSubmit"
         @close="close"
  />
  <van-pull-refresh
      pulling-text="下拉刷新"
      loosing-text="松开刷新"
      loading-text="加载中..."
      success-text="刷新成功"
      v-model="isLoading"
      @refresh="onRefresh"
  >
    <div v-if="actionList.length === 0">
      <van-empty description="暂无可报名活动" />
    </div>
    <van-row justify="center">
      <div v-for="item in actionList">
        <van-cell-group inset style="width: 360px; max-width: calc(100vw - 32px); box-sizing: border-box">
          <van-cell :title="item.title"/>
          <van-cell title="地点">{{item.place}}</van-cell>
          <van-cell title="日期">{{item.date}}</van-cell>
          <van-cell title="时间">{{item.time_range}}</van-cell>
          <van-cell title="人数上限">{{item.max_num}} 人</van-cell>
          <van-cell title="借用球拍">
            <template #right-icon>
              <van-switch v-model="borrow">
              </van-switch>
            </template>
          </van-cell>
          <van-cell>
            <van-button @click="onClick(item.id)" :disabled="buttonDisabled" type="primary" size="small" icon="plus">报名参加</van-button>
          </van-cell>
        </van-cell-group>
        <br/>
      </div>
    </van-row>
    <br/>
    <br/>
  </van-pull-refresh>
</template>

<script>
import Cookies from "js-cookie";
import {showFailToast, showSuccessToast} from "vant";
import { showConfirmDialog } from 'vant';

export default {
  created(){
    this.$memberVerify();
    this.loading = true;
    this.onRefresh();
  },
  data(){
    return{
      borrow: false,
      isLoading: false,
      isShow: false,
      buttonDisabled: false,
      loading: false,
      currentId: -1,
      actionList: []
    };
  },
  methods: {
    onRefresh() {
      this.isLoading = true;
      this.$http.post('/action/queryAction?token='+Cookies.get('token'))
          .then(response => {
            this.loading = false;
            this.isLoading = false;
            if(response.status === 200 && response.data.status === 1)
              this.actionList = response.data.data;
          })
          .catch(error =>{
            console.log(error);
          });
    },
    onClick(id) {
      this.currentId = id;
      this.isShow = true;
    },
    close(){
      this.isShow = false;
    },
    onSubmit(){
      this.loading = true;
      this.isShow = false;
      this.buttonDisabled = true;
      this.$http.post('/action/attendAction?token='+Cookies.get('token')
                          +`&action_id=${this.currentId}&borrow=${this.borrow}`)
          .then(response => {
            this.loading = false;
            if(response.status !== 200){
              showFailToast("系统异常，请稍后重试");
              this.buttonDisabled = false;
            }
            if(response.data.status === -2){
              this.$memberVerify();
            }
            if(response.data.status < 0){
              showFailToast("当前账号暂不能直接报名活动");
              this.buttonDisabled = false;
            }
            if(response.data.status === 0){
              showFailToast("活动已停止报名，请刷新页面");
              this.buttonDisabled = false;
            }
            else if(response.data.status === 1){
              showFailToast("你已报名或进入候补名单，不能重复报名");
              this.buttonDisabled = false;
            }
            else if(response.data.status === 2){
              showConfirmDialog({
                message:
                    '活动名额已满，是否加入候补？报名期间有人取消时将按候补顺序递补；报名截止后未递补的候补记录会被清除。你可以在“我的报名”中查看结果。',
                confirmButtonText: '加入候补',
                cancelButtonText: '取消'
              })
                  .then(() => {
                    this.addToWaitList();
                  })
                  .catch(() => {
                    this.buttonDisabled = false;
                  });
            }
            else if(response.data.status === 3){
              showSuccessToast('报名成功，请到“我的报名”查看并按时参加');
              this.buttonDisabled = false;
            }
          })
          .catch(error =>{
            console.log(error);
            showFailToast("网络异常，请稍后重试");
            this.buttonDisabled = false;
          });
      //alert("报名活动：" + this.currentId);
    },
    addToWaitList(){
      this.loading = true;
      this.$http.post('/waiting/waitCreate?token='+Cookies.get('token')
          +`&action_id=${this.currentId}&borrow=${this.borrow}`)
          .then(response => {
            this.loading = false;
            if(response.status !== 200){
              showFailToast("系统异常，请稍后重试");
              this.buttonDisabled = false;
            }
            if(response.data.status < 0){
              showFailToast("当前账号不能加入候补");
              this.buttonDisabled = false;
            }
            if(response.data.status === 0){
              showFailToast("该活动不能候补，请刷新页面");
              this.buttonDisabled = false;
            }
            if(response.data.status === 1){
              showFailToast("活动已有空位，请刷新页面直接报名");
              this.buttonDisabled = false;
            }
            if(response.data.status === 2){
              showFailToast("不能重复参加此活动");
              this.buttonDisabled = false;
            }
            if(response.data.status === 3){
              showSuccessToast('已加入候补，请到“转让与候补”查看');
              this.buttonDisabled = false;
            }
          })
          .catch(error =>{
            console.log(error);
            showFailToast("网络异常，请稍后重试");
            this.buttonDisabled = false;
          });
    }
  }
}
</script>
