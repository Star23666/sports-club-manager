<template>
  <van-toast v-model:show="loading" type="loading" overlay="true" duration="0"
             forbid_click="true" message="加載中..."></van-toast>
  <div>
    <QrScanner v-if="showQrCodeReader" @decode="onDecodeHandler" @close="qrReaderClose" />
  </div>
  <van-nav-bar
      title="签到核验"
      left-text="返回"
      left-arrow
      fixed
      @click-left="onClickLeft"
      placeholder
  />

  <van-cell-group v-if="!sign_code" inset class="scan-entry">
    <van-cell title="为会员签到" label="可扫描二维码；本机没有摄像头时，输入二维码下方的签到码。" />
    <van-field
        v-model.trim="manualCode"
        label="签到码"
        placeholder="输入会员的签到码"
        maxlength="100"
        clearable
        @keyup.enter="submitManualCode"
    />
    <div class="scan-entry-actions">
      <van-button icon="scan" plain type="primary" @click="startScan">扫码（需摄像头）</van-button>
      <van-button type="primary" @click="submitManualCode">查询签到码</van-button>
    </div>
  </van-cell-group>

  <van-notice-bar left-icon="volume-o" color="#1989fa" background="#ecf9ff" v-if="sign_code && !show_sign && !isLoading"
                  style="position: fixed; z-index: 1000; width: 100%">
    <van-swipe
        vertical
        class="notice-swipe"
        :autoplay="16000"
        :touchable="false"
        :show-indicators="false"
        ref="swipe"
    >
      <van-swipe-item>{{ notice_messgae }}。此结果仅用于核验记录。</van-swipe-item>
      <van-swipe-item v-if="!this.show_sign && !this.signed">如有特殊情况无法签到，可将此页面截图交给管理员处理补签。</van-swipe-item>
    </van-swipe>
  </van-notice-bar>

  <br v-if="sign_code && !show_sign && !isLoading"/>
  <br v-if="sign_code && !show_sign && !isLoading"/>
  <div v-if="sign_code && isLoading">
    <van-empty image="search" description="查询中..." />
  </div>
  <br/>
  <div v-if="sign_code && !isLoading">
    <van-cell-group inset>
      <van-row justify="center" style="margin: 0px 0px 0px 0px;">
        <h4>{{actionInf.title}}&nbsp;</h4>
      </van-row>
      <van-row justify="center" style="margin: -22px 0px 0px 0px; font-size: 10pt; color: gray">
        <vue-qrcode :value="sign_code" :width="180"/>
      </van-row>
      <van-row justify="center" style="margin: 0px 0px 20px 0px; font-size: 8pt; font-weight: bold; color: gray">
        {{sign_code}}
      </van-row>
      <van-cell title="地点">{{actionInf.place}}</van-cell>
      <van-cell title="日期">{{actionInf.date}}</van-cell>
      <van-cell title="时间">{{actionInf.time_range}}</van-cell>
      <van-cell title="球拍">{{borrow ? '需要借用' : '无需借用'}}</van-cell>
      <van-cell title="签到状态" v-if="!this.show_sign">{{signed ? '已签到' : '未签到'}}</van-cell>
      <van-cell v-if="!this.show_sign && !this.signed"></van-cell>
    </van-cell-group>
    <br/>
    <van-cell-group inset>
      <van-cell title="参加者信息"/>
      <van-cell title="姓名">{{memInf.name}}</van-cell>
      <van-cell title="学号">{{memInf.student_id}}</van-cell>
      <van-cell title="手机号">{{memInf.phone}}</van-cell>
      <van-cell title="邮箱" v-if="memInf.email !== ''">{{memInf.email}}</van-cell>
      <van-cell title="微信号">{{memInf.wechat_id}}</van-cell>
    </van-cell-group>
    <van-submit-bar
        v-if="show_sign"
        tip="请仔细核对参加者信息，确认无误后完成签到。"
        tip-icon="info-o"
        placeholder>
      <template #button>
        <van-button icon="sign" round type="warning" @click="onSignClick">确认签到</van-button>
      </template>
    </van-submit-bar>
  </div>
  <br/>
</template>

<script>
import QrScanner from '@/components/QrScanner';
import VueQrcode from 'vue-qrcode';
import Cookies from "js-cookie";
import {showFailToast, showSuccessToast, showToast, showDialog} from "vant";

