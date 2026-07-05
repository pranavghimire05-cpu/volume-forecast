function renderSidebar(activePage) {
  const items = [
    { key: "dashboard", href: "#", icon: "🏠", label: "Dashboard", disabled: true },
    { key: "volume", href: "volume-upload.html", icon: "➕", label: "Volume Upload" },
    { key: "performance-upload", href: "performance-upload.html", icon: "➕", label: "Performance Upload" },
    { key: "training", href: "model-training.html", icon: "✨", label: "Model Training" },
    { key: "predictions", href: "predictions.html", icon: "📈", label: "Predictions" },
    { key: "agent", href: "performance-agent.html", icon: "🗂️", label: "Performance Agent" },
  ];

  const navHtml = items
    .map((it) => {
      const cls = it.key === activePage ? "active" : "";
      const disabledAttr = it.disabled ? ' style="opacity:0.45;cursor:default;pointer-events:none;"' : "";
      return `<a href="${it.href}" class="${cls}"${disabledAttr}><span class="ic">${it.icon}</span>${it.label}</a>`;
    })
    .join("");

  return `
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-icon">📶</div>
        <div class="brand-text">
          <strong>Bandwidth AI</strong>
          <span>Workforce Intelligence</span>
        </div>
      </div>
      <nav class="nav">${navHtml}</nav>
      <div class="sidebar-footer">
        <div class="dot-row"><span class="dot"></span>System Online</div>
        <div class="sub">All services operational</div>
      </div>
    </aside>
  `;
}

function mountSidebar(activePage) {
  document.getElementById("sidebar-mount").outerHTML = renderSidebar(activePage);
}
