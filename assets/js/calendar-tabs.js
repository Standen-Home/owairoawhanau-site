const calendarTabsRoot = document.querySelector("[data-calendar-tabs]");

if (calendarTabsRoot) {
  const buttons = Array.from(
    calendarTabsRoot.querySelectorAll("[data-calendar-tab-button]")
  );
  const panels = Array.from(
    calendarTabsRoot.querySelectorAll("[data-calendar-panel]")
  );

  const setActiveTab = (name) => {
    buttons.forEach((button) => {
      const isActive = button.dataset.calendarTabButton === name;
      button.classList.toggle("btn-primary", isActive);
      button.setAttribute("aria-pressed", isActive ? "true" : "false");
    });

    panels.forEach((panel) => {
      panel.hidden = panel.dataset.calendarPanel !== name;
    });
  };

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      setActiveTab(button.dataset.calendarTabButton);
    });
  });

  setActiveTab("list");
}
