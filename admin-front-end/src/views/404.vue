<template>
  <lay-exception status="404" title="404" describe="Page Not Found" style="margin-top: 30vh">
    <template #extra>
      <lay-button @click="onBackClick">Back</lay-button>
      <lay-button type="primary" @click="onInboxClick">Go to Inbox</lay-button>
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
