<template>
  <lay-exception status="404" title="404" describe="页面不存在" style="margin-top: 30vh">
    <template #extra>
      <lay-button @click="onBackClick">返回</lay-button>
      <lay-button type="primary" @click="onInboxClick">返回首页</lay-button>
    </template>
  </lay-exception>
</template>

<script>

export default {
  methods:{
    onBackClick(){
      this.$router.go(-1);
    },
    onInboxClick(){
      this.$router.push('/');
    }
  }
}
</script>