export default {
  data(){
    return {
      isLoading: false,
      showQrCodeReader: false,
      sign_code: '',
      manualCode: '',
      notice_messgae: '',
      memInf: {
        name: '加载中...',
        username: '加载中...',
        student_id: '加载中...',
        phone: '加载中...',
        email: '加载中...',
        wechat_id: '加载中...',
        state: 3
      },
      borrow: false,
      signed: false,
      loading: false,
      actionInf: {
        title: '加载中...',
        place:'加载中...',
        date: '加载中...',
        time_range: '加载中...'
      },
      show_sign: false
    };
  },
  components:{
    VueQrcode,
    QrScanner
  },
  created() {
    this.$staffVerify();
  },
  methods:{
    startScan(){
      this.showQrCodeReader = true;
    },
    submitManualCode(){
      if (!this.manualCode) {
        showFailToast("请先输入签到码");
        return;
      }
      this.onDecodeHandler(this.manualCode);
    },
    qrReaderClose(){
      this.showQrCodeReader = false;
    },
    resetLookup(){
      this.sign_code = '';
      this.isLoading = false;
    },
    onDecodeHandler(data){
      this.sign_code = String(data || '').trim();
      this.showQrCodeReader = false;
      if (!this.sign_code) {
        showFailToast("请先输入签到码");
        return;
      }
      this.isLoading = true;
      this.$http.post(`/staff/querySign?token=${Cookies.get('token')}`, { sign_code: this.sign_code })
          .then(response => {
            if(response.status !== 200){
              this.resetLookup();
              showFailToast("系统异常，请稍后重试");
              return;
            }
            if(response.data.status < 0) {
              this.$staffVerify();
              return;
            }
            if(response.data.status === 0){
              this.resetLookup();
              showFailToast("签到码无效");
              return;
            }
            if(response.data.status === 2){
              this.resetLookup();
              showFailToast("你不是该活动的负责工作人员");
              return;
            }
            else{
              this.actionInf = response.data.data.act_inf;
              this.memInf = response.data.data.mem_inf;
              this.borrow = response.data.data.borrow;
              this.signed = response.data.data.signed;
              if(response.data.status === 1){
                this.notice_messgae = "该记录已签到";
                showDialog({
                  message: '该记录已签到，此结果仅用于核验记录。',
                  confirmButtonText: '知道了'
                }).then(() => {
                  // on close
                });
              }
              if(response.data.status === 3){
                this.notice_messgae = "活动尚未开放签到";
                showDialog({
                  message: '该活动尚未开放签到，此结果仅用于核验记录。',
                  confirmButtonText: '知道了'
                }).then(() => {
                  // on close
                });
              }
              if(response.data.status === 4){
                this.notice_messgae = "活动已结束，不能签到";
                showDialog({
                  message: '该活动已结束，不能签到；此结果仅用于核验记录。',
                  confirmButtonText: '知道了'
                }).then(() => {
                  // on close
                });
              }
              if(response.data.status === 5){
                this.show_sign = true;
                showToast("请核对参加者信息后再签到");
              }
              this.isLoading = false;
            }
          })
          .catch(error =>{
            console.log(error);
            this.resetLookup();
            showFailToast("网络异常，请稍后重试");
          });
    },
    onClickLeft(){
      this.$router.push({path:'/staff'});
    },
    onSignClick(){
      this.loading = true;
      this.$http.post(`/staff/finishSign?token=${Cookies.get('token')}`, { sign_code: this.sign_code })
          .then(response => {
            this.loading = false;
            if(response.status !== 200){
              this.$router.push({path:'/staff'});
              showFailToast("系统异常，请稍后重试");
            }
            if(response.data.status < 0)
              this.$staffVerify();
            if(response.data.status === 0){
              this.$router.push({path:'/staff'});
              showFailToast("签到信息无效");
            }
            if(response.data.status === 1){
              this.$router.push({path:'/staff'});
              showFailToast("该记录已签到");
            }
            if(response.data.status === 2){
              this.$router.push({path:'/staff'});
              showFailToast("该记录不属于你负责的活动");
            }
            if(response.data.status === 3){
              this.$router.push({path:'/staff'});
              showFailToast("活动尚未开放签到");
            }
            if(response.data.status === 4){
              this.$router.push({path:'/staff'});
              showFailToast("活动已结束，不能签到");
            }
            if(response.data.status === 5){
              this.$router.push({path:'/staff'});
              showSuccessToast("签到成功");
            }
          })
          .catch(error => {
            this.loading = false;
            console.log(error);
            this.$router.push({path:'/staff'});
            showFailToast("网络异常，请稍后重试");
          });
    }
  }
};
</script>
<style scoped>
.notice-swipe {
  height: 40px;
  line-height: 40px;
}
.scan-entry {
  margin-top: 20px;
}
.scan-entry-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 12px 16px 16px;
}
.scan-entry-actions .van-button {
  flex: 1 1 130px;
}
</style>


