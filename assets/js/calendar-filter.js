const root = document.querySelector("[data-calendar-filters]");

if (root) {
  const searchInput = root.querySelector("[data-calendar-search]");
  const monthSelect = root.querySelector("[data-calendar-month]");
  const locationSelect = root.querySelector("[data-calendar-location]");
  const events = Array.from(document.querySelectorAll("[data-calendar-event]"));
  const results = document.querySelector("[data-calendar-results]");
  const emptyState = document.querySelector("[data-calendar-empty]");

  const applyFilters = () => {
    const searchTerm = searchInput.value.trim().toLowerCase();
    const monthValue = monthSelect.value;
    const locationValue = locationSelect.value;

    let visibleCount = 0;

    events.forEach((eventNode) => {
      const matchesSearch = !searchTerm || eventNode.dataset.search.includes(searchTerm);
      const matchesMonth = !monthValue || eventNode.dataset.month === monthValue;
      const matchesLocation = !locationValue || eventNode.dataset.location === locationValue;
      const visible = matchesSearch && matchesMonth && matchesLocation;

      eventNode.hidden = !visible;
      if (visible) {
        visibleCount += 1;
      }
    });

    if (results) {
      results.textContent = visibleCount === 1 ? "1 upcoming event" : `${visibleCount} upcoming events`;
    }

    if (emptyState) {
      emptyState.hidden = visibleCount !== 0;
    }
  };

  [searchInput, monthSelect, locationSelect].forEach((control) => {
    control.addEventListener("input", applyFilters);
    control.addEventListener("change", applyFilters);
  });

  applyFilters();
}
