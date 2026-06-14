import React from 'react';
export class ErrorBoundary extends React.Component<React.PropsWithChildren, {error: boolean}> {
  state = { error: false };
  static getDerivedStateFromError(): {error: boolean} { return { error: true }; }
  render(): React.ReactNode { return this.state.error ? <main><h1>Unable to display this page</h1><p>The API response could not be validated. Please try again.</p></main> : this.props.children; }
}
