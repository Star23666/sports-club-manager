// Keep the admin login puzzle enabled outside an explicit localhost demo.
export const skipPuzzleForLocalDemo = () =>
  process.env.NODE_ENV === 'development' &&
  process.env.VUE_APP_LOCAL_DEMO_NO_PUZZLE === 'true' &&
  ['localhost', '127.0.0.1'].includes(window.location.hostname);
