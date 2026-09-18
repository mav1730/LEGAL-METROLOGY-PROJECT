import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: "2rem", color: "#f4f4f8", maxWidth: 640 }}>
          <h2 style={{ color: "#ff6b00" }}>Something broke on this page</h2>
          <p>{String(this.state.error.message || this.state.error)}</p>
          <button
            type="button"
            onClick={() => {
              this.setState({ error: null });
              window.location.hash = "#scanner";
              window.location.reload();
            }}
          >
            Reload scanner
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
