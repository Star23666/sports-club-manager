// A deliberate local-only escape hatch for demo accounts. Production builds
// retain the puzzle even if the environment variable is accidentally set.
export const skipPuzzleForLocalDemo = () =>
  process.env.NODE_ENV === 'development' &&
  process.env.VUE_APP_LOCAL_DEMO_NO_PUZZLE === 'true' &&
  ['localhost', '127.0.0.1'].includes(window.location.hostname);
